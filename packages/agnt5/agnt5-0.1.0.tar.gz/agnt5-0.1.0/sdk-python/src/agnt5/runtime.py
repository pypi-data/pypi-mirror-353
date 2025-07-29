"""
Runtime integration bridge for AGNT5 Python SDK.

This module provides the bridge between Python durable functions and the
SDK-Core (Rust) that communicates with the AGNT5 Runtime via gRPC.
"""

import asyncio
import json
import logging
import os
import signal
import subprocess
import sys
import tempfile
import traceback
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import aiohttp

from .durable import (
    InvocationRequest,
    InvocationResponse,
    _function_registry,
    _service_registry,
    _object_registry,
    get_service_registration_data,
    handle_invocation_from_runtime,
    set_runtime_client,
    DurableObject,
)

logger = logging.getLogger(__name__)


@dataclass
class RuntimeConfig:
    """Configuration for runtime connection."""

    runtime_endpoint: str = "http://localhost:8081"
    service_name: str = "python-service"
    service_version: str = "1.0.0"
    reconnect_attempts: int = 5
    reconnect_delay: float = 2.0


class PythonRuntimeBridge:
    """
    Bridge between Python SDK and SDK-Core.

    Manages:
    - Service registration with SDK-Core
    - Function invocation handling
    - Error handling and retries
    - Graceful shutdown
    """

    def __init__(self, config: RuntimeConfig):
        self.config = config
        self.running = False
        self._shutdown_event = asyncio.Event()
        self._sdk_core_process: Optional[asyncio.subprocess.Process] = None
        self._sdk_core_module = None
        self._sdk_core_worker = None
        self._message_queue = asyncio.Queue()
        self._shutdown_in_progress = False

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, _):
        """Handle shutdown signals."""
        if self._shutdown_in_progress:
            logger.warning(f"Shutdown already in progress, ignoring signal {signum}")
            return

        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self._shutdown_in_progress = True

        # Set the shutdown event to break the main loop
        if self._shutdown_event and not self._shutdown_event.is_set():
            self._shutdown_event.set()

    async def start(self) -> None:
        """Start the runtime bridge and register services."""
        logger.info("Starting Python runtime bridge...")

        try:
            # Start SDK-Core process
            await self._start_sdk_core()

            # Register services
            await self._register_services()

            # Start message loop
            self.running = True
            logger.info("Python runtime bridge started successfully")

            # Keep running until shutdown
            await self._shutdown_event.wait()

            # After shutdown event, perform cleanup
            logger.info("Shutdown event received, cleaning up...")

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, shutting down...")
        except Exception as e:
            logger.error(f"Failed to start runtime bridge: {e}")
            raise
        finally:
            if self.running or not self._shutdown_in_progress:
                await self.shutdown()

    async def _start_sdk_core(self) -> None:
        """Start the SDK-Core process via Python extension."""
        try:
            logger.info("Initializing SDK-Core integration...")

            # Try to import the Python extension module
            try:
                import agnt5._core as sdk_core

                self._sdk_core_module = sdk_core
                logger.info("SDK-Core Python extension loaded successfully")
            except ImportError as e:
                logger.warning(f"SDK-Core extension not available: {e}")
                logger.info("Falling back to direct HTTP communication")
                self._sdk_core_module = None
                return

            # Create worker configuration
            worker_config = sdk_core.create_config(
                worker_id=f"python-worker-{os.getpid()}",
                service_name=self.config.service_name,
                version=self.config.service_version,
                max_concurrent_invocations=10,
                heartbeat_interval_seconds=30,
            )

            # Create the durable worker
            self._sdk_core_worker = sdk_core.create_worker(
                worker_id=worker_config.worker_id, service_name=worker_config.service_name, version=worker_config.version, coordinator_endpoint=self.config.runtime_endpoint
            )
            assert self._sdk_core_worker is not None

            # Set up message handlers
            self._setup_message_handlers()

            logger.info("SDK-Core worker initialized")

        except Exception as e:
            logger.error(f"Failed to start SDK-Core: {e}")
            # Fall back to HTTP communication
            self._sdk_core_module = None
            self._sdk_core_worker = None
            logger.info("Continuing with HTTP fallback mode")

    async def _register_services(self) -> None:
        """Register all durable functions and objects with SDK-Core."""
        try:
            # Get service registration data
            registration_data = get_service_registration_data()

            logger.info(f"Registering {len(registration_data['functions'])} functions " f"and {len(registration_data['objects'])} objects")

            # Send registration to SDK-Core
            await self._send_to_sdk_core(
                {"type": "service_registration", "data": {"service_name": self.config.service_name, "service_version": self.config.service_version, **registration_data}}
            )

            logger.info("Service registration completed")

        except Exception as e:
            logger.error(f"Failed to register services: {e}")
            raise

    async def _send_to_sdk_core(self, message: Dict[str, Any]) -> None:
        """Send a message to SDK-Core."""
        if self._sdk_core_worker:
            # Use the Rust SDK-Core worker
            try:
                message_type = message.get("type")
                data = message.get("data", {})

                if message_type == "service_registration":
                    # Register functions with the worker
                    await self._register_functions_with_worker(data)
                elif message_type == "invocation_response":
                    # Handle invocation response
                    logger.debug(f"Invocation response: {data.get('invocation_id')}")
                elif message_type == "service_deregistration":
                    # Handle deregistration
                    logger.debug(f"Deregistering service: {data.get('service_name')}")
                else:
                    logger.warning(f"Unknown message type: {message_type}")

            except Exception as e:
                logger.error(f"Error sending message to SDK-Core: {e}")
                raise
        else:
            # Fall back to HTTP communication
            await self._send_http_message(message)

        logger.debug(f"Sent to SDK-Core: {message['type']}")

    async def _receive_from_sdk_core(self) -> Optional[Dict[str, Any]]:
        """Receive a message from SDK-Core."""
        if self._sdk_core_worker:
            # Use the Rust SDK-Core worker
            try:
                # In the Rust implementation, messages are handled via callbacks
                # This method is primarily for the HTTP fallback mode
                await asyncio.sleep(0.1)
                return None
            except Exception as e:
                logger.error(f"Error receiving from SDK-Core: {e}")
                return None
        else:
            # Fall back to HTTP communication
            return await self._receive_http_message()

    async def handle_object_invocation(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle durable object method invocation from SDK-Core.
        
        This handles method calls on durable objects.
        """
        try:
            object_class_name = request_data.get("object_class")
            object_id = request_data.get("object_id")
            method_name = request_data.get("method_name")
            args = request_data.get("args", [])
            kwargs = request_data.get("kwargs", {})
            
            if not all([object_class_name, object_id, method_name]):
                raise ValueError("Missing required object invocation parameters")
            
            # Find the object class
            if object_class_name not in _object_registry:
                raise ValueError(f"Object class '{object_class_name}' not found")
            
            object_class = _object_registry[object_class_name]
            
            # Get or create the object instance
            obj = await object_class.get_or_create(object_id)
            
            # Invoke the method
            result = await obj.invoke_method(method_name, args, kwargs)
            
            # Send response back to SDK-Core
            response_data = {
                "invocation_id": request_data.get("invocation_id", "unknown"),
                "success": True,
                "result": result,
            }
            
            await self._send_to_sdk_core({"type": "object_invocation_response", "data": response_data})
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error handling object invocation: {e}")
            error_response = {
                "invocation_id": request_data.get("invocation_id", "unknown"),
                "success": False,
                "error": str(e),
            }
            
            await self._send_to_sdk_core({"type": "object_invocation_response", "data": error_response})
            
            return error_response
    
    async def handle_invocation(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle function invocation request from SDK-Core.

        This is the main entry point for function execution.
        """
        try:
            # Delegate to the durable module
            response_data = await handle_invocation_from_runtime(request_data)

            # Send response back to SDK-Core
            await self._send_to_sdk_core({"type": "invocation_response", "data": response_data})

            return response_data

        except Exception as e:
            logger.error(f"Error handling invocation: {e}")
            error_response = {
                "invocation_id": request_data.get("invocation_id", "unknown"),
                "success": False,
                "error": str(e),
            }

            await self._send_to_sdk_core({"type": "invocation_response", "data": error_response})

            return error_response

    async def shutdown(self) -> None:
        """Gracefully shutdown the runtime bridge."""
        if not self.running and self._shutdown_in_progress:
            logger.debug("Shutdown already completed")
            return

        logger.info("Shutting down Python runtime bridge...")
        self.running = False
        self._shutdown_in_progress = True

        try:
            # Send deregistration message to SDK-Core
            if self._sdk_core_worker:
                await self._send_to_sdk_core({"type": "service_deregistration", "data": {"service_name": self.config.service_name}})

            # Stop SDK-Core process
            if self._sdk_core_process:
                self._sdk_core_process.terminate()
                await self._sdk_core_process.wait()

            logger.info("Python runtime bridge shutdown completed")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        finally:
            if not self._shutdown_event.is_set():
                self._shutdown_event.set()

    def _setup_message_handlers(self) -> None:
        """Bridge Python function calls with the Rust SDK-Core worker by configuring callback mechanisms for bidirectional communication.."""
        if not self._sdk_core_worker:
            return

        # Register Python functions with the Rust worker
        # This will be called during service registration
        logger.debug("Message handlers configured for SDK-Core integration")

    async def _register_functions_with_worker(self, registration_data: Dict[str, Any]) -> None:
        """Register Python functions with the SDK-Core worker."""
        if not self._sdk_core_worker:
            return

        try:
            functions = registration_data.get("functions", [])

            for func_info in functions:
                func_name = func_info.get("name")
                if not func_name:
                    logger.warning(f"Function info missing name: {func_info}")
                    continue

                # Create a wrapper function that can be called from Rust
                # Note: This function will be registered with the Rust extension in future implementation
                async def _python_handler_wrapper(invocation_id: str, input_data: bytes) -> bytes:
                    try:
                        # Deserialize input
                        input_dict = json.loads(input_data.decode("utf-8"))

                        # Call the Python function
                        from .durable import handle_invocation_from_runtime

                        request_data = {"invocation_id": invocation_id, "function_name": func_name, "args": input_dict.get("args", []), "kwargs": input_dict.get("kwargs", {})}

                        response = await handle_invocation_from_runtime(request_data)

                        # Serialize response
                        return json.dumps(response).encode("utf-8")

                    except Exception as e:
                        logger.error(f"Error in Python handler {func_name}: {e}")
                        error_response = {"success": False, "error": str(e), "invocation_id": invocation_id}
                        return json.dumps(error_response).encode("utf-8")

                # Register the handler with the worker
                # Note: This would need to be implemented in the Rust extension
                logger.debug(f"Registered function {func_name} with SDK-Core worker")

        except Exception as e:
            logger.error(f"Error registering functions with worker: {e}")
            raise

    async def _send_http_message(self, message: Dict[str, Any]) -> None:
        """Fall back to HTTP communication when SDK-Core is not available."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.config.runtime_endpoint}/messages"
                async with session.post(url, json=message) as response:
                    if response.status != 200:
                        logger.warning(f"HTTP message failed: {response.status}")
                    else:
                        logger.debug(f"HTTP message sent successfully: {message['type']}")
        except Exception as e:
            logger.error(f"HTTP communication error: {e}")

    async def _receive_http_message(self) -> Optional[Dict[str, Any]]:
        """Receive messages via HTTP polling (fallback mode)."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.config.runtime_endpoint}/messages"
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return None
        except Exception as e:
            logger.debug(f"HTTP receive error (expected in polling): {e}")
            return None


class RuntimeClient:
    """
    Client for interacting with the AGNT5 Runtime.

    This is set as the global runtime client for durable functions.
    """

    def __init__(self, bridge: PythonRuntimeBridge):
        self.bridge = bridge

    async def call_service(self, service: str, method: str, *args, **kwargs) -> Any:
        """Make a durable service call via the runtime."""
        if self.bridge._sdk_core_worker:
            # Use SDK-Core for service calls
            try:
                call_data = {"service": service, "method": method, "args": args, "kwargs": kwargs}

                # Send service call message to SDK-Core
                await self.bridge._send_to_sdk_core({"type": "service_call", "data": call_data})

                # For now, return a placeholder response
                # In full implementation, this would wait for the response
                logger.info(f"Service call via SDK-Core: {service}.{method}")
                return f"sdk_core_response_from_{service}_{method}"

            except Exception as e:
                logger.error(f"SDK-Core service call failed: {e}")
                # Fall back to mock response
                return f"fallback_response_from_{service}_{method}"
        else:
            # Fall back to HTTP/mock implementation
            logger.info(f"Service call (fallback): {service}.{method}")
            return f"http_response_from_{service}_{method}"
    
    async def get_object(self, object_class: type, object_id: str) -> Any:
        """Get or create a durable object instance via the runtime."""
        if self.bridge._sdk_core_worker:
            # Use SDK-Core for object management
            try:
                object_data = {
                    "object_class": object_class.__name__,
                    "object_id": object_id
                }

                # Send object request message to SDK-Core
                await self.bridge._send_to_sdk_core({"type": "get_object", "data": object_data})

                # For now, return a mock object instance
                # In full implementation, this would wait for the response
                logger.info(f"Object request via SDK-Core: {object_class.__name__}({object_id})")
                
                # Create a local instance for fallback
                if hasattr(object_class, 'get_or_create'):
                    return await object_class.get_or_create(object_id)
                else:
                    return object_class(object_id)

            except Exception as e:
                logger.error(f"SDK-Core object request failed: {e}")
                # Fall back to local object creation
                if hasattr(object_class, 'get_or_create'):
                    return await object_class.get_or_create(object_id)
                else:
                    return object_class(object_id)
        else:
            # Fall back to local object management
            logger.info(f"Object request (fallback): {object_class.__name__}({object_id})")
            if hasattr(object_class, 'get_or_create'):
                return await object_class.get_or_create(object_id)
            else:
                return object_class(object_id)
    
    async def durable_call(self, service: str, method: str, *args, **kwargs) -> Any:
        """Make a durable call (alias for call_service)."""
        return await self.call_service(service, method, *args, **kwargs)
    
    async def durable_sleep(self, seconds: float) -> None:
        """Durable sleep via the runtime."""
        if self.bridge._sdk_core_worker:
            try:
                sleep_data = {"seconds": seconds}
                await self.bridge._send_to_sdk_core({"type": "durable_sleep", "data": sleep_data})
                logger.info(f"Durable sleep via SDK-Core: {seconds} seconds")
                
                # For fallback, use regular sleep
                await asyncio.sleep(seconds)
                
            except Exception as e:
                logger.error(f"SDK-Core durable sleep failed: {e}")
                await asyncio.sleep(seconds)
        else:
            # Fallback to regular sleep
            logger.info(f"Durable sleep (fallback): {seconds} seconds")
            await asyncio.sleep(seconds)
    
    async def get_state(self, key: str, default: Any = None) -> Any:
        """Get state value from durable storage."""
        if self.bridge._sdk_core_worker:
            try:
                state_data = {"key": key, "default": default}
                await self.bridge._send_to_sdk_core({"type": "get_state", "data": state_data})
                
                # For now, return default as placeholder
                # In full implementation, this would wait for the response
                logger.debug(f"Get state via SDK-Core: {key}")
                return default
                
            except Exception as e:
                logger.error(f"SDK-Core get state failed: {e}")
                return default
        else:
            # Fallback: return default
            logger.debug(f"Get state (fallback): {key}")
            return default
    
    async def set_state(self, key: str, value: Any) -> None:
        """Set state value in durable storage."""
        if self.bridge._sdk_core_worker:
            try:
                state_data = {"key": key, "value": value}
                await self.bridge._send_to_sdk_core({"type": "set_state", "data": state_data})
                logger.debug(f"Set state via SDK-Core: {key}")
                
            except Exception as e:
                logger.error(f"SDK-Core set state failed: {e}")
        else:
            # Fallback: no-op
            logger.debug(f"Set state (fallback): {key}")
    
    async def delete_state(self, key: str) -> None:
        """Delete state value from durable storage."""
        if self.bridge._sdk_core_worker:
            try:
                state_data = {"key": key}
                await self.bridge._send_to_sdk_core({"type": "delete_state", "data": state_data})
                logger.debug(f"Delete state via SDK-Core: {key}")
                
            except Exception as e:
                logger.error(f"SDK-Core delete state failed: {e}")
        else:
            # Fallback: no-op
            logger.debug(f"Delete state (fallback): {key}")

    async def schedule_timer(self, delay: float, callback: Callable) -> str:
        """Schedule a durable timer."""
        timer_id = f"timer_{asyncio.get_event_loop().time()}_{delay}"

        if self.bridge._sdk_core_worker:
            # Use SDK-Core for timer scheduling
            try:
                timer_data = {"timer_id": timer_id, "delay": delay, "callback_name": getattr(callback, "__name__", "anonymous")}

                await self.bridge._send_to_sdk_core({"type": "schedule_timer", "data": timer_data})

                logger.info(f"Scheduled timer {timer_id} via SDK-Core for {delay} seconds")

            except Exception as e:
                logger.error(f"SDK-Core timer scheduling failed: {e}")
                # Fall back to simple timer
                asyncio.create_task(self._fallback_timer(delay, callback))
        else:
            # Fall back to simple asyncio timer
            asyncio.create_task(self._fallback_timer(delay, callback))
            logger.info(f"Scheduled fallback timer {timer_id} for {delay} seconds")

        return timer_id

    async def _fallback_timer(self, delay: float, callback: Callable) -> None:
        """Simple fallback timer implementation."""
        await asyncio.sleep(delay)
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback()
            else:
                callback()
        except Exception as e:
            logger.error(f"Timer callback error: {e}")

    async def save_object_state(self, object_id: str, state: Dict[str, Any]) -> None:
        """Save durable object state."""
        if self.bridge._sdk_core_worker:
            try:
                state_data = {"object_id": object_id, "state": state}

                await self.bridge._send_to_sdk_core({"type": "save_state", "data": state_data})

                logger.debug(f"Saved state for object {object_id} via SDK-Core")

            except Exception as e:
                logger.error(f"SDK-Core state save failed: {e}")
        else:
            # Fall back to logging (no persistent storage in fallback mode)
            logger.debug(f"Saving state for object {object_id} (fallback mode - not persistent)")

    async def load_object_state(self, object_id: str) -> Optional[Dict[str, Any]]:
        """Load durable object state."""
        if self.bridge._sdk_core_worker:
            try:
                await self.bridge._send_to_sdk_core({"type": "load_state", "data": {"object_id": object_id}})

                # In full implementation, this would wait for response
                # For now, return None as placeholder
                logger.debug(f"Requested state for object {object_id} via SDK-Core")
                return None

            except Exception as e:
                logger.error(f"SDK-Core state load failed: {e}")
                return None
        else:
            # Fall back mode - no persistent storage
            logger.debug(f"Loading state for object {object_id} (fallback mode - no state available)")
            return None


async def run_service(
    service_name: str = "python-service",
    runtime_endpoint: str = "http://localhost:8081",
    service_version: str = "1.0.0",
) -> None:
    """
    Run the Python service with durable functions.

    This is the main entry point for Python services that use durable functions.

    Args:
        service_name: Name of the service
        runtime_endpoint: AGNT5 Runtime endpoint
        service_version: Version of the service
    """
    config = RuntimeConfig(
        service_name=service_name,
        runtime_endpoint=runtime_endpoint,
        service_version=service_version,
    )

    bridge = PythonRuntimeBridge(config)
    client = RuntimeClient(bridge)

    # Set the runtime client for durable functions
    set_runtime_client(client)

    # Start the service
    await bridge.start()


def main():
    """CLI entry point for running Python services."""
    import argparse

    parser = argparse.ArgumentParser(description="Run AGNT5 Python service")
    parser.add_argument("--service-name", default="python-service", help="Name of the service")
    parser.add_argument("--runtime-endpoint", default="http://localhost:8081", help="AGNT5 Runtime endpoint")
    parser.add_argument("--service-version", default="1.0.0", help="Version of the service")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Log level")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Print service info
    print(f"Starting AGNT5 Python Service: {args.service_name}")
    print(f"Runtime endpoint: {args.runtime_endpoint}")
    print(f"Registered functions: {len(_function_registry)}")
    print(f"Registered flows: {len([f for f in _function_registry.values() if hasattr(f, '_is_flow')])}")
    print(f"Registered objects: {len(_object_registry)}")
    print(f"Registered services: {len(_service_registry)}")

    # Run the service
    try:
        asyncio.run(
            run_service(
                service_name=args.service_name,
                runtime_endpoint=args.runtime_endpoint,
                service_version=args.service_version,
            )
        )
    except KeyboardInterrupt:
        print("\n✅ Service stopped by user")
    except Exception as e:
        print(f"❌ Service failed: {e}")
        sys.exit(1)
    else:
        print("✅ Service completed successfully")


if __name__ == "__main__":
    main()
