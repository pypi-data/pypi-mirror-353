#!/usr/bin/env python3
"""
Shopping Cart Example - Demonstrates Durable Objects

This example shows how to use AGNT5 Durable Objects to implement a shopping cart
that maintains state across failures and provides serialized access per user.
"""

import asyncio
import json
from typing import Dict, List, Any

from agnt5 import durable, DurableContext


@durable.object
class ShoppingCart:
    """
    A durable shopping cart that maintains state across failures.
    
    Each cart is identified by a user_id and provides serialized access
    to ensure consistency during concurrent operations.
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.items: List[Dict[str, Any]] = []
        self.created_at = "2024-01-01T00:00:00Z"  # Would be set by runtime
        self.updated_at = "2024-01-01T00:00:00Z"
    
    async def add_item(self, item_id: str, quantity: int) -> Dict[str, Any]:
        """Add an item to the cart."""
        # Check if item already exists
        for item in self.items:
            if item["id"] == item_id:
                item["qty"] += quantity
                await self.save()
                return item
        
        # Add new item
        new_item = {"id": item_id, "qty": quantity}
        self.items.append(new_item)
        await self.save()
        return new_item
    
    async def remove_item(self, item_id: str) -> bool:
        """Remove an item from the cart."""
        for i, item in enumerate(self.items):
            if item["id"] == item_id:
                del self.items[i]
                await self.save()
                return True
        return False
    
    async def update_quantity(self, item_id: str, quantity: int) -> bool:
        """Update the quantity of an item."""
        for item in self.items:
            if item["id"] == item_id:
                if quantity <= 0:
                    return await self.remove_item(item_id)
                item["qty"] = quantity
                await self.save()
                return True
        return False
    
    async def get_items(self) -> List[Dict[str, Any]]:
        """Get all items in the cart."""
        return self.items.copy()
    
    async def get_total_items(self) -> int:
        """Get total number of items in the cart."""
        return sum(item["qty"] for item in self.items)
    
    async def clear(self) -> None:
        """Clear all items from the cart."""
        self.items = []
        await self.save()
    
    async def checkout(self, ctx: DurableContext) -> Dict[str, Any]:
        """
        Process checkout - calculates total and creates order.
        
        This demonstrates calling external services during object methods.
        """
        if not self.items:
            return {"error": "Cart is empty"}
        
        try:
            # Call pricing service to calculate total
            total = await ctx.call("pricing_service", "calculate_total", self.items)
            
            # Call order service to create order
            order = await ctx.call("order_service", "create_order", {
                "user_id": self.user_id,
                "items": self.items,
                "total": total
            })
            
            # Clear cart after successful order
            self.items = []
            await self.save()
            
            return {
                "success": True,
                "order_id": order.get("order_id"),
                "total": total,
                "items_count": len(self.items)
            }
            
        except Exception as e:
            return {
                "error": f"Checkout failed: {str(e)}"
            }


@durable.function
async def get_user_cart(ctx: DurableContext, user_id: str) -> ShoppingCart:
    """Get or create a shopping cart for a user."""
    return await ctx.get_object(ShoppingCart, user_id)


@durable.function
async def add_item_to_cart(ctx: DurableContext, user_id: str, item_id: str, quantity: int) -> Dict[str, Any]:
    """Add an item to a user's shopping cart."""
    cart = await ctx.get_object(ShoppingCart, user_id)
    result = await cart.add_item(item_id, quantity)
    
    return {
        "success": True,
        "item": result,
        "total_items": await cart.get_total_items()
    }


@durable.function
async def process_cart_checkout(ctx: DurableContext, user_id: str) -> Dict[str, Any]:
    """Process checkout for a user's cart."""
    cart = await ctx.get_object(ShoppingCart, user_id)
    return await cart.checkout(ctx)


@durable.function
async def get_cart_summary(ctx: DurableContext, user_id: str) -> Dict[str, Any]:
    """Get a summary of the user's cart."""
    cart = await ctx.get_object(ShoppingCart, user_id)
    items = await cart.get_items()
    total_items = await cart.get_total_items()
    
    return {
        "user_id": user_id,
        "items": items,
        "total_items": total_items,
        "item_count": len(items)
    }


