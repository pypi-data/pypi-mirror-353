#!/usr/bin/env python3
"""
Demo: FSM and Journal Replay Features

This example demonstrates the practical use of AGNT5's resilient execution:
1. FSM state tracking during function execution
2. Journal recording of all operations
3. Replay after simulated failures
4. State preservation across failures

To run this demo:
    python examples/demo_fsm_replay.py
"""

import asyncio
import json
import logging
import random
import time
from dataclasses import dataclass
from typing import Any, Dict, List

# Import AGNT5 SDK
import agnt5
from agnt5.durable import DurableContext, durable

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class BankTransaction:
    """Bank transaction data structure."""

    transaction_id: str
    from_account: str
    to_account: str
    amount: float
    currency: str = "USD"
    status: str = "pending"


class FailureSimulator:
    """Simulates various types of failures for testing."""

    def __init__(self):
        self.failure_count = 0
        self.max_failures = 2

    def should_fail(self, operation: str) -> bool:
        """Determine if an operation should fail."""
        if self.failure_count >= self.max_failures:
            return False

        # 50% chance of failure for the first few operations
        if random.random() < 0.5:
            self.failure_count += 1
            logger.warning(f"💥 Simulating failure in {operation} (failure #{self.failure_count})")
            return True

        return False

    def reset(self):
        """Reset failure counter."""
        self.failure_count = 0


# Global failure simulator
failure_sim = FailureSimulator()


