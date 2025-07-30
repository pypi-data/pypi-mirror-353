#!/usr/bin/env python3
"""
Software Development Team Example
=================================
Comprehensive demonstration of multi-agent framework features including:
- Expert agents with software development specialties
- Squad orchestration with sequential development process
- Operations with conditional guardrails for different project types
- Template variables for dynamic development workflows
- Memory integration for code knowledge retention
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
    Demonstrates a realistic Software Development workflow with 3 experts:
    1. Software Architect - Designs system architecture and technical specifications
    2. Senior Developer - Implements code based on architectural designs
    3. QA Engineer - Tests and validates the implemented solution
    
    Features demonstrated:
    - Conditional guardrails for different project types
    - Template variables for various development scenarios
    - Sequential development process with context passing
    - Multiple output formats for different artifacts
    - Memory integration for knowledge accumulation
    - Professional software development workflow
    """
    
    # Create outputs directory
    os.makedirs("outputs/software_dev", exist_ok=True)
    
    print("💻 Software Development Team")
    print("=" * 40)
    print("Demonstrating agile development workflow...")
    print()
    
    # 1. CREATE SOFTWARE DEVELOPMENT EXPERTS
    print("👨‍💻 Creating Development Team...")
    
    # Software Architect with architecture template variables
    software_architect = Expert(
        specialty="Software Architect specializing in {architecture_domain}",
        objective="Design {system_type} architecture for {project_scope} using {tech_stack}",
        background="Expert in {design_methodology} with {architecture_experience} and {scalability_focus}",
        security_profile="minimal",
        memory_duration="long_term",
        user_id="software_architect_001"
    )
    
    # Senior Developer Expert with template variables
    developer = Expert(
        specialty="Senior {technology_stack} Developer with {experience_level} experience",
        objective="Implement high-quality code following {coding_standards} standards",
        background="""You are a senior developer specializing in {technology_stack}.
        You write clean, maintainable code following {coding_standards} best practices.
        You prioritize {development_approach} and ensure {code_quality_focus}.""",
        security_profile="minimal",
        memory_duration="long_term",
        user_id="dev_team_developer"
    )
    
    # QA Engineer Expert with template variables
    qa_engineer = Expert(
        specialty="QA Engineer specializing in {testing_type} testing",
        objective="Ensure software quality through comprehensive {testing_approach} testing",
        background="""You are a quality assurance engineer with expertise in {testing_type} testing.
        You use {testing_tools} and follow {testing_methodology} methodologies.
        You focus on {quality_metrics} and ensure {compliance_requirements}.""",
        security_profile="minimal",
        memory_duration="long_term",
        user_id="dev_team_qa"
    )
    
    # 2. CREATE OPERATIONS WITH CONDITIONAL GUARDRAILS
    print("📋 Creating Development Operations...")
    
    # Architecture Design Operation with conditional guardrails
    design_operation = Operation(
        instructions="""
        Design a comprehensive architecture for the {project_type} project.
        
        {architecture_scope, select,
          microservices:Design a microservices architecture with proper service boundaries and communication patterns.|
          monolithic:Design a well-structured monolithic architecture with clear separation of concerns.|
          serverless:Design a serverless architecture using cloud-native patterns and functions.
        }
        
        Technology Stack: {technology_stack}
        Architecture Type: {architecture_type}
        
        Include:
        - System architecture diagrams
        - Component specifications
        - Data flow designs
        - API specifications
        - Security considerations
        - Scalability planning
        
        Store this architectural knowledge for future reference using the remember() method.
        """,
        expert=software_architect,
        guardrails=[
            "{project_complexity, select, simple:Focus on clean, minimal architecture.|complex:Include detailed microservices and scaling patterns.|enterprise:Add comprehensive governance and compliance frameworks.}",
            "{performance_requirements, select, basic:Standard performance patterns.|high:Include caching, CDN, and optimization strategies.|critical:Add detailed performance monitoring and failover systems.}"
        ],
        result_destination="outputs/software_dev/architecture_design.md"
    )
    
    # Code Implementation Operation with dynamic requirements
    implementation_operation = Operation(
        instructions="""
        Based on the architectural design, implement the {component_type} component.
        
        {implementation_approach, select,
          tdd:Use Test-Driven Development with comprehensive unit tests.|
          agile:Follow agile development practices with iterative implementation.|
          enterprise:Include full documentation and enterprise patterns.
        }
        
        Programming Language: {programming_language}
        Framework: {framework}
        
        Implementation should include:
        - Clean, well-documented code
        - Unit tests with {test_coverage}% coverage
        - Error handling and logging
        - Security best practices
        - Performance optimization
        - Code review checklist
        
        Remember key implementation patterns and decisions for future projects.
        """,
        expert=developer,
        guardrails=[
            "{code_quality, select, standard:Follow basic coding standards.|premium:Include advanced patterns and optimization.|enterprise:Add comprehensive documentation and compliance.}",
            "{testing_strategy, select, basic:Unit tests only.|comprehensive:Unit, integration, and e2e tests.|full:Include performance and security testing.}"
        ],
        result_destination="outputs/software_dev/implementation.md"
    )
    
    # Quality Assurance Operation with comprehensive testing
    qa_operation = Operation(
        instructions="""
        Perform comprehensive quality assurance testing on the implemented solution.
        
        {testing_scope, select,
          functional:Focus on functional testing and user scenarios.|
          comprehensive:Include functional, performance, and security testing.|
          enterprise:Add compliance, accessibility, and full regression testing.
        }
        
        Testing Framework: {testing_framework}
        Test Environment: {test_environment}
        
        Testing activities:
        - Test plan creation and execution
        - Bug identification and reporting
        - Performance validation
        - Security vulnerability assessment
        - User acceptance criteria verification
        - Deployment readiness checklist
        
        Document all testing results and maintain quality metrics in memory.
        """,
        expert=qa_engineer,
        guardrails=[
            "{quality_standards, select, basic:Standard testing protocols.|high:Include automated testing and CI/CD.|enterprise:Add comprehensive quality gates and compliance.}",
            "{deployment_readiness, select, development:Basic functionality verified.|staging:Full integration testing complete.|production:All quality gates passed and documented.}"
        ],
        result_destination="outputs/software_dev/qa_report.html"
    )
    
    # 3. CREATE SQUAD WITH SEQUENTIAL PROCESS
    print("👥 Assembling Development Squad...")
    
    development_squad = Squad(
        experts=[software_architect, developer, qa_engineer],
        operations=[design_operation, implementation_operation, qa_operation],
        process="sequential",
        memory_sharing=True
    )
    
    # 4. EXECUTE DEVELOPMENT WORKFLOW WITH TEMPLATE VARIABLES
    print("🚀 Starting Development Workflow...")
    print("Template variables will be dynamically filled based on project requirements.")
    print()
    
    try:
        # Execute the squad operations with comprehensive template variables
        result = development_squad.execute(
            "Develop a web application project",
            template_vars={
                # Architecture variables
                "architecture_domain": "web applications",
                "system_type": "scalable web",
                "project_scope": "e-commerce platform",
                "tech_stack": "Node.js and React",
                "design_methodology": "microservices architecture",
                "architecture_experience": "10+ years",
                "scalability_focus": "high-availability systems",
                "project_type": "e-commerce",
                "architecture_scope": "microservices",
                "architecture_type": "cloud-native",
                "project_complexity": "complex",
                "performance_requirements": "high",
                
                # Development variables
                "technology_stack": "Node.js",
                "experience_level": "senior",
                "coding_standards": "ESLint and Prettier",
                "development_approach": "clean architecture",
                "code_quality_focus": "maintainability",
                "component_type": "payment processing",
                "implementation_approach": "tdd",
                "programming_language": "TypeScript",
                "framework": "Express.js",
                "test_coverage": "90",
                "code_quality": "premium",
                "testing_strategy": "comprehensive",
                
                # QA variables
                "testing_type": "automated",
                "testing_approach": "comprehensive",
                "testing_tools": "Jest and Cypress",
                "testing_methodology": "agile testing",
                "quality_metrics": "code coverage and performance",
                "compliance_requirements": "PCI DSS compliance",
                "testing_scope": "comprehensive",
                "testing_framework": "Jest/Cypress",
                "test_environment": "staging",
                "quality_standards": "enterprise",
                "deployment_readiness": "production"
            }
        )
        
        print("✅ Development Workflow Complete!")
        print()
        print("📁 Generated Outputs:")
        print("   - outputs/software_dev/architecture_design.md")
        print("   - outputs/software_dev/implementation.md") 
        print("   - outputs/software_dev/qa_report.html")
        print()
        
        # 5. DEMONSTRATE MEMORY INTEGRATION
        print("🧠 Memory Integration Features:")
        print("   ✓ Long-term memory storage for all experts")
        print("   ✓ Architectural patterns stored for future projects")
        print("   ✓ Code implementation patterns remembered")
        print("   ✓ Quality standards and testing procedures retained")
        print("   ✓ Cross-expert knowledge sharing enabled")
        print()
        
        # 6. DEMONSTRATE FRAMEWORK FEATURES
        print("🎯 Framework Features Demonstrated:")
        print("   ✓ Expert agents with specialized software development roles")
        print("   ✓ Template variables for dynamic project customization")
        print("   ✓ Conditional guardrails for quality control")
        print("   ✓ Sequential squad process with context passing")
        print("   ✓ Multiple result destinations (md, html)")
        print("   ✓ Memory integration for knowledge retention")
        print("   ✓ Security profiles (minimal for development)")
        print()
        
        return result
        
    except Exception as e:
        print(f"❌ Error in development workflow: {e}")
        return None

if __name__ == "__main__":
    result = main()
    if result:
        print("🎉 Software Development Team example completed successfully!")
        print("Check the outputs/ directory for generated artifacts.")
    else:
        print("❌ Example failed to complete.")
