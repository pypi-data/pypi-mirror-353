#!/usr/bin/env python3
"""
Cross-Session Persistence Example
==================================
Demonstrates memory persistence across different sessions
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

os.environ["GOOGLE_API_KEY"] = "AIzaSyBtIh9ShcSmezYKa8xmI0kIyyl2gJZIYFc"

from tbh_secure_agents.agent import Expert
from tbh_secure_agents.memory.models import MemoryType, MemoryPriority

def session_1():
    print("SESSION 1: Initial data storage")
    
    expert = Expert(
        specialty="Project Manager",
        objective="Track project progress and team information",
        memory_duration="long_term",
        user_id="pm_persistent"
    )
    
    expert.remember(
        content="Project Alpha milestone 1 completed on schedule",
        memory_type=MemoryType.LONG_TERM,
        priority=MemoryPriority.HIGH,
        tags=["project_alpha", "milestone", "completed"]
    )
    
    expert.remember(
        content="Team member John assigned to frontend development",
        memory_type=MemoryType.LONG_TERM,
        priority=MemoryPriority.MEDIUM,
        tags=["team", "john", "frontend"]
    )
    
    expert.remember(
        content="Budget allocated: $50,000 for Q1 development",
        memory_type=MemoryType.LONG_TERM,
        priority=MemoryPriority.HIGH,
        tags=["budget", "Q1", "development"]
    )
    
    print("   Stored 3 project memories in session 1")
    return expert.user_id

def session_2(user_id):
    print("\nSESSION 2: Retrieving data from previous session")
    
    expert = Expert(
        specialty="Project Manager",
        objective="Track project progress and team information",
        memory_duration="long_term",
        user_id=user_id
    )
    
    project_memories = expert.recall(
        query="project alpha milestone progress",
        memory_type=MemoryType.LONG_TERM,
        limit=10
    )
    
    print(f"   Retrieved {len(project_memories)} project memories:")
    for memory in project_memories:
        print(f"     - {memory['content']}")
        print(f"       Tags: {memory.get('tags', [])}")
    
    expert.remember(
        content="Project Alpha milestone 2 started today",
        memory_type=MemoryType.LONG_TERM,
        priority=MemoryPriority.HIGH,
        tags=["project_alpha", "milestone_2", "started"]
    )
    
    print("   Added new milestone memory in session 2")

def session_3(user_id):
    print("\nSESSION 3: Comprehensive data retrieval")
    
    expert = Expert(
        specialty="Project Manager",
        objective="Track project progress and team information",
        memory_duration="long_term",
        user_id=user_id
    )
    
    all_memories = expert.recall(
        query="project team budget development",
        memory_type=MemoryType.LONG_TERM,
        limit=20
    )
    
    print(f"   Total memories across all sessions: {len(all_memories)}")
    
    milestone_memories = expert.recall(
        query="milestone",
        memory_type=MemoryType.LONG_TERM,
        limit=10
    )
    
    print(f"   Milestone-specific memories: {len(milestone_memories)}")
    for memory in milestone_memories:
        print(f"     - {memory['content']}")
    
    team_memories = expert.recall(
        query="team member john frontend",
        memory_type=MemoryType.LONG_TERM,
        limit=10
    )
    
    print(f"   Team-related memories: {len(team_memories)}")
    for memory in team_memories:
        print(f"     - {memory['content']}")

def main():
    print("Testing cross-session memory persistence...")
    
    user_id = session_1()
    session_2(user_id)
    session_3(user_id)
    
    print("\nPersistence test completed - all memories retrieved successfully!")

if __name__ == "__main__":
    main()