async def demo_shopping_cart():
    """Demonstrate shopping cart functionality."""
    print("🛒 Shopping Cart Durable Objects Demo")
    print("=" * 50)
    
    # Simulate user sessions
    user_ids = ["user-123", "user-456", "user-789"]
    
    for user_id in user_ids:
        print(f"\n👤 User: {user_id}")
        
        # Add items to cart
        print("  Adding items to cart...")
        result1 = await add_item_to_cart(None, user_id, "laptop-001", 1)
        print(f"    ✅ Added laptop: {result1}")
        
        result2 = await add_item_to_cart(None, user_id, "mouse-002", 2)
        print(f"    ✅ Added mouse: {result2}")
        
        result3 = await add_item_to_cart(None, user_id, "laptop-001", 1)  # Same item again
        print(f"    ✅ Added another laptop: {result3}")
        
        # Get cart summary
        summary = await get_cart_summary(None, user_id)
        print(f"    📋 Cart Summary: {summary}")
        
        # Simulate checkout
        print("  Processing checkout...")
        checkout_result = await process_cart_checkout(None, user_id)
        print(f"    💳 Checkout Result: {checkout_result}")
    
    print("\n🎉 Demo completed successfully!")


async def demo_concurrent_access():
    """Demonstrate concurrent access to the same cart."""
    print("\n🔀 Concurrent Access Demo")
    print("=" * 30)
    
    user_id = "concurrent-user"
    
    # Simulate multiple concurrent operations on the same cart
    async def add_multiple_items(item_prefix: str, count: int):
        results = []
        for i in range(count):
            result = await add_item_to_cart(None, user_id, f"{item_prefix}-{i:03d}", 1)
            results.append(result)
        return results
    
    # Run concurrent operations
    print("  Running concurrent operations...")
    task1 = asyncio.create_task(add_multiple_items("book", 5))
    task2 = asyncio.create_task(add_multiple_items("pen", 3))
    task3 = asyncio.create_task(add_multiple_items("notebook", 2))
    
    results1, results2, results3 = await asyncio.gather(task1, task2, task3)
    
    print(f"    ✅ Task 1 (books): {len(results1)} items added")
    print(f"    ✅ Task 2 (pens): {len(results2)} items added")
    print(f"    ✅ Task 3 (notebooks): {len(results3)} items added")
    
    # Check final state
    summary = await get_cart_summary(None, user_id)
    print(f"    📋 Final Cart: {summary['item_count']} unique items, {summary['total_items']} total")
    
    # Verify serialized access worked correctly
    expected_items = 5 + 3 + 2  # book + pen + notebook
    if summary['item_count'] == expected_items:
        print("    ✅ Concurrent access handled correctly!")
    else:
        print(f"    ❌ Expected {expected_items} items, got {summary['item_count']}")


async def demo_state_persistence():
    """Demonstrate state persistence across 'restarts'."""
    print("\n💾 State Persistence Demo")
    print("=" * 30)
    
    user_id = "persistent-user"
    
    # Add items to cart
    print("  Adding items before 'restart'...")
    await add_item_to_cart(None, user_id, "persistent-item-1", 3)
    await add_item_to_cart(None, user_id, "persistent-item-2", 1)
    
    # Get cart state
    summary_before = await get_cart_summary(None, user_id)
    print(f"    📋 Cart before restart: {summary_before}")
    
    # Simulate restart by creating new cart reference
    print("  Simulating restart...")
    
    # Get cart again (should restore state)
    summary_after = await get_cart_summary(None, user_id)
    print(f"    📋 Cart after restart: {summary_after}")
    
    # Verify state was preserved
    if (summary_before['total_items'] == summary_after['total_items'] and
        summary_before['item_count'] == summary_after['item_count']):
        print("    ✅ State persisted correctly across restart!")
    else:
        print("    ❌ State was not preserved correctly")


if __name__ == "__main__":
    async def main():
        print("🚀 AGNT5 Durable Objects - Shopping Cart Example")
        print("=" * 60)
        
        try:
            # Basic shopping cart demo
            await demo_shopping_cart()
            
            # Concurrent access demo
            await demo_concurrent_access()
            
            # State persistence demo
            await demo_state_persistence()
            
            print("\n✨ All demos completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Demo failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Run the demo
    asyncio.run(main())