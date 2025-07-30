#!/usr/bin/env python3
"""
Basic Memory Operations Example
===============================
Demonstrates core memory operations: store, recall, update, delete
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

os.environ["GOOGLE_API_KEY"] = "AIzaSyBtIh9ShcSmezYKa8xmI0kIyyl2gJZIYFc"

from tbh_secure_agents import Expert

def main():
    expert = Expert(
        specialty="Data Analyst",
        objective="Analyze and remember data patterns",
        memory_duration="long_term",
        user_id="analyst_001"
    )
    
    print("1. Storing memories")
    
    memory_id_1 = expert.remember(
        content="Q4 2024 revenue increased by 15% compared to Q3",
        memory_type=MemoryType.LONG_TERM,
        priority=MemoryPriority.HIGH,
        tags=["revenue", "Q4_2024", "growth"]
    )
    print(f"   Stored revenue data: {memory_id_1}")
    
    memory_id_2 = expert.remember(
        content="Customer satisfaction score improved from 7.2 to 8.1",
        memory_type=MemoryType.LONG_TERM,
        priority=MemoryPriority.MEDIUM,
        tags=["customer_satisfaction", "improvement", "metrics"]
    )
    print(f"   Stored satisfaction data: {memory_id_2}")
    
    memory_id_3 = expert.remember(
        content="New product launch scheduled for March 2025",
        memory_type=MemoryType.LONG_TERM,
        priority=MemoryPriority.HIGH,
        tags=["product_launch", "march_2025", "planning"]
    )
    print(f"   Stored product launch data: {memory_id_3}")
    
    print("\n2. Recalling memories by query")
    
    revenue_memories = expert.recall(
        query="revenue growth financial performance",
        memory_type=MemoryType.LONG_TERM,
        limit=5
    )
    print(f"   Found {len(revenue_memories)} revenue-related memories:")
    for memory in revenue_memories:
        print(f"     - {memory['content']}")
        print(f"       Tags: {memory.get('tags', [])}")
    
    print("\n3. Recalling memories by tags")
    
    satisfaction_memories = expert.recall(
        query="customer satisfaction metrics",
        memory_type=MemoryType.LONG_TERM,
        limit=5
    )
    print(f"   Found {len(satisfaction_memories)} satisfaction memories:")
    for memory in satisfaction_memories:
        print(f"     - {memory['content']}")
    
    print("\n4. Updating a memory")
    
    updated_id = expert.remember(
        content="Q4 2024 revenue increased by 18% compared to Q3 (updated figure)",
        memory_type=MemoryType.LONG_TERM,
        priority=MemoryPriority.HIGH,
        tags=["revenue", "Q4_2024", "growth", "updated"]
    )
    print(f"   Updated revenue memory: {updated_id}")
    
    print("\n5. Recalling all memories")
    
    all_memories = expert.recall(
        query="business data metrics",
        memory_type=MemoryType.LONG_TERM,
        limit=10
    )
    print(f"   Total memories found: {len(all_memories)}")
    for i, memory in enumerate(all_memories, 1):
        print(f"     {i}. {memory['content'][:50]}...")
        print(f"        ID: {memory['id']}")
        print(f"        Priority: {memory.get('priority')}")
        print(f"        Tags: {memory.get('tags', [])}")

if __name__ == "__main__":
    main()
