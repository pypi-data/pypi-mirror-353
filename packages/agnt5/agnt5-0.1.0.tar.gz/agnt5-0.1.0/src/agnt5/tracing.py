"""
OpenAI-style tracing API for AGNT5 Python SDK.

This module provides a comprehensive tracing system inspired by OpenAI's approach,
with zero external dependencies while supporting full integration with the 
Rust SDK-Core through FFI bridge calls.

Design Principles:
- Zero Dependencies: No OpenTelemetry imports in Python SDK
- Simple API: Easy-to-use functions for spans, logs, and metrics
- SDK-Core Communication: Send telemetry data via existing FFI bridge
- Backward Compatible: Non-breaking addition to existing APIs
"""

import os
import time
import uuid
import contextvars
import inspect
from typing import Dict, Optional, Any, Union, List, Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
import threading
import weakref


def _get_caller_info(skip_frames: int = 2) -> Dict[str, Any]:
    """Get file and line information for the caller"""
    try:
        frame = inspect.currentframe()
        for _ in range(skip_frames):
            if frame is not None:
                frame = frame.f_back
        
        if frame is not None:
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno
            func_name = frame.f_code.co_name
            
            # Get relative path for cleaner output
            if "/" in filename:
                short_filename = "/".join(filename.split("/")[-2:])  # last 2 parts
            else:
                short_filename = filename
                
            return {
                "code.filepath": short_filename,
                "code.lineno": lineno,
                "code.function": func_name,
            }
    except Exception:
        # Silently ignore any issues with frame inspection
        pass
    
    return {}


class TraceLevel(Enum):
    """Trace logging levels following OpenTelemetry conventions"""
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"


@dataclass
class Span:
    """Lightweight span representation following OpenAI patterns"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    parent_id: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "ok"
    error: Optional[str] = None
    
    def set_attribute(self, key: str, value: Any):
        """Set span attribute"""
        self.attributes[key] = value
        
    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Add event to span"""
        self.events.append({
            "name": name,
            "timestamp": time.time(),
            "attributes": attributes or {}
        })
        
    def set_error(self, error: Exception):
        """Mark span as error"""
        self.status = "error"
        self.error = str(error)
        self.attributes["error.type"] = type(error).__name__
        self.attributes["error.message"] = str(error)
        
    def finish(self):
        """Finish the span"""
        if self.end_time is None:
            self.end_time = time.time()
    
    @property
    def duration_ms(self) -> float:
        """Get span duration in milliseconds"""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time) * 1000
        return 0.0


@dataclass
class Trace:
    """Trace containing multiple spans"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    spans: List[Span] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    
    def add_span(self, span: Span):
        """Add span to trace"""
        self.spans.append(span)
        
    def finish(self):
        """Finish the trace"""
        if self.end_time is None:
            self.end_time = time.time()


# Context variables for thread-safe trace management (like OpenAI does)
_current_trace: contextvars.ContextVar[Optional[Trace]] = contextvars.ContextVar('current_trace', default=None)
_current_span: contextvars.ContextVar[Optional[Span]] = contextvars.ContextVar('current_span', default=None)


class TraceProcessor:
    """Base class for trace processors - follows OpenAI's pluggable architecture"""
    
    def process_span(self, span: Span, trace: Trace):
        """Process a finished span"""
        pass
        
    def process_trace(self, trace: Trace):
        """Process a finished trace"""
        pass


class SdkCoreTraceProcessor(TraceProcessor):
    """Processor that sends traces to SDK-Core via FFI"""
    
    def __init__(self):
        self._bridge = None  # Will be set when FFI bridge is available
        
    def set_bridge(self, bridge):
        """Set the FFI bridge for communication with SDK-Core"""
        self._bridge = bridge
    
    def process_span(self, span: Span, trace: Trace):
        """Send span to SDK-Core"""
        if self._bridge:
            self._send_span_to_core(span, trace)
        
    def process_trace(self, trace: Trace):
        """Send complete trace to SDK-Core"""
        if self._bridge:
            self._send_trace_to_core(trace)
    
    def _send_span_to_core(self, span: Span, trace: Trace):
        """FFI call to send span data to SDK-Core"""
        span_data = {
            "span_id": span.id,
            "trace_id": trace.id,
            "parent_id": span.parent_id,
            "name": span.name,
            "start_time": span.start_time,
            "end_time": span.end_time,
            "duration_ms": span.duration_ms,
            "attributes": span.attributes,
            "events": span.events,
            "status": span.status,
            "error": span.error,
        }
        
        try:
            # This would call SDK-Core FFI when bridge is available
            if hasattr(self._bridge, 'send_span'):
                self._bridge.send_span(span_data)
        except Exception as e:
            # Log error but don't fail - telemetry should never break the application
            print(f"Warning: Failed to send span to SDK-Core: {e}")
        
    def _send_trace_to_core(self, trace: Trace):
        """FFI call to send complete trace to SDK-Core"""
        trace_data = {
            "trace_id": trace.id,
            "metadata": trace.metadata,
            "start_time": trace.start_time,
            "end_time": trace.end_time,
            "span_count": len(trace.spans),
        }
        
        try:
            # This would call SDK-Core FFI when bridge is available
            if hasattr(self._bridge, 'send_trace'):
                self._bridge.send_trace(trace_data)
        except Exception as e:
            # Log error but don't fail - telemetry should never break the application
            print(f"Warning: Failed to send trace to SDK-Core: {e}")


