#!/usr/bin/env python3
"""
Product Launch Strategy Multi-Agent Team Example
===============================================
Advanced demonstration of comprehensive multi-agent framework features including:
- Multiple expert agents with specialized roles
- Complex operations with advanced guardrails
- Squad orchestration with hierarchical process
- Cross-operation context sharing and memory persistence
- Dynamic template variables and conditional logic
- Advanced security profiles and result destinations
- Real-world business workflow simulation
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tbh_secure_agents import Expert, Operation, Squad

# Set API key for testing
os.environ["GOOGLE_API_KEY"] = "AIzaSyBtIh9ShcSmezYKa8xmI0kIyyl2gJZIYFc"

def main():
    """
    Demonstrates a comprehensive Product Launch Strategy workflow with 5 experts:
    1. Market Research Analyst - Analyzes market conditions and opportunities
    2. Product Strategy Expert - Develops positioning and value propositions
    3. Marketing Campaign Manager - Creates marketing strategies and campaigns
    4. Sales Strategy Specialist - Develops sales approaches and tactics
    5. Launch Coordinator - Orchestrates timeline and execution plan
    
    Advanced Features Demonstrated:
    - Complex template variable systems with conditional logic
    - Advanced guardrails with multiple selection options
    - Cross-expert knowledge sharing through memory
    - Hierarchical operation dependencies
    - Multi-format result destinations
    - Security profiles with role-based access
    - Dynamic workflow adaptation based on inputs
    """
    
    # Create comprehensive outputs directory structure
    os.makedirs("outputs/product_launch", exist_ok=True)
    os.makedirs("outputs/product_launch/research", exist_ok=True)
    os.makedirs("outputs/product_launch/strategy", exist_ok=True)
    os.makedirs("outputs/product_launch/campaigns", exist_ok=True)
    os.makedirs("outputs/product_launch/execution", exist_ok=True)
    
    # 1. CREATE SPECIALIZED EXPERT AGENTS
    
    # Market Research Analyst with advanced template variables
    market_analyst = Expert(
        specialty="Market Research Analyst specializing in {market_sector} within {industry_vertical}",
        objective="Conduct comprehensive market analysis for {product_category} targeting {target_segments}",
        background="Expert in {research_methodologies} with {market_experience} years experience in {market_specialization}",
        security_profile="minimal",
        memory_duration="long_term",
        user_id="market_analyst_001"
    )
    
    # Product Strategy Expert
    product_strategist = Expert(
        specialty="Product Strategy Expert for {product_type} in {competitive_landscape}",
        objective="Develop positioning strategy for {product_name} with {differentiation_focus} approach",
        background="Strategic consultant with expertise in {strategy_domains} and {positioning_methodology}",
        security_profile="minimal",
        memory_duration="long_term",
        user_id="product_strategist_001"
    )
    
    # Marketing Campaign Manager
    marketing_manager = Expert(
        specialty="Marketing Campaign Manager for {marketing_channels} across {campaign_scope}",
        objective="Create integrated marketing strategy for {product_launch_type} leveraging {marketing_tactics}",
        background="Marketing expert specializing in {marketing_expertise} with {campaign_experience} track record",
        security_profile="minimal",
        memory_duration="long_term",
        user_id="marketing_manager_001"
    )
    
    # Sales Strategy Specialist
    sales_specialist = Expert(
        specialty="Sales Strategy Specialist for {sales_model} in {sales_channels}",
        objective="Develop sales approach for {revenue_targets} through {sales_methodology}",
        background="Sales strategist with expertise in {sales_expertise} and {deal_experience} experience",
        security_profile="minimal",
        memory_duration="long_term",
        user_id="sales_specialist_001"
    )
    
    # Launch Coordinator
    launch_coordinator = Expert(
        specialty="Launch Coordinator for {launch_complexity} projects in {project_environment}",
        objective="Orchestrate {launch_timeline} launch with {coordination_approach} methodology",
        background="Project management expert specializing in {pm_methodology} with {launch_experience}",
        security_profile="minimal",
        memory_duration="long_term",
        user_id="launch_coordinator_001"
    )
    
    # 2. CREATE COMPREHENSIVE OPERATIONS WITH ADVANCED GUARDRAILS
    
    # Market Research Operation
    market_research_operation = Operation(
        instructions="""
        Conduct comprehensive market research for {product_name} in the {industry_vertical} sector.
        
        Research Scope:
        {research_depth, select,
          market_overview: Focus on market size, growth trends, and key segments.|
          competitive_analysis: Deep dive into competitive landscape and positioning gaps.|
          customer_insights: Comprehensive customer needs analysis and buying behavior.|
          comprehensive: Complete analysis covering all aspects including market, competition, and customers.
        }
        
        Analysis Framework:
        - Market Size and Growth: {market_analysis_focus}
        - Customer Segmentation: {target_segments}
        - Competitive Landscape: {competitive_analysis_type}
        - Market Trends: {trend_analysis_scope}
        - Opportunity Assessment: {opportunity_focus}
        
        Research Methodologies: {research_methodologies}
        Data Sources: {data_sources}
        Geographic Scope: {geographic_scope}
        
        Deliverables:
        - Market sizing and growth projections
        - Customer persona development
        - Competitive positioning map
        - Market opportunity assessment
        - Risk and challenge analysis
        """,
        expected_output="Comprehensive market research report with actionable insights for {product_name}",
        expert=market_analyst,
        result_destination="outputs/product_launch/research/market_analysis.md"
    )
    
    # Product Strategy Operation
    product_strategy_operation = Operation(
        instructions="""
        Develop comprehensive product strategy for {product_name} based on market research insights.
        
        Strategy Development Framework:
        {strategy_approach, select,
          differentiation: Focus on unique value proposition and competitive differentiation.|
          market_penetration: Emphasize market entry and rapid adoption strategies.|
          innovation_leadership: Position as innovative solution with cutting-edge features.|
          value_optimization: Balance features, pricing, and market positioning for optimal value.
        }
        
        Strategic Components:
        - Value Proposition: {value_prop_focus}
        - Target Positioning: {positioning_strategy}
        - Differentiation Strategy: {differentiation_focus}
        - Pricing Framework: {pricing_approach}
        - Go-to-Market Approach: {gtm_strategy}
        
        Key Considerations:
        - Product Category: {product_category}
        - Competitive Context: {competitive_landscape}
        - Market Maturity: {market_maturity}
        - Customer Sophistication: {customer_sophistication}
        
        Integration Requirements:
        - Incorporate market research findings
        - Align with customer insights
        - Address competitive gaps identified
        - Consider resource and capability constraints
        """,
        expected_output="Strategic positioning framework with clear value proposition for {product_name}",
        expert=product_strategist,
        result_destination="outputs/product_launch/strategy/product_strategy.md"
    )
    
    # Marketing Campaign Operation
    marketing_campaign_operation = Operation(
        instructions="""
        Create integrated marketing campaign strategy for {product_name} launch.
        
        Campaign Strategy:
        {campaign_focus, select,
          awareness_building: Focus on brand awareness and market education.|
          demand_generation: Emphasize lead generation and conversion tactics.|
          thought_leadership: Position as industry innovator and expert solution.|
          integrated_approach: Comprehensive strategy combining awareness, demand, and thought leadership.
        }
        
        Marketing Mix:
        - Channels: {marketing_channels}
        - Messaging: {messaging_strategy}
        - Content Strategy: {content_approach}
        - Campaign Timeline: {campaign_timeline}
        - Budget Allocation: {budget_strategy}
        
        Tactical Execution:
        - Digital Marketing: {digital_tactics}
        - Traditional Marketing: {traditional_tactics}
        - Content Marketing: {content_tactics}
        - Event Marketing: {event_strategy}
        - Partnership Marketing: {partnership_approach}
        
        Success Metrics:
        - Awareness Metrics: {awareness_kpis}
        - Engagement Metrics: {engagement_kpis}
        - Conversion Metrics: {conversion_kpis}
        - Revenue Attribution: {attribution_model}
        
        Integration Points:
        - Align with product positioning strategy
        - Leverage market research insights
        - Coordinate with sales approach
        - Support launch timeline requirements
        """,
        expected_output="Integrated marketing campaign plan with tactical execution roadmap",
        expert=marketing_manager,
        result_destination="outputs/product_launch/campaigns/marketing_strategy.md"
    )
    
    # Sales Strategy Operation
    sales_strategy_operation = Operation(
        instructions="""
        Develop comprehensive sales strategy for {product_name} aligned with marketing and product positioning.
        
        Sales Approach:
        {sales_methodology, select,
          consultative_selling: Focus on customer needs analysis and solution selling.|
          relationship_building: Emphasize long-term relationships and account development.|
          value_selling: Concentrate on ROI demonstration and business value creation.|
          integrated_approach: Combine consultative, relationship, and value selling methodologies.
        }
        
        Sales Framework:
        - Sales Model: {sales_model}
        - Channel Strategy: {sales_channels}
        - Territory Planning: {territory_approach}
        - Account Segmentation: {account_strategy}
        - Revenue Targets: {revenue_targets}
        
        Sales Enablement:
        - Training Requirements: {training_needs}
        - Sales Tools: {sales_tools}
        - Collateral Needs: {sales_collateral}
        - CRM Configuration: {crm_requirements}
        - Competitive Intelligence: {competitive_intel}
        
        Performance Management:
        - Success Metrics: {sales_kpis}
        - Commission Structure: {compensation_model}
        - Performance Tracking: {tracking_methodology}
        - Pipeline Management: {pipeline_approach}
        
        Integration Requirements:
        - Align with marketing messaging and campaigns
        - Leverage product positioning and value proposition
        - Coordinate with launch timeline
        - Support market research insights
        """,
        expected_output="Comprehensive sales strategy with tactical implementation plan",
        expert=sales_specialist,
        result_destination="outputs/product_launch/strategy/sales_strategy.md"
    )
    
    # Launch Coordination Operation
    launch_coordination_operation = Operation(
        instructions="""
        Orchestrate comprehensive launch plan integrating all strategic components.
        
        Launch Management:
        {coordination_approach, select,
          phased_rollout: Structured phases with validation gates and iteration points.|
          big_bang_launch: Coordinated simultaneous launch across all channels and markets.|
          pilot_and_scale: Initial pilot with select customers followed by broader rollout.|
          market_by_market: Sequential geographic or segment-based launch progression.
        }
        
        Launch Orchestration:
        - Timeline Coordination: {launch_timeline}
        - Resource Allocation: {resource_planning}
        - Risk Management: {risk_mitigation}
        - Quality Assurance: {qa_approach}
        - Communication Plan: {communication_strategy}
        
        Cross-Functional Integration:
        - Product Readiness: {product_readiness_criteria}
        - Marketing Alignment: {marketing_coordination}
        - Sales Enablement: {sales_readiness}
        - Operations Readiness: {operational_readiness}
        - Support Infrastructure: {support_requirements}
        
        Success Management:
        - Launch Metrics: {launch_kpis}
        - Monitoring Dashboard: {monitoring_approach}
        - Escalation Procedures: {escalation_framework}
        - Continuous Improvement: {improvement_process}
        
        Integration Synthesis:
        - Synthesize market research findings
        - Integrate product strategy recommendations
        - Coordinate marketing campaign execution
        - Align sales strategy implementation
        - Ensure comprehensive launch readiness
        """,
        expected_output="Master launch plan with integrated timeline and execution framework",
        expert=launch_coordinator,
        result_destination="outputs/product_launch/execution/launch_plan.md"
    )
    
    # 3. CREATE SQUAD WITH SEQUENTIAL PROCESS
    
    product_launch_squad = Squad(
        experts=[market_analyst, product_strategist, marketing_manager, sales_specialist, launch_coordinator],
        operations=[
            market_research_operation,
            product_strategy_operation, 
            marketing_campaign_operation,
            sales_strategy_operation,
            launch_coordination_operation
        ],
        process="sequential",
        security_profile="minimal",
        result_destination="outputs/product_launch/master_launch_strategy.json"
    )
    
    # 4. DEFINE COMPREHENSIVE GUARDRAILS WITH ADVANCED VARIABLES
    
    guardrails = {
        # Product Configuration
        "product_name": "AI-Powered Inventory Optimization Platform",
        "product_type": "B2B SaaS solution",
        "product_category": "supply chain management software",
        
        # Market Configuration
        "industry_vertical": "retail and e-commerce",
        "market_sector": "enterprise software",
        "target_segments": "mid-market and enterprise retailers",
        "geographic_scope": "North American market with European expansion plans",
        "market_maturity": "growing market with increasing AI adoption",
        
        # Research Configuration
        "research_depth": "comprehensive",
        "research_methodologies": "quantitative analysis, customer interviews, and competitive intelligence",
        "data_sources": "industry reports, customer surveys, competitive analysis, and market databases",
        "market_analysis_focus": "total addressable market and growth projections",
        "competitive_analysis_type": "feature comparison and positioning analysis",
        "trend_analysis_scope": "AI adoption trends and supply chain digitization",
        "opportunity_focus": "market gaps and unmet customer needs",
        
        # Strategy Configuration
        "strategy_approach": "innovation_leadership",
        "value_prop_focus": "ROI-driven efficiency gains and predictive analytics",
        "positioning_strategy": "premium solution with proven results",
        "differentiation_focus": "AI-powered predictive capabilities and seamless integration",
        "pricing_approach": "value-based pricing with ROI guarantee",
        "gtm_strategy": "partner-enabled direct sales model",
        "competitive_landscape": "established players with legacy solutions",
        "customer_sophistication": "moderate to high technical sophistication",
        
        # Marketing Configuration
        "campaign_focus": "integrated_approach",
        "marketing_channels": "digital, content marketing, industry events, and partner channels",
        "messaging_strategy": "ROI-focused with customer success stories",
        "content_approach": "thought leadership and educational content",
        "campaign_timeline": "6-month integrated campaign",
        "budget_strategy": "70% digital, 20% events, 10% traditional",
        "digital_tactics": "SEO, PPC, social media, and webinar series",
        "traditional_tactics": "industry publications and trade shows",
        "content_tactics": "whitepapers, case studies, and video testimonials",
        "event_strategy": "speaking opportunities and sponsored events",
        "partnership_approach": "co-marketing with systems integrators",
        "awareness_kpis": "brand recognition and market share",
        "engagement_kpis": "content consumption and webinar attendance",
        "conversion_kpis": "lead quality and sales pipeline contribution",
        "attribution_model": "multi-touch attribution with sales influence",
        
        # Sales Configuration
        "sales_methodology": "integrated_approach",
        "sales_model": "inside sales with field support",
        "sales_channels": "direct sales, channel partners, and digital channels",
        "territory_approach": "geographic and vertical specialization",
        "account_strategy": "named account and territory models",
        "revenue_targets": "$10M ARR within 18 months",
        "training_needs": "product certification and consultative selling",
        "sales_tools": "CRM, sales enablement platform, and ROI calculators",
        "sales_collateral": "ROI studies, competitive battle cards, and demo scripts",
        "crm_requirements": "Salesforce integration with marketing automation",
        "competitive_intel": "real-time competitive tracking and positioning guides",
        "sales_kpis": "pipeline velocity, win rate, and deal size",
        "compensation_model": "base plus commission with accelerators",
        "tracking_methodology": "CRM-based with activity and outcome metrics",
        "pipeline_approach": "stage-gate methodology with conversion tracking",
        
        # Launch Configuration
        "coordination_approach": "phased_rollout",
        "launch_timeline": "6-month phased approach with 3 major milestones",
        "resource_planning": "cross-functional teams with dedicated launch resources",
        "risk_mitigation": "comprehensive risk register with mitigation plans",
        "qa_approach": "multi-stage validation including beta customer feedback",
        "communication_strategy": "stakeholder-specific communication plans",
        "product_readiness_criteria": "feature completeness, performance benchmarks, and security validation",
        "marketing_coordination": "synchronized campaign launch with product availability",
        "sales_readiness": "training completion, tool deployment, and territory assignment",
        "operational_readiness": "support infrastructure, billing systems, and customer onboarding",
        "support_requirements": "24/7 technical support and customer success programs",
        "launch_kpis": "adoption rate, customer satisfaction, and revenue generation",
        "monitoring_approach": "real-time dashboard with automated alerts",
        "escalation_framework": "defined escalation paths and response procedures",
        "improvement_process": "weekly reviews with continuous optimization",
        
        # Advanced Context Variables
        "market_experience": "15+",
        "market_specialization": "supply chain and retail technology",
        "strategy_domains": "B2B SaaS positioning and go-to-market strategy",
        "positioning_methodology": "competitive differentiation and value proposition development",
        "marketing_expertise": "B2B technology marketing and demand generation",
        "campaign_experience": "proven track record in enterprise software launches",
        "sales_expertise": "enterprise software sales and channel development",
        "deal_experience": "complex B2B sales cycles",
        "pm_methodology": "Agile project management with stage-gate reviews",
        "launch_experience": "multiple successful enterprise software launches",
        "launch_complexity": "multi-market enterprise software",
        "project_environment": "fast-paced technology company"
    }
    
    # 5. ADVANCED MEMORY INTEGRATION WITH CROSS-EXPERT KNOWLEDGE SHARING
    
    # Market Analyst Knowledge Base
    market_analyst.remember(
        content="Enterprise retailers typically see 15-25% inventory cost reduction with AI optimization",
        memory_type="LONG_TERM"
    )
    
    market_analyst.remember(
        content="Supply chain software market growing at 12% CAGR with AI adoption accelerating",
        memory_type="LONG_TERM"
    )
    
    # Product Strategist Knowledge Base
    product_strategist.remember(
        content="Successful B2B SaaS positioning requires clear ROI demonstration and integration simplicity",
        memory_type="WORKING"
    )
    
    product_strategist.remember(
        content="Enterprise software buyers prioritize proven results over cutting-edge features",
        memory_type="WORKING"
    )
    
    # Marketing Manager Knowledge Base
    marketing_manager.remember(
        content="B2B technology buyers consume average of 13 pieces of content before purchase decision",
        memory_type="LONG_TERM"
    )
    
    marketing_manager.remember(
        content="Webinar series and customer case studies drive highest quality leads for enterprise software",
        memory_type="WORKING"
    )
    
    # Sales Specialist Knowledge Base
    sales_specialist.remember(
        content="Enterprise software sales cycles average 9-12 months with multiple stakeholders",
        memory_type="LONG_TERM"
    )
    
    sales_specialist.remember(
        content="ROI-based selling with customer references reduces sales cycle by 30%",
        memory_type="WORKING"
    )
    
    # Launch Coordinator Knowledge Base
    launch_coordinator.remember(
        content="Successful enterprise software launches require 6-month preparation with phased rollout",
        memory_type="LONG_TERM"
    )
    
    launch_coordinator.remember(
        content="Customer success programs launched simultaneously with product improve retention by 40%",
        memory_type="WORKING"
    )
    
    # 6. EXECUTE COMPREHENSIVE PRODUCT LAUNCH WORKFLOW
    
    try:
        # Deploy the squad with comprehensive guardrails
        result = product_launch_squad.deploy(guardrails=guardrails)
        
        # Create summary of generated artifacts
        artifacts_summary = {
            "research_artifacts": [
                "outputs/product_launch/research/market_analysis.md"
            ],
            "strategy_artifacts": [
                "outputs/product_launch/strategy/product_strategy.md",
                "outputs/product_launch/strategy/sales_strategy.md"
            ],
            "campaign_artifacts": [
                "outputs/product_launch/campaigns/marketing_strategy.md"
            ],
            "execution_artifacts": [
                "outputs/product_launch/execution/launch_plan.md"
            ],
            "master_summary": [
                "outputs/product_launch/master_launch_strategy.json"
            ]
        }
        
        # Test comprehensive memory recall across all experts
        memory_insights = {}
        
        market_memories = market_analyst.recall("inventory AI retail", limit=2)
        memory_insights["market_analyst"] = [m.get('content', '')[:100] + "..." for m in market_memories]
        
        strategy_memories = product_strategist.recall("B2B SaaS positioning", limit=2)
        memory_insights["product_strategist"] = [m.get('content', '')[:100] + "..." for m in strategy_memories]
        
        marketing_memories = marketing_manager.recall("B2B technology content", limit=2)
        memory_insights["marketing_manager"] = [m.get('content', '')[:100] + "..." for m in marketing_memories]
        
        sales_memories = sales_specialist.recall("enterprise software sales", limit=2)
        memory_insights["sales_specialist"] = [m.get('content', '')[:100] + "..." for m in sales_memories]
        
        launch_memories = launch_coordinator.recall("enterprise software launch", limit=2)
        memory_insights["launch_coordinator"] = [m.get('content', '')[:100] + "..." for m in launch_memories]
        
        return {
            "status": "success",
            "squad_result": result[:500] + "..." if len(result) > 500 else result,
            "artifacts": artifacts_summary,
            "memory_insights": memory_insights,
            "features_demonstrated": [
                "5 specialized expert agents with advanced template variables",
                "Complex operations with conditional guardrails",
                "Sequential squad process with cross-operation context",
                "Comprehensive memory integration and recall",
                "Multi-format result destinations",
                "Advanced security profiles",
                "Real-world business workflow simulation",
                "Cross-expert knowledge sharing"
            ]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Error during comprehensive workflow execution"
        }

if __name__ == "__main__":
    result = main()
    
    if result["status"] == "success":
        print("🎉 COMPREHENSIVE PRODUCT LAUNCH STRATEGY COMPLETED!")
        print("=" * 60)
        print(f"✅ Squad Result: {result['squad_result']}")
        print()
        print("📁 Generated Artifacts:")
        for category, files in result["artifacts"].items():
            print(f"  {category}:")
            for file in files:
                print(f"    - {file}")
        print()
        print("🧠 Memory Insights:")
        for expert, insights in result["memory_insights"].items():
            print(f"  {expert}:")
            for insight in insights:
                print(f"    - {insight}")
        print()
        print("🚀 Framework Features Demonstrated:")
        for feature in result["features_demonstrated"]:
            print(f"  ✅ {feature}")
    else:
        print(f"❌ Error: {result['error']}")
        print(f"Message: {result['message']}")
