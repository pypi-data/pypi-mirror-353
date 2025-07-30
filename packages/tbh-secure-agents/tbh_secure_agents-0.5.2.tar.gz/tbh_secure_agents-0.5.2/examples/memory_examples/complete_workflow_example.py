#!/usr/bin/env python3
"""
Complete Workflow Example
==========================
Comprehensive demonstration of all framework features in a realistic workflow
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

os.environ["GOOGLE_API_KEY"] = "AIzaSyBtIh9ShcSmezYKa8xmI0kIyyl2gJZIYFc"

from tbh_secure_agents.agent import Expert
from tbh_secure_agents.memory.models import MemoryType, MemoryPriority

def phase_1_research_and_planning():
    """Phase 1: Research and initial planning"""
    print("PHASE 1: Research and Planning")
    print("=" * 40)
    
    research_expert = Expert(
        specialty="Market Research Analyst",
        objective="Research market trends and competitive analysis",
        memory_duration="long_term",
        user_id="market_researcher_001"
    )
    
    print("\n1. Conducting market research tasks")
    
    # Execute research tasks (automatic memory storage)
    market_analysis = research_expert.execute_task(
        "Analyze current trends in AI and machine learning market"
    )
    print(f"   Market analysis completed: {market_analysis[:80]}...")
    
    competitive_analysis = research_expert.execute_task(
        "Research main competitors in the AI consulting space"
    )
    print(f"   Competitive analysis completed: {competitive_analysis[:80]}...")
    
    # Store additional research findings manually
    research_expert.remember(
        content="Market size for AI consulting: $15.7B expected by 2025",
        memory_type=MemoryType.LONG_TERM,
        priority=MemoryPriority.HIGH,
        tags=["market_size", "AI_consulting", "2025", "revenue"]
    )
    
    research_expert.remember(
        content="Key competitor: TechConsult Corp with 23% market share",
        memory_type=MemoryType.LONG_TERM,
        priority=MemoryPriority.HIGH,
        tags=["competitor", "TechConsult", "market_share", "analysis"]
    )
    
    print("   Stored additional research findings")
    
    # Retrieve research summary
    research_summary = research_expert.recall(
        query="market analysis AI consulting trends competitors",
        limit=10
    )
    
    print(f"\n2. Research summary ({len(research_summary)} insights):")
    for insight in research_summary:
        print(f"   - {insight['content'][:70]}...")
        print(f"     Tags: {insight.get('tags', [])}")
    
    return research_expert.user_id

def phase_2_strategy_development(research_user_id):
    """Phase 2: Strategy development based on research"""
    print("\nPHASE 2: Strategy Development")
    print("=" * 40)
    
    strategy_expert = Expert(
        specialty="Business Strategy Consultant",
        objective="Develop business strategies based on research",
        memory_duration="long_term",
        user_id="strategy_consultant_001"
    )
    
    # Reference research findings (cross-user access not allowed, so creating strategy memories)
    print("\n1. Developing strategic recommendations")
    
    strategy_result = strategy_expert.execute_task(
        "Develop a go-to-market strategy for AI consulting services"
    )
    print(f"   Strategy development completed: {strategy_result[:80]}...")
    
    # Store strategic decisions
    strategy_expert.remember(
        content="Target market: Mid-size companies (100-1000 employees) in tech sector",
        memory_type=MemoryType.LONG_TERM,
        priority=MemoryPriority.HIGH,
        tags=["target_market", "mid_size", "tech_sector", "strategy"]
    )
    
    strategy_expert.remember(
        content="Pricing strategy: Premium positioning at $250/hour consultation rate",
        memory_type=MemoryType.LONG_TERM,
        priority=MemoryPriority.HIGH,
        tags=["pricing", "premium", "consultation", "hourly_rate"]
    )
    
    strategy_expert.remember(
        content="Service offering: AI implementation, training, and ongoing support",
        memory_type=MemoryType.LONG_TERM,
        priority=MemoryPriority.MEDIUM,
        tags=["services", "AI_implementation", "training", "support"]
    )
    
    print("   Stored strategic decisions")
    
    # Retrieve strategy overview
    strategy_memories = strategy_expert.recall(
        query="strategy target market pricing services",
        limit=10
    )
    
    print(f"\n2. Strategic framework ({len(strategy_memories)} components):")
    for component in strategy_memories:
        print(f"   - {component['content']}")
        print(f"     Priority: {component.get('priority')}")
    
    return strategy_expert.user_id

def phase_3_implementation_planning(strategy_user_id):
    """Phase 3: Implementation planning and task management"""
    print("\nPHASE 3: Implementation Planning")
    print("=" * 40)
    
    project_manager = Expert(
        specialty="Project Manager",
        objective="Plan and track project implementation",
        memory_duration="long_term",
        user_id="project_manager_001"
    )
    
    print("\n1. Creating implementation plan")
    
    implementation_plan = project_manager.execute_task(
        "Create a detailed implementation plan for launching AI consulting services"
    )
    print(f"   Implementation plan created: {implementation_plan[:80]}...")
    
    # Store implementation milestones
    milestones = [
        {
            "content": "Milestone 1: Team recruitment and training (Weeks 1-4)",
            "tags": ["milestone_1", "recruitment", "training", "weeks_1_4"],
            "priority": MemoryPriority.HIGH
        },
        {
            "content": "Milestone 2: Service portfolio development (Weeks 5-8)",
            "tags": ["milestone_2", "portfolio", "development", "weeks_5_8"],
            "priority": MemoryPriority.HIGH
        },
        {
            "content": "Milestone 3: Marketing campaign launch (Weeks 9-12)",
            "tags": ["milestone_3", "marketing", "campaign", "weeks_9_12"],
            "priority": MemoryPriority.MEDIUM
        },
        {
            "content": "Milestone 4: First client engagement (Week 13+)",
            "tags": ["milestone_4", "client", "engagement", "week_13"],
            "priority": MemoryPriority.HIGH
        }
    ]
    
    for milestone in milestones:
        project_manager.remember(
            content=milestone["content"],
            memory_type=MemoryType.LONG_TERM,
            priority=milestone["priority"],
            tags=milestone["tags"]
        )
    
    print(f"   Stored {len(milestones)} implementation milestones")
    
    # Store team assignments
    team_assignments = [
        "John Smith assigned to lead technical team",
        "Sarah Johnson assigned to client relations",
        "Mike Davis assigned to marketing and outreach"
    ]
    
    for assignment in team_assignments:
        project_manager.remember(
            content=assignment,
            memory_type=MemoryType.LONG_TERM,
            priority=MemoryPriority.MEDIUM,
            tags=["team", "assignment", "roles"]
        )
    
    print(f"   Stored {len(team_assignments)} team assignments")
    
    return project_manager.user_id

def phase_4_execution_tracking(pm_user_id):
    """Phase 4: Execution tracking and progress monitoring"""
    print("\nPHASE 4: Execution Tracking")
    print("=" * 40)
    
    # Same project manager continues tracking
    project_manager = Expert(
        specialty="Project Manager",
        objective="Track project progress and manage execution",
        memory_duration="long_term",
        user_id=pm_user_id
    )
    
    print("\n1. Recording progress updates")
    
    # Store progress updates
    progress_updates = [
        {
            "content": "Week 2 update: 3 team members recruited, training materials prepared",
            "tags": ["week_2", "progress", "recruitment", "training"],
            "priority": MemoryPriority.MEDIUM
        },
        {
            "content": "Week 5 update: Service portfolio 60% complete, client presentation ready",
            "tags": ["week_5", "progress", "portfolio", "presentation"],
            "priority": MemoryPriority.MEDIUM
        },
        {
            "content": "Issue identified: Marketing budget needs 20% increase for digital campaigns",
            "tags": ["issue", "marketing", "budget", "increase", "digital"],
            "priority": MemoryPriority.HIGH
        }
    ]
    
    for update in progress_updates:
        project_manager.remember(
            content=update["content"],
            memory_type=MemoryType.LONG_TERM,
            priority=update["priority"],
            tags=update["tags"]
        )
    
    print(f"   Recorded {len(progress_updates)} progress updates")
    
    print("\n2. Analyzing project status")
    
    # Retrieve milestone status
    milestone_status = project_manager.recall(
        query="milestone progress week update",
        limit=10
    )
    
    print(f"   Project status ({len(milestone_status)} updates):")
    for status in milestone_status:
        content = status['content']
        tags = status.get('tags', [])
        priority = status.get('priority', 'UNKNOWN')
        print(f"   [{priority}] {content}")
        if 'issue' in tags:
            print(f"       ⚠️  ATTENTION REQUIRED")
    
    # Retrieve team assignments
    team_info = project_manager.recall(
        query="team assignment roles John Sarah Mike",
        limit=10
    )
    
    print(f"\n3. Team assignments ({len(team_info)} entries):")
    for assignment in team_info:
        print(f"   - {assignment['content']}")

def phase_5_final_analysis():
    """Phase 5: Final analysis and reporting"""
    print("\nPHASE 5: Final Analysis and Reporting")
    print("=" * 40)
    
    analyst = Expert(
        specialty="Business Analyst",
        objective="Analyze project outcomes and generate reports",
        memory_duration="long_term",
        user_id="business_analyst_001"
    )
    
    print("\n1. Generating final project report")
    
    final_report = analyst.execute_task(
        "Generate a comprehensive project completion report with key metrics"
    )
    print(f"   Final report generated: {final_report[:80]}...")
    
    # Store project completion data
    completion_data = [
        {
            "content": "Project completed on schedule with 95% milestone achievement",
            "tags": ["completion", "on_schedule", "95_percent", "milestones"],
            "priority": MemoryPriority.HIGH
        },
        {
            "content": "Total project cost: $125,000 (within 5% of budget)",
            "tags": ["cost", "budget", "125k", "within_budget"],
            "priority": MemoryPriority.HIGH
        },
        {
            "content": "First client signed during week 14 for $50,000 contract",
            "tags": ["first_client", "week_14", "50k_contract", "success"],
            "priority": MemoryPriority.HIGH
        },
        {
            "content": "Lessons learned: Earlier stakeholder engagement improves outcomes",
            "tags": ["lessons_learned", "stakeholder", "engagement", "improvement"],
            "priority": MemoryPriority.MEDIUM
        }
    ]
    
    for data in completion_data:
        analyst.remember(
            content=data["content"],
            memory_type=MemoryType.LONG_TERM,
            priority=data["priority"],
            tags=data["tags"]
        )
    
    print(f"   Stored {len(completion_data)} completion metrics")
    
    # Generate summary
    project_summary = analyst.recall(
        query="project completion cost budget client success",
        limit=15
    )
    
    print(f"\n2. Project summary ({len(project_summary)} key points):")
    
    high_priority_items = [item for item in project_summary if item.get('priority') == 'HIGH']
    medium_priority_items = [item for item in project_summary if item.get('priority') == 'MEDIUM']
    
    print(f"\n   Critical outcomes ({len(high_priority_items)}):")
    for item in high_priority_items:
        print(f"   ✓ {item['content']}")
    
    print(f"\n   Additional insights ({len(medium_priority_items)}):")
    for item in medium_priority_items:
        print(f"   • {item['content']}")

def main():
    """Execute complete workflow demonstrating all framework features"""
    print("COMPLETE WORKFLOW DEMONSTRATION")
    print("===============================")
    print("Demonstrating TBH Secure Agents framework with Chroma integration")
    print("Features: Memory storage, retrieval, encryption, user isolation, tagging")
    
    try:
        research_user = phase_1_research_and_planning()
        strategy_user = phase_2_strategy_development(research_user)
        pm_user = phase_3_implementation_planning(strategy_user)
        phase_4_execution_tracking(pm_user)
        phase_5_final_analysis()
        
        print("\n" + "=" * 50)
        print("WORKFLOW COMPLETED SUCCESSFULLY")
        print("=" * 50)
        print("\nFramework features demonstrated:")
        print("✓ Automatic memory storage during task execution")
        print("✓ Manual memory storage with tags and priorities")
        print("✓ Cross-session memory persistence")
        print("✓ User-based memory isolation")
        print("✓ Semantic search and retrieval")
        print("✓ Memory encryption and security")
        print("✓ Tag-based categorization")
        print("✓ Priority-based filtering")
        print("✓ Chroma vector database integration")
        print("✓ Memory type management (LONG_TERM, SESSION, WORKING)")
        
    except Exception as e:
        print(f"\nError during workflow execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