class LoggingTraceProcessor(TraceProcessor):
    """Processor that logs traces for debugging"""
    
    def process_span(self, span: Span, trace: Trace):
        """Log span completion"""
        # Extract file and line info from attributes
        file_info = ""
        if "code.filepath" in span.attributes and "code.lineno" in span.attributes:
            file_info = f" [{span.attributes['code.filepath']}:{span.attributes['code.lineno']}]"
        
        if span.status == "error":
            print(f"ERROR: Span {span.name} failed: {span.error}{file_info}")
        else:
            print(f"DEBUG: Span {span.name} completed in {span.duration_ms:.2f}ms{file_info}")
        
    def process_trace(self, trace: Trace):
        """Log trace completion"""
        duration = (trace.end_time - trace.start_time) * 1000 if trace.end_time else 0
        print(f"DEBUG: Trace {trace.id} completed with {len(trace.spans)} spans in {duration:.2f}ms")


class TracingConfig:
    """Configuration for tracing system - inspired by OpenAI's approach"""
    
    def __init__(self):
        self.enabled = os.getenv("AGNT5_TRACING_ENABLED", "true").lower() == "true"
        self.level = TraceLevel(os.getenv("AGNT5_TRACING_LEVEL", "info"))
        self.sample_rate = float(os.getenv("AGNT5_TRACING_SAMPLE_RATE", "1.0"))
        self.capture_inputs = os.getenv("AGNT5_TRACING_CAPTURE_INPUTS", "true").lower() == "true"
        self.capture_outputs = os.getenv("AGNT5_TRACING_CAPTURE_OUTPUTS", "true").lower() == "true"
        self.max_attribute_length = int(os.getenv("AGNT5_TRACING_MAX_ATTRIBUTE_LENGTH", "1000"))
        self.debug_logging = os.getenv("AGNT5_TRACING_DEBUG", "false").lower() == "true"
        
        # Initialize processors
        self.processors: List[TraceProcessor] = []
        self._setup_default_processors()
        
    def _setup_default_processors(self):
        """Setup default trace processors"""
        # Always add SDK-Core processor for production telemetry
        self.processors.append(SdkCoreTraceProcessor())
        
        # Add logging processor for debugging if enabled
        if self.debug_logging:
            self.processors.append(LoggingTraceProcessor())
    
    def should_sample(self) -> bool:
        """Determine if current operation should be sampled"""
        if not self.enabled:
            return False
        if self.sample_rate >= 1.0:
            return True
        if self.sample_rate <= 0.0:
            return False
        return time.time() % 1.0 < self.sample_rate


# Global config instance
_config = TracingConfig()


class TracingContext:
    """Main tracing context manager - similar to OpenAI's design"""
    
    @classmethod
    def set_processors(cls, processors: List[TraceProcessor]):
        """Set trace processors"""
        _config.processors = processors
        
    @classmethod
    def add_processor(cls, processor: TraceProcessor):
        """Add a trace processor"""
        _config.processors.append(processor)
        
    @classmethod
    def configure(cls, **kwargs):
        """Configure tracing settings"""
        for key, value in kwargs.items():
            if hasattr(_config, key):
                setattr(_config, key, value)
    
    @classmethod
    def get_config(cls) -> TracingConfig:
        """Get current tracing configuration"""
        return _config
    
    @classmethod
    def set_bridge(cls, bridge):
        """Set FFI bridge for SDK-Core communication"""
        for processor in _config.processors:
            if isinstance(processor, SdkCoreTraceProcessor):
                processor.set_bridge(bridge)


