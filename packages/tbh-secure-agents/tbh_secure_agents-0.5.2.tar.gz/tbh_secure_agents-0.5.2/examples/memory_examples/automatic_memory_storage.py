#!/usr/bin/env python3
"""
Automatic Memory Storage Example
================================
Demonstrates automatic memory storage during task execution
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

os.environ["GOOGLE_API_KEY"] = "AIzaSyBtIh9ShcSmezYKa8xmI0kIyyl2gJZIYFc"

from tbh_secure_agents.agent import Expert

def main():
    print("1. Testing automatic memory storage with different durations")
    
    long_term_expert = Expert(
        specialty="Research Analyst",
        objective="Conduct research and maintain knowledge base",
        memory_duration="long_term",
        user_id="researcher_auto"
    )
    
    print("\n   Long-term memory expert executing tasks...")
    
    result1 = long_term_expert.execute_task(
        "Research the benefits of renewable energy sources"
    )
    print(f"   Task 1 completed: {result1[:100]}...")
    
    result2 = long_term_expert.execute_task(
        "Analyze the economic impact of solar power adoption"
    )
    print(f"   Task 2 completed: {result2[:100]}...")
    
    print("\n2. Checking automatically stored memories")
    
    auto_memories = long_term_expert.recall(
        query="renewable energy solar power research",
        limit=10
    )
    print(f"   Found {len(auto_memories)} automatically stored memories:")
    for i, memory in enumerate(auto_memories, 1):
        print(f"     {i}. {memory['content'][:80]}...")
        print(f"        Type: {memory.get('memory_type')}")
        print(f"        Auto-stored: {memory.get('auto_stored', False)}")
    
    print("\n3. Testing session-level automatic storage")
    
    session_expert = Expert(
        specialty="Quick Assistant",
        objective="Provide immediate help",
        memory_duration="short_term",
        user_id="assistant_session"
    )
    
    session_result = session_expert.execute_task(
        "Provide a quick summary of machine learning basics"
    )
    print(f"   Session task completed: {session_result[:100]}...")
    
    session_memories = session_expert.recall(
        query="machine learning summary",
        limit=5
    )
    print(f"   Found {len(session_memories)} session memories:")
    for memory in session_memories:
        print(f"     - {memory['content'][:60]}...")
    
    print("\n4. Testing auto memory type")
    
    auto_expert = Expert(
        specialty="General Helper",
        objective="Assist with various tasks",
        memory_duration="auto",
        user_id="helper_auto"
    )
    
    auto_result = auto_expert.execute_task(
        "Explain the concept of artificial intelligence"
    )
    print(f"   Auto task completed: {auto_result[:100]}...")
    
    auto_memories = auto_expert.recall(
        query="artificial intelligence concept",
        limit=5
    )
    print(f"   Found {len(auto_memories)} auto-type memories:")
    for memory in auto_memories:
        print(f"     - {memory['content'][:60]}...")
        print(f"       Memory type: {memory.get('memory_type')}")

if __name__ == "__main__":
    main()
