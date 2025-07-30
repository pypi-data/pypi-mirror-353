#!/usr/bin/env python3
"""
Memory Search Patterns Example
===============================
Demonstrates various search patterns and filtering options
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

os.environ["GOOGLE_API_KEY"] = "AIzaSyBtIh9ShcSmezYKa8xmI0kIyyl2gJZIYFc"

from tbh_secure_agents.agent import Expert
from tbh_secure_agents.memory.models import MemoryType, MemoryPriority

def setup_test_data(expert):
    """Create diverse test memories for search demonstrations"""
    
    memories = [
        {
            "content": "Python is a versatile programming language used for web development",
            "tags": ["python", "programming", "web_development"],
            "priority": MemoryPriority.HIGH
        },
        {
            "content": "Machine learning algorithms can predict customer behavior patterns",
            "tags": ["machine_learning", "algorithms", "customer_analysis"],
            "priority": MemoryPriority.HIGH
        },
        {
            "content": "Database optimization improved query performance by 40%",
            "tags": ["database", "optimization", "performance"],
            "priority": MemoryPriority.MEDIUM
        },
        {
            "content": "JavaScript frameworks like React are popular for frontend development",
            "tags": ["javascript", "react", "frontend"],
            "priority": MemoryPriority.MEDIUM
        },
        {
            "content": "Data science project completed with 95% accuracy rate",
            "tags": ["data_science", "project", "accuracy"],
            "priority": MemoryPriority.HIGH
        },
        {
            "content": "API security implemented using OAuth 2.0 authentication",
            "tags": ["API", "security", "oauth"],
            "priority": MemoryPriority.HIGH
        },
        {
            "content": "Cloud migration reduced infrastructure costs by 30%",
            "tags": ["cloud", "migration", "cost_reduction"],
            "priority": MemoryPriority.MEDIUM
        },
        {
            "content": "Team training session on agile methodologies scheduled",
            "tags": ["training", "agile", "team"],
            "priority": MemoryPriority.LOW
        }
    ]
    
    for memory_data in memories:
        expert.remember(
            content=memory_data["content"],
            memory_type=MemoryType.LONG_TERM,
            priority=memory_data["priority"],
            tags=memory_data["tags"]
        )
    
    print(f"   Created {len(memories)} test memories")

def main():
    expert = Expert(
        specialty="Technical Consultant",
        objective="Search and analyze technical information",
        memory_duration="long_term",
        user_id="search_patterns_demo"
    )
    
    print("1. Setting up test data")
    setup_test_data(expert)
    
    print("\n2. Semantic search patterns")
    
    print("\n   Programming-related search:")
    programming_results = expert.recall(
        query="programming languages development coding",
        limit=5
    )
    for memory in programming_results:
        print(f"     - {memory['content']}")
        print(f"       Relevance tags: {memory.get('tags', [])}")
    
    print("\n   Performance and optimization search:")
    performance_results = expert.recall(
        query="performance optimization efficiency improvements",
        limit=5
    )
    for memory in performance_results:
        print(f"     - {memory['content']}")
    
    print("\n   Technology stack search:")
    tech_results = expert.recall(
        query="technology frameworks tools platforms",
        limit=5
    )
    for memory in tech_results:
        print(f"     - {memory['content']}")
    
    print("\n3. Specific keyword searches")
    
    print("\n   Machine learning focused:")
    ml_results = expert.recall(
        query="machine learning algorithms AI",
        limit=3
    )
    for memory in ml_results:
        print(f"     - {memory['content']}")
    
    print("\n   Security focused:")
    security_results = expert.recall(
        query="security authentication protection",
        limit=3
    )
    for memory in security_results:
        print(f"     - {memory['content']}")
    
    print("\n4. Priority-based filtering demonstration")
    
    all_results = expert.recall(
        query="development technology project",
        limit=10
    )
    
    high_priority = [m for m in all_results if m.get('priority') == 'HIGH']
    medium_priority = [m for m in all_results if m.get('priority') == 'MEDIUM']
    low_priority = [m for m in all_results if m.get('priority') == 'LOW']
    
    print(f"\n   High priority memories ({len(high_priority)}):")
    for memory in high_priority:
        print(f"     - {memory['content']}")
    
    print(f"\n   Medium priority memories ({len(medium_priority)}):")
    for memory in medium_priority:
        print(f"     - {memory['content']}")
    
    print(f"\n   Low priority memories ({len(low_priority)}):")
    for memory in low_priority:
        print(f"     - {memory['content']}")
    
    print("\n5. Broad vs. specific searches")
    
    print("\n   Broad search (general terms):")
    broad_results = expert.recall(
        query="technology development",
        limit=5
    )
    print(f"     Found {len(broad_results)} results")
    
    print("\n   Specific search (detailed terms):")
    specific_results = expert.recall(
        query="React JavaScript frontend framework development",
        limit=5
    )
    print(f"     Found {len(specific_results)} results")
    for memory in specific_results:
        print(f"     - {memory['content']}")
    
    print("\n6. Tag-based categorization")
    
    all_memories = expert.recall(
        query="technology programming development project",
        limit=20
    )
    
    tag_categories = {}
    for memory in all_memories:
        tags = memory.get('tags', [])
        for tag in tags:
            if tag not in tag_categories:
                tag_categories[tag] = []
            tag_categories[tag].append(memory['content'][:50] + "...")
    
    print(f"\n   Memory categories by tags:")
    for tag, memories in tag_categories.items():
        print(f"     {tag}: {len(memories)} memories")
        for mem_content in memories[:2]:  # Show first 2 for each tag
            print(f"       - {mem_content}")

if __name__ == "__main__":
    main()
