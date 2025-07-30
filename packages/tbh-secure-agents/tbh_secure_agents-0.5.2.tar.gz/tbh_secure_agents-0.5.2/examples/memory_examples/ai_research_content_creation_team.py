#!/usr/bin/env python3
"""
AI Research & Content Creation Team Example
==========================================
Comprehensive demonstration of multi-agent framework features including:
- Expert agents with different specialties
- Squad orchestration with sequential process
- Operations with guardrails and result destinations  
- Context passing between operations
- Template variables for dynamic behavior
- Memory integration for knowledge retention
- Security profiles (minimal for examples)
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tbh_secure_agents import Expert, Operation, Squad

# Set API key for testing
# os.environ["GOOGLE_API_KEY"] = "your-api-key-here"

def main():
    """
    Demonstrates a realistic AI Research & Content Creation workflow with 3 experts:
    1. Research Specialist - Conducts thorough research
    2. Content Writer - Creates engaging content based on research
    3. Content Editor - Reviews and refines the final content
    
    Features demonstrated:
    - Template variables in expert profiles and operations
    - Guardrails for dynamic control
    - Sequential process with context passing
    - Result destinations for organized output
    - Memory integration for knowledge retention
    - Minimal security profile for development
    """
    
    # Create outputs directory
    os.makedirs("outputs/research_team", exist_ok=True)
    
    print("🚀 AI Research & Content Creation Team")
    print("=" * 50)
    print("Demonstrating comprehensive multi-agent framework features...")
    print()
    
    # 1. CREATE EXPERT AGENTS WITH TEMPLATE VARIABLES
    print("👥 Creating Expert Team Members...")
    
    # Research Specialist with template variables and memory
    research_specialist = Expert(
        specialty="Research Specialist in {research_domain}",
        objective="Conduct comprehensive research on {research_topic} focusing on {research_focus}",
        background="Expert researcher with access to {data_sources} and {research_depth} analysis capabilities",
        security_profile="minimal",  # Using minimal security for development
        memory_duration="long_term",  # Enable long-term memory
        user_id="research_specialist_001"
    )
    
    # Content Writer with template variables and memory
    content_writer = Expert(
        specialty="Content Writer specializing in {content_domain}",
        objective="Transform research into {content_type} for {target_audience}",
        background="Skilled at creating {writing_style} content with {content_approach} approach",
        security_profile="minimal",
        memory_duration="long_term",
        user_id="content_writer_001"
    )
    
    # Content Editor with template variables and memory
    content_editor = Expert(
        specialty="Content Editor specializing in {editing_domain}",
        objective="Review and enhance {content_type} ensuring {quality_standards}",
        background="Expert editor focusing on {editing_focus} with {editorial_approach} methodology",
        security_profile="minimal",
        memory_duration="long_term",
        user_id="content_editor_001"
    )
    
    print("✅ Created 3 expert agents with memory and template variables")
    print()
    
    # 2. CREATE OPERATIONS WITH GUARDRAILS AND RESULT DESTINATIONS
    print("📋 Setting up Operations with Guardrails...")
    
    # Research Operation with comprehensive guardrails
    research_operation = Operation(
        instructions="""
        Conduct thorough research on {research_topic} in the {research_domain} field.
        
        Research Requirements:
        {research_depth, select,
          basic: Provide a foundational overview with key concepts and current state.|
          comprehensive: Conduct deep analysis including trends, challenges, opportunities, and expert perspectives.|
          expert: Perform exhaustive research with technical details, case studies, and future projections.
        }
        
        Focus Areas:
        - {research_focus}
        - Current market trends and statistics
        - Key players and innovations
        - Challenges and opportunities
        - Future outlook and predictions
        
        Data Sources: {data_sources}
        Analysis Style: {research_style}
        Target Depth: {research_depth}
        
        Ensure all information is accurate, well-sourced, and relevant to {target_audience}.
        """,
        expected_output="Comprehensive research analysis on {research_topic}",
        expert=research_specialist,
        result_destination="outputs/research_team/01_research_analysis.md"
    )
    
    # Writing Operation that builds on research context
    writing_operation = Operation(
        instructions="""
        Create a compelling {content_type} based on the research findings provided.
        
        Content Requirements:
        {content_style, select,
          informative: Focus on clear, factual presentation with educational value.|
          engaging: Balance information with storytelling and reader engagement.|
          professional: Maintain formal tone suitable for business audiences.
        }
        
        Structure:
        - Compelling introduction that hooks the reader
        - Well-organized main content with clear sections
        - Data and insights from the research
        - Practical implications and recommendations
        - Strong conclusion with key takeaways
        
        Writing Guidelines:
        - Target Audience: {target_audience}
        - Writing Style: {writing_style}
        - Content Length: {content_length}
        - Tone: {content_tone}
        - Include specific data and examples from research
        
        Ensure the content is {content_approach} and meets {quality_standards}.
        """,
        expected_output="Well-structured {content_type} about {research_topic}",
        expert=content_writer,
        result_destination="outputs/research_team/02_content_draft.md"
    )
    
    # Editing Operation for final refinement
    editing_operation = Operation(
        instructions="""
        Review and enhance the provided {content_type} to ensure exceptional quality.
        
        Editorial Focus Areas:
        {editing_focus, select,
          clarity: Improve readability, flow, and comprehension.|
          engagement: Enhance reader engagement and content appeal.|
          accuracy: Verify facts, improve precision, and ensure credibility.|
          comprehensive: Address all aspects including clarity, engagement, and accuracy.
        }
        
        Quality Standards to Apply:
        - {quality_standards}
        - Ensure consistent tone and style
        - Verify all facts and data accuracy
        - Improve clarity and readability
        - Enhance overall impact and engagement
        
        Editorial Approach: {editorial_approach}
        Target Audience: {target_audience}
        Content Type: {content_type}
        
        Provide the polished final version with any significant improvements noted.
        """,
        expected_output="Polished and refined {content_type} ready for publication",
        expert=content_editor,
        result_destination="outputs/research_team/03_final_content.md"
    )
    
    print("✅ Created 3 operations with guardrails and result destinations")
    print()
    
    # 3. CREATE SQUAD WITH SEQUENTIAL PROCESS
    print("🤝 Creating Research Team Squad...")
    
    research_team_squad = Squad(
        experts=[research_specialist, content_writer, content_editor],
        operations=[research_operation, writing_operation, editing_operation],
        process="sequential",  # Sequential process enables context passing
        security_profile="minimal",  # Minimal security for development
        result_destination="outputs/research_team/team_workflow_summary.json"
    )
    
    print("✅ Squad created with sequential process and context passing")
    print()
    
    # 4. DEFINE COMPREHENSIVE GUARDRAILS
    print("🛡️  Setting up Comprehensive Guardrails...")
    
    guardrails = {
        # Research Configuration
        "research_topic": "AI-powered customer service automation",
        "research_domain": "business technology",
        "research_focus": "ROI analysis and implementation best practices",
        "research_depth": "comprehensive",
        "research_style": "data-driven with practical insights",
        "data_sources": "industry reports, case studies, and expert analysis",
        
        # Content Configuration
        "content_type": "strategic implementation guide",
        "content_domain": "business technology strategy",
        "content_style": "engaging",
        "content_approach": "actionable and practical",
        "content_length": "3000-4000 words",
        "content_tone": "professional yet accessible",
        "writing_style": "clear and engaging",
        
        # Editorial Configuration
        "editing_domain": "business content",
        "editing_focus": "comprehensive",
        "editorial_approach": "thorough and systematic",
        "quality_standards": "publication-ready with clear structure and compelling narrative",
        
        # Audience and Context
        "target_audience": "C-level executives and IT decision makers",
        
        # Advanced template variables for dynamic behavior
        "urgency_level": "standard",
        "complexity_preference": "balanced",
        "example_preference": "real-world case studies"
    }
    
    print("✅ Comprehensive guardrails configured with template variables")
    print()
    
    # 5. DEMONSTRATE MEMORY INTEGRATION
    print("🧠 Demonstrating Memory Integration...")
    
    # Store some contextual knowledge for the research specialist
    print("📝 Storing contextual knowledge in expert memories...")
    
    # FIXED: Remove the 'tags' parameter which is not supported
    research_specialist.remember(
        content="AI customer service automation ROI typically ranges 200-400% within first year",
        memory_type="LONG_TERM"
    )
    
    research_specialist.remember(
        content="Key implementation challenges include data integration, staff training, and customer adoption",
        memory_type="LONG_TERM"
    )
    
    content_writer.remember(
        content="Business executives prefer content that balances technical details with strategic implications",
        memory_type="WORKING"
    )
    
    content_writer.remember(
        content="Most effective business content includes concrete ROI data and implementation timelines",
        memory_type="WORKING"
    )
    
    print("✅ Successfully stored contextual knowledge in expert memories")
    print()
    
    # 6. EXECUTE THE RESEARCH TEAM WORKFLOW
    print("🚀 Executing Research Team Workflow...")
    print("This demonstrates sequential operations with context passing...")
    print()
    
    try:
        # Deploy the squad with guardrails
        result = research_team_squad.deploy(guardrails=guardrails)
        
        print("=" * 60)
        print("🎉 WORKFLOW EXECUTION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print()
        print("📊 Results Summary:")
        print(f"- Squad Result: {result[:200]}..." if len(result) > 200 else f"- Squad Result: {result}")
        print()
        print("📁 Generated Files:")
        print("- outputs/research_team/01_research_analysis.md")
        print("- outputs/research_team/02_content_draft.md") 
        print("- outputs/research_team/03_final_content.md")
        print("- outputs/research_team/team_workflow_summary.json")
        print()
        
        # 7. DEMONSTRATE MEMORY RECALL
        print("🔍 Demonstrating Memory Recall...")
        
        # Test memory recall from research specialist
        print("💡 Research Specialist recalling ROI information:")
        roi_memories = research_specialist.recall("ROI customer service", limit=3)
        for i, memory in enumerate(roi_memories, 1):
            print(f"   {i}. {memory.get('content', 'No content')[:100]}...")
        
        print()
        print("✏️  Content Writer recalling writing preferences:")
        writing_memories = content_writer.recall("business content executives", limit=2)
        for i, memory in enumerate(writing_memories, 1):
            print(f"   {i}. {memory.get('content', 'No content')[:100]}...")
        
        print()
        print("🎯 Framework Features Successfully Demonstrated:")
        print("   ✅ Expert agents with template variables")
        print("   ✅ Operations with guardrails and result destinations")
        print("   ✅ Squad orchestration with sequential processing")
        print("   ✅ Context passing between operations")
        print("   ✅ Memory integration (storage and recall)")
        print("   ✅ Security profiles (minimal for development)")
        print("   ✅ Dynamic template variable substitution")
        print("   ✅ File output generation")
        
    except Exception as e:
        print(f"❌ Error during workflow execution: {e}")
        print("This could be due to API key issues, network connectivity, or framework configuration.")
        print("Check the logs above for more detailed error information.")

if __name__ == "__main__":
    main()
