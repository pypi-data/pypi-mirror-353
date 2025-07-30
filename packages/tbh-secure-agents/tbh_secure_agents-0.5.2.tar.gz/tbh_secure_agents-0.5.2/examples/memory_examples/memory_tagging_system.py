#!/usr/bin/env python3
"""
Memory Tagging System Example
==============================
Demonstrates memory tagging and categorization features
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

os.environ["GOOGLE_API_KEY"] = "AIzaSyBtIh9ShcSmezYKa8xmI0kIyyl2gJZIYFc"

from tbh_secure_agents.agent import Expert
from tbh_secure_agents.memory.models import MemoryType, MemoryPriority

def main():
    expert = Expert(
        specialty="Knowledge Manager",
        objective="Organize and categorize information",
        memory_duration="long_term",
        user_id="knowledge_manager_001"
    )
    
    print("1. Creating memories with diverse tag categories")
    
    tagged_memories = [
        {
            "content": "Quarterly sales report shows 25% increase",
            "tags": ["sales", "report", "Q1_2025", "performance", "metrics"],
            "priority": MemoryPriority.HIGH
        },
        {
            "content": "New Python library for data analysis released",
            "tags": ["python", "library", "data_analysis", "tools", "development"],
            "priority": MemoryPriority.MEDIUM
        },
        {
            "content": "Team meeting scheduled for project planning",
            "tags": ["meeting", "team", "planning", "project", "schedule"],
            "priority": MemoryPriority.MEDIUM
        },
        {
            "content": "Customer feedback: UI improvements needed",
            "tags": ["customer", "feedback", "UI", "improvements", "product"],
            "priority": MemoryPriority.HIGH
        },
        {
            "content": "Security audit completed with no issues",
            "tags": ["security", "audit", "completed", "compliance", "clean"],
            "priority": MemoryPriority.HIGH
        },
        {
            "content": "Training materials updated for new employees",
            "tags": ["training", "materials", "employees", "onboarding", "HR"],
            "priority": MemoryPriority.LOW
        },
        {
            "content": "Database backup procedure documented",
            "tags": ["database", "backup", "procedure", "documentation", "IT"],
            "priority": MemoryPriority.MEDIUM
        },
        {
            "content": "Budget approval received for Q2 initiatives",
            "tags": ["budget", "approval", "Q2_2025", "initiatives", "finance"],
            "priority": MemoryPriority.HIGH
        }
    ]
    
    for memory_data in tagged_memories:
        expert.remember(
            content=memory_data["content"],
            memory_type=MemoryType.LONG_TERM,
            priority=memory_data["priority"],
            tags=memory_data["tags"]
        )
    
    print(f"   Created {len(tagged_memories)} tagged memories")
    
    print("\n2. Tag-based memory retrieval")
    
    print("\n   Finance and budget related:")
    finance_memories = expert.recall(
        query="budget finance sales revenue",
        limit=10
    )
    finance_tags = set()
    for memory in finance_memories:
        print(f"     - {memory['content']}")
        finance_tags.update(memory.get('tags', []))
    print(f"     Related tags: {sorted(list(finance_tags))}")
    
    print("\n   Technology and development:")
    tech_memories = expert.recall(
        query="python development tools library database",
        limit=10
    )
    tech_tags = set()
    for memory in tech_memories:
        print(f"     - {memory['content']}")
        tech_tags.update(memory.get('tags', []))
    print(f"     Related tags: {sorted(list(tech_tags))}")
    
    print("\n   Team and HR activities:")
    team_memories = expert.recall(
        query="team meeting training employees HR",
        limit=10
    )
    team_tags = set()
    for memory in team_memories:
        print(f"     - {memory['content']}")
        team_tags.update(memory.get('tags', []))
    print(f"     Related tags: {sorted(list(team_tags))}")
    
    print("\n3. Tag frequency analysis")
    
    all_memories = expert.recall(
        query="business operations technology team",
        limit=20
    )
    
    tag_frequency = {}
    for memory in all_memories:
        tags = memory.get('tags', [])
        for tag in tags:
            tag_frequency[tag] = tag_frequency.get(tag, 0) + 1
    
    sorted_tags = sorted(tag_frequency.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n   Tag frequency across {len(all_memories)} memories:")
    for tag, count in sorted_tags:
        print(f"     {tag}: {count} occurrences")
    
    print("\n4. Category-based organization")
    
    categories = {
        "Business & Finance": ["sales", "budget", "finance", "revenue", "performance"],
        "Technology & Development": ["python", "development", "tools", "database", "IT"],
        "Team & Human Resources": ["team", "meeting", "training", "employees", "HR"],
        "Security & Compliance": ["security", "audit", "compliance", "procedure"],
        "Product & Customer": ["customer", "feedback", "product", "UI", "improvements"]
    }
    
    print(f"\n   Organizing memories by categories:")
    
    for category, category_tags in categories.items():
        category_query = " ".join(category_tags)
        category_memories = expert.recall(
            query=category_query,
            limit=10
        )
        
        # Filter memories that actually contain category tags
        relevant_memories = []
        for memory in category_memories:
            memory_tags = memory.get('tags', [])
            if any(tag in memory_tags for tag in category_tags):
                relevant_memories.append(memory)
        
        print(f"\n     {category} ({len(relevant_memories)} memories):")
        for memory in relevant_memories:
            matching_tags = [tag for tag in memory.get('tags', []) if tag in category_tags]
            print(f"       - {memory['content']}")
            print(f"         Matching tags: {matching_tags}")
    
    print("\n5. Advanced tag combinations")
    
    print("\n   High priority AND Q1/Q2 related:")
    quarterly_memories = expert.recall(
        query="Q1 Q2 2025 quarterly important",
        limit=10
    )
    
    high_priority_quarterly = [
        m for m in quarterly_memories 
        if m.get('priority') == 'HIGH' and 
        any(tag in ['Q1_2025', 'Q2_2025'] for tag in m.get('tags', []))
    ]
    
    print(f"     Found {len(high_priority_quarterly)} high-priority quarterly memories:")
    for memory in high_priority_quarterly:
        print(f"       - {memory['content']}")
        print(f"         Tags: {memory.get('tags', [])}")
    
    print("\n   Cross-category memories (multiple departments):")
    cross_category_memories = expert.recall(
        query="team security development finance",
        limit=10
    )
    
    for memory in cross_category_memories:
        tags = memory.get('tags', [])
        categories_found = []
        for category, category_tags in categories.items():
            if any(tag in tags for tag in category_tags):
                categories_found.append(category)
        
        if len(categories_found) > 1:
            print(f"       - {memory['content']}")
            print(f"         Spans categories: {categories_found}")

if __name__ == "__main__":
    main()
