#!/usr/bin/env python3
"""
Financial Advisory Team Example
==============================
Comprehensive demonstration of multi-agent framework features including:
- Expert agents with financial specialties
- Squad orchestration with advisory process
- Operations with conditional guardrails for different client types
- Template variables for dynamic financial planning
- Memory integration for client knowledge retention
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
    Demonstrates a realistic Financial Advisory workflow with 3 experts:
    1. Financial Researcher - Conducts market research and investment analysis
    2. Financial Advisor - Provides personalized financial planning and advice
    3. Compliance Officer - Ensures regulatory compliance and risk management
    
    Features demonstrated:
    - Conditional guardrails for different client profiles and risk levels
    - Template variables for various financial scenarios
    - Sequential advisory process with context building
    - Multiple output formats for different financial documents
    - Memory integration for client knowledge accumulation
    - Professional financial advisory workflow
    """
    
    # Create outputs directory
    os.makedirs("outputs/financial_advisory", exist_ok=True)
    
    print("💰 Financial Advisory Team")
    print("=" * 35)
    print("Demonstrating comprehensive financial planning workflow...")
    print()
    
    # 1. CREATE FINANCIAL ADVISORY EXPERTS
    print("🏦 Creating Financial Advisory Team...")
    
    # Financial Researcher with research template variables
    financial_researcher = Expert(
        specialty="Financial Researcher specializing in {research_domain}",
        objective="Analyze {investment_focus} and provide {analysis_depth} market insights for {client_profile}",
        background="Expert in {research_methodology} with {market_expertise} and {analytical_tools}",
        security_profile="minimal",
        memory_duration="long_term",
        user_id="financial_researcher_001"
    )
    
    # Financial Advisor with advisory template variables
    financial_advisor = Expert(
        specialty="Financial Advisor expert in {advisory_domain}",
        objective="Provide {planning_type} for {client_segment} using {advisory_approach}",
        background="Certified financial planner with {advisory_expertise} and {planning_methodology}",
        security_profile="minimal",
        memory_duration="long_term",
        user_id="financial_advisor_001"
    )
    
    # Compliance Officer with regulatory template variables
    compliance_officer = Expert(
        specialty="Compliance Officer specializing in {compliance_domain}",
        objective="Ensure {compliance_standards} and manage {risk_assessment} for {regulatory_framework}",
        background="Expert in {compliance_expertise} with {regulatory_experience} and {risk_methodology}",
        security_profile="minimal",
        memory_duration="long_term",
        user_id="compliance_officer_001"
    )
    
    print("✅ Created financial advisory team with memory and specializations")
    print()
    
    # 2. CREATE FINANCIAL OPERATIONS WITH CONDITIONAL GUARDRAILS
    print("📊 Setting up Financial Operations...")
    
    # Market Research Operation with investment type conditions
    research_operation = Operation(
        instructions="""
        Conduct comprehensive financial market research for {client_profile} focusing on {investment_focus}.
        
        Research Framework:
        {research_scope, select,
          market_overview: Broad market analysis with sector performance and economic indicators.|
          investment_specific: Detailed analysis of specific investment opportunities and vehicles.|
          risk_assessment: Focus on risk factors, volatility analysis, and downside protection.|
          comprehensive: Complete analysis covering market trends, investments, and risk factors.
        }
        
        Analysis Components:
        - Market Conditions: {market_analysis}
        - Investment Opportunities: {investment_focus}
        - Risk Assessment: {risk_evaluation}
        - Economic Indicators: {economic_factors}
        - Performance Metrics: {performance_analysis}
        
        {client_sophistication, select,
          basic: Provide fundamental analysis suitable for novice investors.|
          intermediate: Include technical analysis and moderate complexity strategies.|
          advanced: Deliver sophisticated analysis with complex instruments and strategies.|
          institutional: Provide institutional-grade analysis with advanced modeling.
        }
        
        Research Elements:
        - Asset allocation recommendations
        - Market timing and entry/exit strategies
        - Diversification and portfolio construction
        - Tax implications and optimization
        - Regulatory and compliance considerations
        
        Research Domain: {research_domain}
        Research Methodology: {research_methodology}
        Market Expertise: {market_expertise}
        
        {time_horizon, select,
          short_term: Focus on 1-2 year investment strategies and tactical opportunities.|
          medium_term: Analyze 3-7 year growth strategies and lifecycle planning.|
          long_term: Emphasize 10+ year wealth building and retirement planning.|
          multi_horizon: Provide strategies across multiple time horizons and goals.
        }
        
        Ensure research supports {financial_objectives} and matches {risk_tolerance}.
        """,
        expected_output="Comprehensive market research analysis for {client_profile}",
        expert=financial_researcher,
        result_destination={
            "format": "md",
            "file_path": "outputs/financial_advisory/01_market_research.md"
        }
    )
    
    # Financial Planning Operation
    planning_operation = Operation(
        instructions="""
        Develop personalized financial plan based on market research and client profile.
        
        Planning Framework:
        {planning_approach, select,
          goals_based: Focus on specific financial goals with timeline and funding strategies.|
          lifecycle: Comprehensive planning across life stages and changing needs.|
          wealth_management: High-net-worth planning with tax optimization and estate planning.|
          retirement_focused: Specialized retirement planning with income replacement strategies.
        }
        
        Financial Planning Components:
        - Planning Type: {planning_type}
        - Client Segment: {client_segment}
        - Advisory Approach: {advisory_approach}
        - Risk Profile: {risk_tolerance}
        - Investment Strategy: {investment_strategy}
        
        {priority_focus, select,
          wealth_accumulation: Emphasize growth strategies and investment optimization.|
          risk_management: Focus on insurance, protection, and downside mitigation.|
          tax_optimization: Prioritize tax-efficient strategies and planning.|
          estate_planning: Concentrate on wealth transfer and legacy planning.|
          balanced: Integrate all aspects of comprehensive financial planning.
        }
        
        Plan Elements:
        - Financial goals and timeline assessment
        - Investment policy statement and allocation
        - Insurance and protection strategies
        - Tax planning and optimization tactics
        - Estate planning and wealth transfer
        
        Advisory Domain: {advisory_domain}
        Advisory Expertise: {advisory_expertise}
        Planning Methodology: {planning_methodology}
        
        {implementation_style, select,
          conservative: Low-risk approach with capital preservation focus.|
          moderate: Balanced approach with moderate risk for steady growth.|
          aggressive: Higher-risk strategies for accelerated wealth building.|
          dynamic: Adaptive approach adjusting to market conditions and life changes.
        }
        
        Ensure plan achieves {financial_objectives} within {risk_tolerance} parameters.
        """,
        expected_output="Complete financial plan tailored for {client_segment}",
        expert=financial_advisor,
        result_destination={
            "format": "md",
            "file_path": "outputs/financial_advisory/02_financial_plan.md"
        }
    )
    
    # Compliance Review Operation
    compliance_operation = Operation(
        instructions="""
        Review financial recommendations for regulatory compliance and risk management.
        
        Compliance Framework:
        {compliance_focus, select,
          regulatory: Ensure adherence to SEC, FINRA, and state regulations.|
          fiduciary: Verify fiduciary standard compliance and best interest requirements.|
          risk_management: Focus on risk disclosure and client suitability.|
          comprehensive: Cover all regulatory, fiduciary, and risk management aspects.
        }
        
        Compliance Review:
        - Compliance Standards: {compliance_standards}
        - Risk Assessment: {risk_assessment}
        - Regulatory Framework: {regulatory_framework}
        - Documentation: {compliance_documentation}
        - Monitoring: {ongoing_compliance}
        
        {risk_tolerance_verification, select,
          conservative: Verify alignment with low-risk tolerance and capital preservation.|
          moderate: Confirm balanced risk approach with growth and protection balance.|
          aggressive: Validate high-risk tolerance with appropriate disclosures.|
          custom: Review customized risk profile with specific client considerations.
        }
        
        Compliance Elements:
        - Suitability analysis and documentation
        - Risk disclosure and client acknowledgment
        - Regulatory filing and record keeping
        - Conflict of interest identification
        - Ongoing monitoring and review procedures
        
        Compliance Domain: {compliance_domain}
        Compliance Expertise: {compliance_expertise}
        Regulatory Experience: {regulatory_experience}
        
        {documentation_level, select,
          basic: Essential documentation for regulatory compliance.|
          standard: Comprehensive documentation with detailed justifications.|
          extensive: Exhaustive documentation for complex or high-risk strategies.|
          audit_ready: Documentation prepared for regulatory examination and audit.
        }
        
        Ensure all recommendations meet {compliance_standards} and protect client interests.
        """,
        expected_output="Compliance review with regulatory validation and risk assessment",
        expert=compliance_officer,
        result_destination={
            "format": "html",
            "file_path": "outputs/financial_advisory/03_compliance_review.html"
        }
    )
    
    print("✅ Created financial operations with regulatory guardrails")
    print()
    
    # 3. CREATE FINANCIAL ADVISORY SQUAD
    print("🎯 Assembling Financial Advisory Squad...")
    
    advisory_squad = Squad(
        experts=[financial_researcher, financial_advisor, compliance_officer],
        operations=[research_operation, planning_operation, compliance_operation],
        process="sequential",
        security_profile="minimal",
        result_destination={
            "format": "json",
            "file_path": "outputs/financial_advisory/advisory_package.json"
        }
    )
    
    print("✅ Advisory squad assembled with compliance workflow")
    print()
    
    # 4. COMPREHENSIVE GUARDRAILS FOR FINANCIAL ADVISORY
    print("🛡️ Configuring Financial Guardrails...")
    
    guardrails = {
        # Financial Researcher Configuration
        "research_domain": "investment analysis and market research",
        "investment_focus": "balanced portfolio with growth and income strategies",
        "analysis_depth": "comprehensive analysis with risk assessment",
        "client_profile": "high-net-worth individual seeking wealth preservation and growth",
        "research_methodology": "fundamental analysis with quantitative risk modeling",
        "market_expertise": "equity markets, fixed income, and alternative investments",
        "analytical_tools": "financial modeling, scenario analysis, and stress testing",
        "research_scope": "comprehensive",
        "client_sophistication": "advanced",
        "time_horizon": "multi_horizon",
        
        # Financial Advisor Configuration
        "advisory_domain": "comprehensive wealth management and financial planning",
        "planning_type": "integrated wealth management with tax optimization",
        "client_segment": "affluent professionals and business owners",
        "advisory_approach": "holistic planning with lifecycle considerations",
        "advisory_expertise": "CFP certification with estate planning specialization",
        "planning_methodology": "goals-based planning with regular review and adjustment",
        "planning_approach": "wealth_management",
        "priority_focus": "balanced",
        "implementation_style": "moderate",
        
        # Compliance Officer Configuration
        "compliance_domain": "investment advisor compliance and fiduciary standards",
        "compliance_standards": "SEC RIA regulations and fiduciary duty requirements",
        "risk_assessment": "comprehensive suitability and risk tolerance validation",
        "regulatory_framework": "federal and state investment advisor regulations",
        "compliance_expertise": "Series 65, compliance procedures, and regulatory filing",
        "regulatory_experience": "RIA compliance and examination preparation",
        "risk_methodology": "risk profiling and ongoing suitability monitoring",
        "compliance_focus": "comprehensive",
        "risk_tolerance_verification": "moderate",
        "documentation_level": "standard",
        
        # Client-wide Advisory Parameters
        "financial_objectives": "wealth preservation, tax-efficient growth, and retirement security",
        "risk_tolerance": "moderate with focus on long-term growth and downside protection",
        "market_analysis": "current market conditions with economic outlook assessment",
        "risk_evaluation": "portfolio risk analysis with stress testing scenarios",
        "economic_factors": "interest rates, inflation, and monetary policy impacts",
        "performance_analysis": "historical performance with forward-looking projections",
        "investment_strategy": "diversified allocation with tactical adjustments",
        "compliance_documentation": "comprehensive suitability and recommendation documentation",
        "ongoing_compliance": "quarterly review with annual comprehensive assessment"
    }
    
    print("✅ Financial guardrails configured for wealth management client")
    print()
    
    # 5. DEPLOY FINANCIAL ADVISORY SQUAD
    print("🚀 Deploying Financial Advisory Squad...")
    print("   📈 Research: Analyzing investment opportunities and market conditions")
    print("   💡 Planning: Developing comprehensive wealth management strategy")
    print("   ✅ Compliance: Ensuring regulatory compliance and risk management")
    print()
    
    try:
        # Deploy the advisory squad
        result = advisory_squad.deploy(guardrails=guardrails)
        
        print("🎉 Financial Advisory Process Complete!")
        print()
        print("📁 Advisory Deliverables:")
        print("   • Market Research: outputs/financial_advisory/01_market_research.md")
        print("   • Financial Plan: outputs/financial_advisory/02_financial_plan.md")
        print("   • Compliance Review: outputs/financial_advisory/03_compliance_review.html")
        print("   • Complete Package: outputs/financial_advisory/advisory_package.json")
        print()
        
        # 6. STORE FINANCIAL KNOWLEDGE
        print("🧠 Storing Financial Knowledge...")
        
        financial_researcher.remember(
            content="High-net-worth clients require comprehensive market analysis with alternative investments and tax-loss harvesting strategies",
            tags=["high_net_worth", "market_analysis", "alternative_investments", "tax_optimization", "wealth_management"]
        )
        
        financial_advisor.remember(
            content="Wealth management planning must integrate estate planning, tax optimization, and risk management for affluent clients",
            tags=["wealth_management", "estate_planning", "tax_optimization", "risk_management", "affluent_clients"]
        )
        
        compliance_officer.remember(
            content="RIA compliance requires thorough suitability documentation and ongoing risk tolerance monitoring for fiduciary duty",
            tags=["ria_compliance", "suitability", "risk_tolerance", "fiduciary_duty", "regulatory_documentation"]
        )
        
        print("✅ Financial knowledge stored for future client engagements")
        print()
        
        # 7. DEMONSTRATE FRAMEWORK FEATURES
        print("🎯 Financial Advisory Framework Features Demonstrated:")
        print("   ✅ Client-type conditional guardrails (basic, intermediate, advanced, institutional)")
        print("   ✅ Planning approaches (goals_based, lifecycle, wealth_management, retirement_focused)")
        print("   ✅ Compliance frameworks (regulatory, fiduciary, risk_management)")
        print("   ✅ Memory-enabled client knowledge accumulation")
        print("   ✅ Sequential advisory process with regulatory validation")
        print("   ✅ Multiple output formats for different financial stakeholders")
        print("   ✅ Professional financial workflow with compliance integration")
        print("   ✅ Scalable guardrails for different client segments and risk profiles")
        print()
        
        if result:
            print("📋 Advisory Summary:")
            print(f"   {result[:250]}...")
        
        return result
        
    except Exception as e:
        print(f"❌ Error during advisory squad deployment: {str(e)}")
        return None