# Core tracing functions following OpenAI patterns
def start_trace(name: str, metadata: Optional[Dict[str, Any]] = None) -> Trace:
    """Start a new trace"""
    if not _config.should_sample():
        return Trace()  # Return dummy trace
        
    trace = Trace(metadata=metadata or {})
    trace.metadata["name"] = name
    trace.metadata["service"] = "agnt5-python-sdk"
    trace.metadata["component"] = "python-sdk"
    _current_trace.set(trace)
    return trace


def end_trace() -> Optional[Trace]:
    """End current trace"""
    trace = _current_trace.get()
    if trace:
        trace.finish()
        # Process with all processors
        for processor in _config.processors:
            try:
                processor.process_trace(trace)
            except Exception as e:
                if _config.debug_logging:
                    print(f"Warning: Trace processor failed: {e}")
        _current_trace.set(None)
    return trace


@contextmanager
def trace(name: str, metadata: Optional[Dict[str, Any]] = None):
    """Context manager for traces - OpenAI style"""
    trace_obj = start_trace(name, metadata)
    try:
        yield trace_obj
    finally:
        end_trace()


def start_span(name: str, attributes: Optional[Dict[str, Any]] = None) -> Span:
    """Start a new span"""
    if not _config.should_sample():
        return Span()  # Return dummy span
        
    current_span = _current_span.get()
    parent_id = current_span.id if current_span else None
    
    # Get caller information for file and line number
    caller_info = _get_caller_info(skip_frames=2)
    
    # Combine caller info with provided attributes
    safe_attributes = caller_info.copy()
    if attributes:
        for key, value in attributes.items():
            str_value = str(value)
            if len(str_value) > _config.max_attribute_length:
                str_value = str_value[:_config.max_attribute_length] + "..."
            safe_attributes[key] = str_value
    
    span = Span(name=name, parent_id=parent_id, attributes=safe_attributes)
    
    # Add to current trace
    current_trace = _current_trace.get()
    if current_trace:
        current_trace.add_span(span)
        
    _current_span.set(span)
    return span


def end_span() -> Optional[Span]:
    """End current span"""
    span = _current_span.get()
    if span:
        span.finish()
        
        # Process with all processors
        current_trace = _current_trace.get()
        for processor in _config.processors:
            try:
                processor.process_span(span, current_trace)
            except Exception as e:
                if _config.debug_logging:
                    print(f"Warning: Span processor failed: {e}")
            
        # Restore parent span
        if current_trace:
            parent_span = None
            for s in reversed(current_trace.spans):
                if s.id == span.parent_id:
                    parent_span = s
                    break
            _current_span.set(parent_span)
        else:
            _current_span.set(None)
            
    return span


@contextmanager
def span(name: str, attributes: Optional[Dict[str, Any]] = None):
    """Context manager for spans - OpenAI style"""
    span_obj = start_span(name, attributes)
    try:
        yield span_obj
    except Exception as e:
        span_obj.set_error(e)
        raise
    finally:
        end_span()


# Convenience functions
def get_current_span() -> Optional[Span]:
    """Get current active span"""
    return _current_span.get()


def get_current_trace() -> Optional[Trace]:
    """Get current active trace"""
    return _current_trace.get()


def set_span_attribute(key: str, value: Any):
    """Set attribute on current span"""
    current_span = _current_span.get()
    if current_span:
        current_span.set_attribute(key, value)


def add_span_event(name: str, attributes: Optional[Dict[str, Any]] = None):
    """Add event to current span"""
    current_span = _current_span.get()
    if current_span:
        current_span.add_event(name, attributes)


def log(level: TraceLevel, message: str, **attributes):
    """Log message with current span context"""
    current_span = _current_span.get()
    if current_span:
        # Get caller information for file and line number
        caller_info = _get_caller_info(skip_frames=2)
        
        current_span.add_event(f"log.{level.value}", {
            "message": message,
            **caller_info,
            **attributes
        })


# Convenience logging functions that include file/line info
def debug(message: str, **attributes):
    """Debug log with file and line information"""
    caller_info = _get_caller_info(skip_frames=2)
    if _config.debug_logging:
        file_info = f" [{caller_info.get('code.filepath', 'unknown')}:{caller_info.get('code.lineno', '?')}]"
        print(f"DEBUG: {message}{file_info}")
    log(TraceLevel.DEBUG, message, **attributes)


def info(message: str, **attributes):
    """Info log with file and line information"""
    caller_info = _get_caller_info(skip_frames=2)
    if _config.debug_logging:
        file_info = f" [{caller_info.get('code.filepath', 'unknown')}:{caller_info.get('code.lineno', '?')}]"
        print(f"INFO: {message}{file_info}")
    log(TraceLevel.INFO, message, **attributes)


