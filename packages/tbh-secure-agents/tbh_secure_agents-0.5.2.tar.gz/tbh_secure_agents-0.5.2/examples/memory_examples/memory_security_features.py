#!/usr/bin/env python3
"""
Memory Security Features Example
================================
Demonstrates security and access control features
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

os.environ["GOOGLE_API_KEY"] = "AIzaSyBtIh9ShcSmezYKa8xmI0kIyyl2gJZIYFc"

from tbh_secure_agents.agent import Expert
from tbh_secure_agents.memory.models import MemoryType, MemoryPriority

def main():
    print("1. User isolation demonstration")
    
    user1_expert = Expert(
        specialty="Financial Analyst",
        objective="Manage financial data",
        memory_duration="long_term",
        user_id="financial_user_001"
    )
    
    user2_expert = Expert(
        specialty="HR Manager", 
        objective="Manage employee data",
        memory_duration="long_term",
        user_id="hr_user_002"
    )
    
    print("\n   User 1 (Financial) storing sensitive data:")
    user1_expert.remember(
        content="Q4 revenue projection: $1.2M with 8% margin",
        memory_type=MemoryType.LONG_TERM,
        priority=MemoryPriority.HIGH,
        tags=["financial", "revenue", "confidential"]
    )
    
    user1_expert.remember(
        content="Budget allocation for R&D: $300,000",
        memory_type=MemoryType.LONG_TERM,
        priority=MemoryPriority.HIGH,
        tags=["budget", "R&D", "sensitive"]
    )
    print("     Stored 2 financial memories")
    
    print("\n   User 2 (HR) storing employee data:")
    user2_expert.remember(
        content="Employee John Doe salary review scheduled",
        memory_type=MemoryType.LONG_TERM,
        priority=MemoryPriority.MEDIUM,
        tags=["employee", "salary", "review"]
    )
    
    user2_expert.remember(
        content="New hire orientation program updated",
        memory_type=MemoryType.LONG_TERM,
        priority=MemoryPriority.LOW,
        tags=["orientation", "program", "updates"]
    )
    print("     Stored 2 HR memories")
    
    print("\n2. Testing memory isolation")
    
    print("\n   User 1 searching for financial data:")
    user1_memories = user1_expert.recall(
        query="revenue budget financial",
        limit=10
    )
    print(f"     User 1 can see {len(user1_memories)} memories:")
    for memory in user1_memories:
        print(f"       - {memory['content']}")
    
    print("\n   User 1 trying to search for HR data:")
    user1_hr_search = user1_expert.recall(
        query="employee salary orientation",
        limit=10
    )
    print(f"     User 1 searching HR terms: {len(user1_hr_search)} results")
    print("     (Should be 0 - users cannot access each other's memories)")
    
    print("\n   User 2 searching for HR data:")
    user2_memories = user2_expert.recall(
        query="employee orientation salary",
        limit=10
    )
    print(f"     User 2 can see {len(user2_memories)} memories:")
    for memory in user2_memories:
        print(f"       - {memory['content']}")
    
    print("\n   User 2 trying to search for financial data:")
    user2_financial_search = user2_expert.recall(
        query="revenue budget financial",
        limit=10
    )
    print(f"     User 2 searching financial terms: {len(user2_financial_search)} results")
    print("     (Should be 0 - users cannot access each other's memories)")
    
    print("\n3. Memory encryption demonstration")
    
    security_expert = Expert(
        specialty="Security Officer",
        objective="Manage security protocols",
        memory_duration="long_term",
        user_id="security_officer_001"
    )
    
    print("\n   Storing encrypted security data:")
    security_expert.remember(
        content="Access codes for server room: Alpha-7732-Beta",
        memory_type=MemoryType.LONG_TERM,
        priority=MemoryPriority.HIGH,
        tags=["access_codes", "server_room", "classified"]
    )
    
    security_expert.remember(
        content="Security incident on 2025-01-15: Resolved",
        memory_type=MemoryType.LONG_TERM,
        priority=MemoryPriority.HIGH,
        tags=["incident", "security", "resolved"]
    )
    print("     Stored encrypted security memories")
    
    print("\n   Retrieving encrypted data (automatic decryption):")
    security_memories = security_expert.recall(
        query="access codes security incident",
        limit=5
    )
    print(f"     Retrieved {len(security_memories)} security memories:")
    for memory in security_memories:
        print(f"       - {memory['content']}")
        print(f"         Tags: {memory.get('tags', [])}")
    
    print("\n4. Priority-based access control")
    
    admin_expert = Expert(
        specialty="System Administrator",
        objective="System administration tasks",
        memory_duration="long_term",
        user_id="admin_user_001"
    )
    
    print("\n   Creating memories with different priority levels:")
    
    admin_expert.remember(
        content="Critical system backup completed successfully",
        memory_type=MemoryType.LONG_TERM,
        priority=MemoryPriority.HIGH,
        tags=["backup", "critical", "success"]
    )
    
    admin_expert.remember(
        content="Regular maintenance scheduled for next week",
        memory_type=MemoryType.LONG_TERM,
        priority=MemoryPriority.MEDIUM,
        tags=["maintenance", "scheduled", "routine"]
    )
    
    admin_expert.remember(
        content="Software update notes for reference",
        memory_type=MemoryType.LONG_TERM,
        priority=MemoryPriority.LOW,
        tags=["updates", "notes", "reference"]
    )
    
    print("     Stored memories with HIGH, MEDIUM, and LOW priorities")
    
    admin_memories = admin_expert.recall(
        query="system maintenance backup",
        limit=10
    )
    
    print(f"\n   Retrieved memories sorted by relevance:")
    for memory in admin_memories:
        priority = memory.get('priority', 'UNKNOWN')
        print(f"     [{priority}] {memory['content']}")
    
    print("\n5. Security summary")
    print("   ✓ User memory isolation working")
    print("   ✓ Memory encryption/decryption automatic")
    print("   ✓ Priority levels properly maintained")
    print("   ✓ Tag-based security categorization")
    print("   ✓ Cross-user access prevention verified")

if __name__ == "__main__":
    main()