def demonstrate_alternative_client():
    """
    Shows how the same advisory squad can be reconfigured for different client types
    """
    print("\n" + "="*60)
    print("🔄 Alternative Client Configuration")
    print("="*60)
    
    alternative_guardrails = {
        "client_profile": "young professional seeking retirement planning",
        "planning_approach": "retirement_focused",
        "client_sophistication": "basic",
        "time_horizon": "long_term",
        "priority_focus": "wealth_accumulation",
        "implementation_style": "conservative",
        "risk_tolerance_verification": "conservative"
    }
    
    print("✅ Same advisory framework, different client:")
    print("   Original: High-net-worth wealth management with tax optimization")
    print("   Alternative: Young professional retirement planning")
    print("🎯 Demonstrates framework adaptability across client segments")

if __name__ == "__main__":
    result = main()
    demonstrate_alternative_client()
    
    print("\n" + "="*60)
    print("💰 Financial Advisory Team Complete!")
    print("="*60)
    print("Demonstrated comprehensive financial advisory capabilities:")
    print("• Conditional guardrails for different client profiles and risk levels")
    print("• Professional advisory workflow from research to compliance")
    print("• Memory-enabled client knowledge accumulation across engagements")
    print("• Multiple output formats for different financial stakeholders")
    print("• Regulatory compliance integration with fiduciary standards")
    print("• Scalable framework for various client segments and planning needs")