def warn(message: str, **attributes):
    """Warning log with file and line information"""
    caller_info = _get_caller_info(skip_frames=2)
    if _config.debug_logging:
        file_info = f" [{caller_info.get('code.filepath', 'unknown')}:{caller_info.get('code.lineno', '?')}]"
        print(f"WARN: {message}{file_info}")
    log(TraceLevel.WARN, message, **attributes)


def error(message: str, **attributes):
    """Error log with file and line information"""
    caller_info = _get_caller_info(skip_frames=2)
    file_info = f" [{caller_info.get('code.filepath', 'unknown')}:{caller_info.get('code.lineno', '?')}]"
    print(f"ERROR: {message}{file_info}")
    log(TraceLevel.ERROR, message, **attributes)


# Decorators for automatic tracing
def traced(name: Optional[str] = None, capture_args: bool = False, capture_result: bool = False):
    """Decorator for automatic function tracing - OpenAI style"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            span_name = name or f"{func.__module__}.{func.__name__}"
            
            span_attributes = {
                "function.name": func.__name__,
                "function.module": func.__module__,
            }
            
            if capture_args and _config.capture_inputs:
                # Safely capture arguments (truncate if too long)
                args_str = str(args)[:_config.max_attribute_length]
                kwargs_str = str(kwargs)[:_config.max_attribute_length]
                span_attributes.update({
                    "function.args": args_str,
                    "function.kwargs": kwargs_str,
                })
            
            with span(span_name, span_attributes) as s:
                try:
                    result = func(*args, **kwargs)
                    
                    if capture_result and _config.capture_outputs:
                        result_str = str(result)[:_config.max_attribute_length]
                        s.set_attribute("function.result", result_str)
                        
                    return result
                except Exception as e:
                    s.set_error(e)
                    raise
                    
        return wrapper
    return decorator


# Agent-specific tracing helpers
def trace_agent_run(agent_name: str):
    """Start an agent run trace"""
    return trace(f"agent.{agent_name}.run", {
        "agent.name": agent_name,
        "agent.type": "high_level",
    })


def trace_tool_call(tool_name: str):
    """Start a tool call span"""
    return span(f"tool.{tool_name}", {
        "tool.name": tool_name,
        "tool.type": "function",
    })


def trace_llm_call(model: str, prompt_length: int):
    """Start an LLM call span"""
    return span("llm.call", {
        "llm.model": model,
        "llm.prompt_length": prompt_length,
        "llm.provider": "anthropic",
    })


def trace_workflow_step(step_name: str, step_index: int):
    """Start a workflow step span"""
    return span(f"workflow.step.{step_name}", {
        "workflow.step.name": step_name,
        "workflow.step.index": step_index,
    })


def trace_memory_operation(operation: str, memory_type: str):
    """Start a memory operation span"""
    return span(f"memory.{operation}", {
        "memory.operation": operation,
        "memory.type": memory_type,
    })


# Public API for configuration
def enable_tracing():
    """Enable tracing"""
    _config.enabled = True


def disable_tracing():
    """Disable tracing"""
    _config.enabled = False


def is_tracing_enabled() -> bool:
    """Check if tracing is enabled"""
    return _config.enabled and _config.should_sample()


def set_sample_rate(rate: float):
    """Set sampling rate (0.0 to 1.0)"""
    _config.sample_rate = max(0.0, min(1.0, rate))


def get_trace_stats() -> Dict[str, Any]:
    """Get tracing statistics"""
    current_trace = get_current_trace()
    current_span = get_current_span()
    
    return {
        "enabled": _config.enabled,
        "sample_rate": _config.sample_rate,
        "current_trace_id": current_trace.id if current_trace else None,
        "current_span_id": current_span.id if current_span else None,
        "processor_count": len(_config.processors),
        "config": {
            "capture_inputs": _config.capture_inputs,
            "capture_outputs": _config.capture_outputs,
            "debug_logging": _config.debug_logging,
            "max_attribute_length": _config.max_attribute_length,
        }
    }


# Initialize telemetry on module import
def _initialize_telemetry():
    """Initialize telemetry system with environment-based configuration"""
    if _config.debug_logging:
        print("AGNT5 Tracing: Initialized with zero-dependency telemetry")
        print(f"AGNT5 Tracing: Sample rate = {_config.sample_rate}")
        print(f"AGNT5 Tracing: Processors = {len(_config.processors)}")


# Call initialization
_initialize_telemetry()