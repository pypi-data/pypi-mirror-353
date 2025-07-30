#!/usr/bin/env python3
"""
Memory Types Demonstration
===========================
Shows different memory types: LONG_TERM, SESSION, WORKING
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

os.environ["GOOGLE_API_KEY"] = "AIzaSyBtIh9ShcSmezYKa8xmI0kIyyl2gJZIYFc"

from tbh_secure_agents.agent import Expert
from tbh_secure_agents.memory.models import MemoryType, MemoryPriority

def main():
    expert = Expert(
        specialty="Knowledge Worker",
        objective="Demonstrate different memory types",
        memory_duration="long_term",
        user_id="memory_types_demo"
    )
    
    print("1. Storing different types of memories")
    
    print("\n   LONG_TERM memories (persistent across sessions):")
    expert.remember(
        content="Company policy: Remote work allowed 3 days per week",
        memory_type=MemoryType.LONG_TERM,
        priority=MemoryPriority.HIGH,
        tags=["policy", "remote_work", "permanent"]
    )
    
    expert.remember(
        content="Annual budget for 2025: $2.5 million",
        memory_type=MemoryType.LONG_TERM,
        priority=MemoryPriority.HIGH,
        tags=["budget", "2025", "financial"]
    )
    print("     Stored company policies and budget information")
    
    print("\n   SESSION memories (current session only):")
    expert.remember(
        content="Today's meeting notes: Discussed Q1 priorities",
        memory_type=MemoryType.SESSION,
        priority=MemoryPriority.MEDIUM,
        tags=["meeting", "Q1", "temporary"]
    )
    
    expert.remember(
        content="Current task: Prepare presentation for tomorrow",
        memory_type=MemoryType.SESSION,
        priority=MemoryPriority.HIGH,
        tags=["task", "presentation", "urgent"]
    )
    print("     Stored session-specific information")
    
    print("\n   WORKING memories (temporary processing):")
    expert.remember(
        content="Calculation result: 15% growth rate for last quarter",
        memory_type=MemoryType.WORKING,
        priority=MemoryPriority.LOW,
        tags=["calculation", "growth", "temporary"]
    )
    
    expert.remember(
        content="Draft idea: Implement AI chatbot for customer support",
        memory_type=MemoryType.WORKING,
        priority=MemoryPriority.MEDIUM,
        tags=["idea", "AI", "draft"]
    )
    print("     Stored working/temporary information")
    
    print("\n2. Retrieving memories by type")
    
    print("\n   LONG_TERM memories:")
    long_term = expert.recall(
        query="policy budget company",
        memory_type=MemoryType.LONG_TERM,
        limit=10
    )
    for memory in long_term:
        print(f"     - {memory['content']}")
        print(f"       Priority: {memory.get('priority')}")
    
    print("\n   SESSION memories:")
    session = expert.recall(
        query="meeting task today",
        memory_type=MemoryType.SESSION,
        limit=10
    )
    for memory in session:
        print(f"     - {memory['content']}")
        print(f"       Tags: {memory.get('tags', [])}")
    
    print("\n   WORKING memories:")
    working = expert.recall(
        query="calculation idea draft",
        memory_type=MemoryType.WORKING,
        limit=10
    )
    for memory in working:
        print(f"     - {memory['content']}")
        print(f"       Tags: {memory.get('tags', [])}")
    
    print("\n3. Retrieving all memories (mixed types)")
    
    all_memories = expert.recall(
        query="work company task",
        limit=20
    )
    
    print(f"\n   Total memories found: {len(all_memories)}")
    
    memory_type_counts = {}
    for memory in all_memories:
        mem_type = memory.get('memory_type', 'unknown')
        memory_type_counts[mem_type] = memory_type_counts.get(mem_type, 0) + 1
        print(f"     - [{mem_type}] {memory['content'][:50]}...")
    
    print(f"\n   Memory type distribution:")
    for mem_type, count in memory_type_counts.items():
        print(f"     {mem_type}: {count} memories")

if __name__ == "__main__":
    main()