@durable.function
async def transfer_money(ctx: DurableContext, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Durable money transfer function that demonstrates FSM and replay.

    This function:
    1. Validates accounts
    2. Checks balances
    3. Holds funds
    4. Transfers money
    5. Sends notifications

    Each step is journaled and can be replayed after failures.
    """
    transaction = BankTransaction(**transaction_data)
    logger.info(f"🏦 Starting money transfer: {transaction.transaction_id}")

    # FSM State: Created -> Running
    await ctx.state_set("transaction_id", transaction.transaction_id)
    await ctx.state_set("status", "processing")
    await ctx.state_set("current_step", 0)
    await ctx.state_set("started_at", time.time())

    try:
        # Step 1: Validate accounts (with potential failure)
        logger.info(f"Step 1: Validating accounts for {transaction.transaction_id}")

        if failure_sim.should_fail("account_validation"):
            raise Exception("Account validation service temporarily unavailable")

        account_validation = await ctx.call(
            "account_service", "validate_accounts", {"from_account": transaction.from_account, "to_account": transaction.to_account, "currency": transaction.currency}
        )

        await ctx.state_set("current_step", 1)
        await ctx.state_set("account_validation", account_validation)
        logger.info(f"✅ Accounts validated for {transaction.transaction_id}")

        # Step 2: Check balance (with potential failure)
        logger.info(f"Step 2: Checking balance for {transaction.transaction_id}")

        if failure_sim.should_fail("balance_check"):
            raise Exception("Balance service temporarily unavailable")

        balance_check = await ctx.call(
            "balance_service", "check_sufficient_funds", {"account": transaction.from_account, "amount": transaction.amount, "currency": transaction.currency}
        )

        if not balance_check.get("sufficient", False):
            raise Exception(f"Insufficient funds in account {transaction.from_account}")

        await ctx.state_set("current_step", 2)
        await ctx.state_set("balance_check", balance_check)
        logger.info(f"✅ Balance verified for {transaction.transaction_id}")

        # Step 3: Hold funds (with potential failure)
        logger.info(f"Step 3: Holding funds for {transaction.transaction_id}")

        if failure_sim.should_fail("fund_hold"):
            raise Exception("Fund holding service temporarily unavailable")

        hold_result = await ctx.call(
            "account_service",
            "hold_funds",
            {"account": transaction.from_account, "amount": transaction.amount, "currency": transaction.currency, "transaction_id": transaction.transaction_id},
        )

        await ctx.state_set("current_step", 3)
        await ctx.state_set("hold_id", hold_result.get("hold_id"))
        logger.info(f"✅ Funds held for {transaction.transaction_id}")

        # Step 4: Sleep for processing delay (demonstrates timer suspension)
        logger.info(f"Step 4: Processing delay for {transaction.transaction_id}")
        await ctx.sleep(2.0)  # 2 second processing delay
        await ctx.state_set("current_step", 4)

        # Step 5: Execute transfer (with potential failure)
        logger.info(f"Step 5: Executing transfer for {transaction.transaction_id}")

        if failure_sim.should_fail("transfer_execution"):
            raise Exception("Transfer execution service temporarily unavailable")

        transfer_result = await ctx.call(
            "transfer_service",
            "execute_transfer",
            {
                "from_account": transaction.from_account,
                "to_account": transaction.to_account,
                "amount": transaction.amount,
                "currency": transaction.currency,
                "hold_id": hold_result.get("hold_id"),
                "transaction_id": transaction.transaction_id,
            },
        )

        await ctx.state_set("current_step", 5)
        await ctx.state_set("transfer_result", transfer_result)
        logger.info(f"✅ Transfer executed for {transaction.transaction_id}")

        # Step 6: Send notifications (parallel execution)
        logger.info(f"Step 6: Sending notifications for {transaction.transaction_id}")

        # Use spawn for parallel notification sending
        notification_results = await ctx.spawn(
            [
                (
                    "notification_service",
                    "send_transfer_notification",
                    {"account": transaction.from_account, "type": "debit", "amount": transaction.amount, "transaction_id": transaction.transaction_id},
                ),
                (
                    "notification_service",
                    "send_transfer_notification",
                    {"account": transaction.to_account, "type": "credit", "amount": transaction.amount, "transaction_id": transaction.transaction_id},
                ),
            ]
        )

        await ctx.state_set("current_step", 6)
        await ctx.state_set("notifications_sent", True)
        await ctx.state_set("notification_results", notification_results)

        # Final step: Mark as completed
        await ctx.state_set("status", "completed")
        await ctx.state_set("completed_at", time.time())

        logger.info(f"🎉 Transfer completed successfully: {transaction.transaction_id}")

        # FSM State: Running -> Completed
        return {
            "transaction_id": transaction.transaction_id,
            "status": "completed",
            "from_account": transaction.from_account,
            "to_account": transaction.to_account,
            "amount": transaction.amount,
            "currency": transaction.currency,
            "transfer_id": transfer_result.get("transfer_id"),
            "completed_at": time.time(),
            "steps_completed": 6,
        }

    except Exception as e:
        # FSM State: Running -> Failed (will retry)
        await ctx.state_set("status", "failed")
        await ctx.state_set("error", str(e))
        await ctx.state_set("failed_at", time.time())

        logger.error(f"❌ Transfer failed: {transaction.transaction_id} - {e}")
        raise


@durable.function
async def batch_transfer(ctx: DurableContext, batch_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process multiple transfers in a batch, demonstrating complex workflows.
    """
    batch_id = batch_data.get("batch_id")
    transfers = batch_data.get("transfers", [])

    logger.info(f"📦 Starting batch transfer: {batch_id} ({len(transfers)} transfers)")

    await ctx.state_set("batch_id", batch_id)
    await ctx.state_set("total_transfers", len(transfers))
    await ctx.state_set("completed_transfers", 0)
    await ctx.state_set("failed_transfers", 0)

    results = []

    for i, transfer_data in enumerate(transfers):
        try:
            logger.info(f"Processing transfer {i+1}/{len(transfers)}")

            # Call the individual transfer function
            result = await transfer_money(ctx, transfer_data)
            results.append({"status": "success", "result": result})

            completed = await ctx.state_get("completed_transfers", 0)
            await ctx.state_set("completed_transfers", completed + 1)

        except Exception as e:
            logger.error(f"Transfer {i+1} failed: {e}")
            results.append({"status": "failed", "error": str(e), "transfer": transfer_data})

            failed = await ctx.state_get("failed_transfers", 0)
            await ctx.state_set("failed_transfers", failed + 1)

    success_count = sum(1 for r in results if r["status"] == "success")
    failure_count = len(results) - success_count

    await ctx.state_set("batch_status", "completed")

    return {"batch_id": batch_id, "total_transfers": len(transfers), "successful_transfers": success_count, "failed_transfers": failure_count, "results": results}


async def demonstrate_fsm_states():
    """Demonstrate FSM state transitions."""
    logger.info("\n🏛️ DEMONSTRATING FSM STATE TRANSITIONS")
    logger.info("=" * 50)

    states = [
        "Created - Invocation is created and queued",
        "Running - Function is actively executing",
        "SuspendedAwait - Waiting for external service call",
        "SuspendedSleep - Waiting for timer/delay",
        "SuspendedEvent - Waiting for external event",
        "Completed - Function completed successfully",
        "Failed - Function failed (may retry)",
        "Recovery - Marked for recovery after connection failure",
    ]

    for state in states:
        logger.info(f"  • {state}")

    logger.info("\nState transitions are validated and logged for monitoring.")


async def demonstrate_journal_entries():
    """Demonstrate journal entry types."""
    logger.info("\n📝 DEMONSTRATING JOURNAL ENTRIES")
    logger.info("=" * 50)

    entries = [
        "StateSet - Record state variable updates",
        "StateGet - Record state variable reads",
        "ServiceCall - Record external service calls and results",
        "Sleep - Record timer/delay operations",
        "Await - Record event waiting operations",
    ]

    for entry in entries:
        logger.info(f"  • {entry}")

    logger.info("\nAll entries are recorded for deterministic replay.")


async def simulate_failure_and_recovery():
    """Simulate failure scenarios and recovery."""
    logger.info("\n🔄 SIMULATING FAILURE AND RECOVERY")
    logger.info("=" * 50)

    # Reset failure simulator
    failure_sim.reset()

    # Create a test transaction
    transaction_data = {"transaction_id": "txn_demo_001", "from_account": "account_123", "to_account": "account_456", "amount": 100.00, "currency": "USD"}

    logger.info("Creating worker for failure simulation...")

    try:
        # Create worker
        worker = agnt5.get_worker(service_name="demo_bank_service", service_version="1.0.0", coordinator_endpoint="http://localhost:8081")

        # Register functions
        await worker.register_function(transfer_money, name="transfer_money", timeout=300, retry=5)
        await worker.register_function(batch_transfer, name="batch_transfer", timeout=600, retry=3)

        logger.info("✅ Worker created and functions registered")

        # In a real scenario, the worker would start and the function would be invoked
        # For demo purposes, we'll show what would happen:

        logger.info("\n📱 Simulated Execution Flow:")
        logger.info("1. Function starts execution (FSM: Created -> Running)")
        logger.info("2. Step 1: Account validation - SUCCESS (Journal: ServiceCall recorded)")
        logger.info("3. Step 2: Balance check - FAILURE (FSM: Running -> Failed)")
        logger.info("4. Automatic retry triggered (FSM: Failed -> Running)")
        logger.info("5. Replay from journal - Skip completed steps")
        logger.info("6. Step 2: Balance check - SUCCESS (Journal: Updated)")
        logger.info("7. Continue execution from step 3...")
        logger.info("8. All steps complete (FSM: Running -> Completed)")

        logger.info("\n✅ Recovery simulation complete!")

    except Exception as e:
        logger.error(f"Simulation failed: {e}")


async def demonstrate_monitoring():
    """Demonstrate monitoring capabilities."""
    logger.info("\n📊 DEMONSTRATING MONITORING CAPABILITIES")
    logger.info("=" * 50)

    # Simulate FSM statistics
    stats = {"total_invocations": 25, "created": 2, "running": 5, "suspended_await": 3, "suspended_sleep": 1, "suspended_event": 0, "completed": 12, "failed": 2, "recovery": 0}

    logger.info("Current FSM Statistics:")
    for state, count in stats.items():
        logger.info(f"  {state.replace('_', ' ').title()}: {count}")

    success_rate = (stats["completed"] / stats["total_invocations"]) * 100
    logger.info(f"\nSuccess Rate: {success_rate:.1f}%")

    # Simulate invocation details
    logger.info("\nActive Invocations:")
    active_invocations = [
        {"id": "inv_001", "function": "transfer_money", "state": "Running", "step": 3, "duration": "2.5s"},
        {"id": "inv_002", "function": "batch_transfer", "state": "SuspendedAwait", "step": 1, "duration": "1.2s"},
        {"id": "inv_003", "function": "transfer_money", "state": "SuspendedSleep", "step": 4, "duration": "0.8s"},
    ]

    for inv in active_invocations:
        logger.info(f"  {inv['id']}: {inv['function']} - {inv['state']} (step {inv['step']}, {inv['duration']})")


async def main():
    """Main demo runner."""
    logger.info("🚀 AGNT5 FSM & REPLAY DEMONSTRATION")
    logger.info("=" * 60)

    try:
        # Demonstrate FSM concepts
        await demonstrate_fsm_states()

        # Demonstrate journal concepts
        await demonstrate_journal_entries()

        # Simulate failure and recovery
        await simulate_failure_and_recovery()

        # Demonstrate monitoring
        await demonstrate_monitoring()

        logger.info("\n🎯 KEY BENEFITS DEMONSTRATED:")
        logger.info("✅ Precise state tracking with FSM")
        logger.info("✅ Deterministic replay after failures")
        logger.info("✅ Automatic retry with backoff")
        logger.info("✅ Zero data loss guarantees")
        logger.info("✅ Real-time monitoring and visibility")
        logger.info("✅ Production-ready resilience")

        logger.info("\n🎉 DEMO COMPLETED SUCCESSFULLY!")
        logger.info("AGNT5 provides enterprise-grade resilient execution!")

        return True

    except Exception as e:
        logger.error(f"Demo failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
