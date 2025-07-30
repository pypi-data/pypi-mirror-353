#!/usr/bin/env python3
"""
Marketing Campaign Squad Example
===============================
Comprehensive demonstration of multi-agent framework features including:
- Expert agents with marketing specialties
- Squad orchestration with campaign development process
- Operations with conditional guardrails for different campaign types
- Template variables for dynamic marketing strategies
- Memory integration for brand knowledge retention
- Security profiles (minimal for examples)
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tbh_secure_agents import Expert, Operation, Squad

# Set API key for testing
os.environ["GOOGLE_API_KEY"] = "AIzaSyBtIh9ShcSmezYKa8xmI0kIyyl2gJZIYFc"

def main():
    """
    Demonstrates a realistic Marketing Campaign workflow with 3 experts:
    1. Marketing Strategist - Develops campaign strategy and positioning
    2. Content Creator - Creates marketing content and creative assets
    3. Campaign Analyst - Analyzes performance and optimizes campaigns
    
    Features demonstrated:
    - Conditional guardrails for different campaign types and channels
    - Template variables for various marketing scenarios
    - Sequential campaign development with context passing
    - Multiple output formats for different marketing assets
    - Memory integration for brand knowledge accumulation
    - Professional marketing campaign workflow
    """
    
    # Create outputs directory
    os.makedirs("outputs/marketing_campaign", exist_ok=True)
    
    print("📢 Marketing Campaign Squad")
    print("=" * 35)
    print("Demonstrating integrated marketing campaign development...")
    print()
    
    # 1. CREATE MARKETING EXPERTS
    print("🎯 Creating Marketing Team...")
    
    # Marketing Strategist with strategy template variables
    marketing_strategist = Expert(
        specialty="Marketing Strategist specializing in {marketing_domain}",
        objective="Develop {campaign_type} strategies for {target_market} using {marketing_channels}",
        background="Expert in {strategy_methodology} with {marketing_experience} and {brand_expertise}",
        security_profile="minimal",
        memory_duration="long_term",
        user_id="marketing_strategist_001"
    )
    
    # Content Creator with creative template variables
    content_creator = Expert(
        specialty="Content Creator expert in {content_domain}",
        objective="Create {content_type} for {audience_segment} across {distribution_channels}",
        background="Creative expert with {creative_expertise} and {content_approach} methodology",
        security_profile="minimal",
        memory_duration="long_term",
        user_id="content_creator_001"
    )
    
    # Campaign Analyst with analytics template variables
    campaign_analyst = Expert(
        specialty="Campaign Analyst specializing in {analytics_domain}",
        objective="Analyze {campaign_performance} and optimize {marketing_metrics} using {analytics_tools}",
        background="Data-driven marketer with {analytics_expertise} and {optimization_methodology}",
        security_profile="minimal",
        memory_duration="long_term",
        user_id="campaign_analyst_001"
    )
    
    print("✅ Created marketing team with memory and specializations")
    print()
    
    # 2. CREATE MARKETING OPERATIONS WITH CONDITIONAL GUARDRAILS
    print("📈 Setting up Marketing Operations...")
    
    # Strategy Development Operation with campaign type conditions
    strategy_operation = Operation(
        instructions="""
        Develop comprehensive marketing strategy for {campaign_objective} targeting {target_market}.
        
        Campaign Strategy Framework:
        {campaign_type, select,
          brand_awareness: Focus on brand visibility, reach, and recognition across target audiences.|
          lead_generation: Emphasize conversion optimization, lead capture, and sales funnel development.|
          product_launch: Create launch strategy with market introduction and adoption tactics.|
          retention: Develop customer loyalty and retention strategies for existing customers.
        }
        
        Strategic Components:
        - Target Market Analysis: {target_market}
        - Marketing Channels: {marketing_channels}
        - Budget Allocation: {budget_strategy}
        - Timeline: {campaign_timeline}
        - Success Metrics: {success_metrics}
        
        {audience_approach, select,
          demographic: Target based on age, income, education, and geographic factors.|
          psychographic: Focus on lifestyle, values, interests, and personality traits.|
          behavioral: Target based on purchasing behavior, brand loyalty, and usage patterns.|
          comprehensive: Integrate demographic, psychographic, and behavioral targeting.
        }
        
        Marketing Strategy Elements:
        - Positioning and messaging strategy
        - Channel mix and media planning
        - Creative direction and brand guidelines
        - Competitive differentiation approach
        - Customer journey and touchpoint mapping
        
        Marketing Domain: {marketing_domain}
        Strategy Methodology: {strategy_methodology}
        Brand Expertise: {brand_expertise}
        
        {competitive_positioning, select,
          challenger: Position as innovative alternative to market leaders.|
          leader: Reinforce market leadership and premium positioning.|
          niche: Focus on specialized market segment with unique value proposition.|
          follower: Competitive pricing and feature parity with market leaders.
        }
        
        Ensure strategy aligns with {business_objectives} and brand identity.
        """,
        expected_output="Comprehensive marketing strategy for {campaign_objective}",
        expert=marketing_strategist,
        result_destination={
            "format": "md",
            "file_path": "outputs/marketing_campaign/01_marketing_strategy.md"
        }
    )
    
    # Content Creation Operation
    content_creation_operation = Operation(
        instructions="""
        Create compelling marketing content based on the strategic framework provided.
        
        Content Development Framework:
        {content_approach, select,
          informational: Educational content that builds trust and expertise.|
          emotional: Engaging content that creates emotional connection with audience.|
          promotional: Direct response content focused on conversions and sales.|
          storytelling: Narrative-driven content that builds brand affinity and engagement.
        }
        
        Content Requirements:
        - Content Type: {content_type}
        - Target Audience: {audience_segment}
        - Distribution Channels: {distribution_channels}
        - Brand Voice: {brand_voice}
        - Content Goals: {content_objectives}
        
        {format_optimization, select,
          social_media: Optimize for engagement, shares, and social platform algorithms.|
          website: Focus on SEO optimization, user experience, and conversion paths.|
          email: Personalized messaging with clear calls-to-action and segmentation.|
          video: Visual storytelling with platform-specific optimization and engagement.
        }
        
        Creative Elements:
        - Headlines and messaging hierarchy
        - Visual direction and design concepts
        - Call-to-action optimization
        - Brand consistency and guidelines
        - Multi-channel content adaptation
        
        Content Domain: {content_domain}
        Creative Expertise: {creative_expertise}
        Content Methodology: {content_approach}
        
        {personalization_level, select,
          basic: Generic content suitable for broad audience segments.|
          targeted: Customized content for specific audience demographics and interests.|
          dynamic: Personalized content based on individual behavior and preferences.|
          automated: AI-driven content personalization with real-time optimization.
        }
        
        Ensure content supports {campaign_objective} and drives {success_metrics}.
        """,
        expected_output="Complete content package for {campaign_type} campaign",
        expert=content_creator,
        result_destination={
            "format": "md",
            "file_path": "outputs/marketing_campaign/02_content_assets.md"
        }
    )
    
    # Campaign Analysis Operation
    analysis_operation = Operation(
        instructions="""
        Analyze campaign performance and provide optimization recommendations.
        
        Analytics Framework:
        {analytics_approach, select,
          descriptive: Analyze what happened with historical performance data.|
          diagnostic: Understand why certain results occurred and identify root causes.|
          predictive: Forecast future performance based on current trends and data.|
          prescriptive: Recommend specific actions for campaign optimization.
        }
        
        Performance Analysis:
        - Campaign Performance: {campaign_performance}
        - Marketing Metrics: {marketing_metrics}
        - Analytics Tools: {analytics_tools}
        - ROI Analysis: {roi_measurement}
        - Attribution Modeling: {attribution_method}
        
        {optimization_focus, select,
          conversion: Optimize for lead generation and sales conversion rates.|
          engagement: Focus on audience engagement, interaction, and brand affinity.|
          reach: Maximize audience reach and brand awareness metrics.|
          efficiency: Optimize cost-effectiveness and return on marketing investment.
        }
        
        Analysis Components:
        - Performance dashboard and KPI tracking
        - Audience behavior and engagement analysis
        - Channel effectiveness and attribution
        - Competitive benchmarking and market share
        - Optimization recommendations and action items
        
        Analytics Domain: {analytics_domain}
        Analytics Expertise: {analytics_expertise}
        Optimization Methodology: {optimization_methodology}
        
        {reporting_frequency, select,
          real_time: Continuous monitoring with automated alerts and updates.|
          daily: Daily performance reports for active campaign management.|
          weekly: Weekly analysis for tactical optimization and adjustments.|
          monthly: Monthly strategic review for campaign planning and budget allocation.
        }
        
        Provide actionable insights that improve {success_metrics} and {campaign_objective}.
        """,
        expected_output="Comprehensive campaign analysis with optimization recommendations",
        expert=campaign_analyst,
        result_destination={
            "format": "html",
            "file_path": "outputs/marketing_campaign/03_campaign_analysis.html"
        }
    )
    
    print("✅ Created marketing operations with conditional logic")
    print()
    
    # 3. CREATE MARKETING CAMPAIGN SQUAD
    print("🎯 Assembling Marketing Squad...")
    
    marketing_squad = Squad(
        experts=[marketing_strategist, content_creator, campaign_analyst],
        operations=[strategy_operation, content_creation_operation, analysis_operation],
        process="sequential",
        security_profile="minimal",
        result_destination={
            "format": "json",
            "file_path": "outputs/marketing_campaign/campaign_deliverables.json"
        }
    )
    
    print("✅ Marketing squad assembled with integrated workflow")
    print()
    
    # 4. COMPREHENSIVE GUARDRAILS FOR MARKETING CAMPAIGN
    print("🛡️ Configuring Marketing Guardrails...")
    
    guardrails = {
        # Marketing Strategist Configuration
        "marketing_domain": "digital marketing and brand strategy",
        "campaign_type": "product_launch",
        "target_market": "tech-savvy millennials and Gen Z consumers",
        "marketing_channels": "social media, influencer partnerships, and content marketing",
        "strategy_methodology": "data-driven marketing with agile campaign optimization",
        "marketing_experience": "B2C technology product marketing",
        "brand_expertise": "startup brand development and growth marketing",
        "campaign_objective": "new mobile app launch with user acquisition focus",
        "audience_approach": "comprehensive",
        "competitive_positioning": "challenger",
        
        # Content Creator Configuration
        "content_domain": "social media and digital content creation",
        "content_type": "multi-format campaign assets including video, graphics, and copy",
        "audience_segment": "mobile-first consumers aged 18-35",
        "distribution_channels": "Instagram, TikTok, YouTube, and app store optimization",
        "creative_expertise": "viral content creation and social media optimization",
        "content_approach": "storytelling",
        "brand_voice": "authentic, energetic, and user-centric",
        "content_objectives": "brand awareness and app download conversion",
        "format_optimization": "social_media",
        "personalization_level": "targeted",
        
        # Campaign Analyst Configuration
        "analytics_domain": "digital marketing analytics and performance optimization",
        "campaign_performance": "user acquisition, engagement rates, and conversion metrics",
        "marketing_metrics": "cost per acquisition, lifetime value, and retention rates",
        "analytics_tools": "Google Analytics, Facebook Analytics, and mobile attribution platforms",
        "analytics_expertise": "mobile app marketing analytics and attribution modeling",
        "optimization_methodology": "continuous testing and data-driven optimization",
        "analytics_approach": "prescriptive",
        "optimization_focus": "conversion",
        "reporting_frequency": "weekly",
        
        # Campaign-wide Marketing Parameters
        "business_objectives": "mobile app market penetration and user base growth",
        "budget_strategy": "performance-based allocation with 60% digital, 40% influencer",
        "campaign_timeline": "12-week launch campaign with 4-week pre-launch",
        "success_metrics": "100K app downloads, 25% monthly active users, 4.5+ app store rating",
        "roi_measurement": "customer acquisition cost and lifetime value optimization",
        "attribution_method": "multi-touch attribution with view-through tracking"
    }
    
    print("✅ Marketing guardrails configured for mobile app launch")
    print()
    
    # 5. DEPLOY MARKETING CAMPAIGN SQUAD
    print("🚀 Deploying Marketing Squad...")
    print("   📊 Strategy: Developing mobile app launch strategy")
    print("   🎨 Content: Creating social media and viral content assets")
    print("   📈 Analytics: Setting up performance tracking and optimization")
    print()
    
    try:
        # Deploy the marketing squad
        result = marketing_squad.deploy(guardrails=guardrails)
        
        print("🎉 Marketing Campaign Development Complete!")
        print()
        print("📁 Campaign Deliverables:")
        print("   • Marketing Strategy: outputs/marketing_campaign/01_marketing_strategy.md")
        print("   • Content Assets: outputs/marketing_campaign/02_content_assets.md")
        print("   • Campaign Analysis: outputs/marketing_campaign/03_campaign_analysis.html")
        print("   • Complete Package: outputs/marketing_campaign/campaign_deliverables.json")
        print()
        
        # 6. STORE MARKETING KNOWLEDGE
        print("🧠 Storing Marketing Knowledge...")
        
        marketing_strategist.remember(
            content="Mobile app launches require integrated social media strategy with influencer partnerships for Gen Z targeting",
            tags=["mobile_app", "social_media", "influencer_marketing", "gen_z", "app_launch", "strategy"]
        )
        
        content_creator.remember(
            content="Viral content for app launches needs authentic storytelling with user-generated content and platform-specific optimization",
            tags=["viral_content", "app_launch", "storytelling", "user_generated_content", "social_optimization"]
        )
        
        campaign_analyst.remember(
            content="Mobile app marketing requires multi-touch attribution and focus on lifetime value over just acquisition costs",
            tags=["mobile_analytics", "attribution", "lifetime_value", "app_marketing", "performance_optimization"]
        )
        
        print("✅ Marketing knowledge stored for future campaigns")
        print()
        
        # 7. DEMONSTRATE FRAMEWORK FEATURES
        print("🎯 Marketing Framework Features Demonstrated:")
        print("   ✅ Campaign-type conditional guardrails (brand_awareness, lead_generation, product_launch)")
        print("   ✅ Multi-channel content optimization (social_media, website, email, video)")
        print("   ✅ Analytics approaches (descriptive, diagnostic, predictive, prescriptive)")
        print("   ✅ Memory-enabled brand knowledge accumulation")
        print("   ✅ Sequential campaign development with context building")
        print("   ✅ Multiple output formats for different marketing stakeholders")
        print("   ✅ Professional marketing workflow with performance optimization")
        print("   ✅ Scalable guardrails for different campaign types and audiences")
        print()
        
        if result:
            print("📋 Campaign Summary:")
            print(f"   {result[:250]}...")
        
        return result
        
    except Exception as e:
        print(f"❌ Error during marketing squad deployment: {str(e)}")
        return None

def demonstrate_alternative_campaign():
    """
    Shows how the same marketing squad can be reconfigured for different campaigns
    """
    print("\n" + "="*60)
    print("🔄 Alternative Campaign Configuration")
    print("="*60)
    
    alternative_guardrails = {
        "campaign_type": "brand_awareness",
        "target_market": "enterprise B2B decision makers",
        "marketing_channels": "LinkedIn, industry publications, and webinar marketing",
        "content_type": "thought leadership content and case studies",
        "analytics_approach": "diagnostic",
        "optimization_focus": "engagement"
    }
    
    print("✅ Same marketing framework, different campaign:")
    print("   Original: B2C mobile app launch with social media focus")
    print("   Alternative: B2B brand awareness with thought leadership")
    print("🎯 Demonstrates framework flexibility across marketing contexts")

if __name__ == "__main__":
    result = main()
    demonstrate_alternative_campaign()
    
    print("\n" + "="*60)
    print("📢 Marketing Campaign Squad Complete!")
    print("="*60)
    print("Demonstrated comprehensive marketing campaign capabilities:")
    print("• Conditional guardrails for different campaign types and objectives")
    print("• Professional marketing workflow from strategy to analysis")
    print("• Memory-enabled brand knowledge accumulation across campaigns")
    print("• Multiple output formats for different marketing stakeholders")
    print("• Multi-channel content creation and optimization strategies")
    print("• Performance analytics with data-driven optimization recommendations")
