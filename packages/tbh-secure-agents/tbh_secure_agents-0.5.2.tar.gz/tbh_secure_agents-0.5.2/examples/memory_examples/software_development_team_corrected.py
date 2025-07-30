#!/usr/bin/env python3
"""
Software Development Team - Comprehensive Multi-Agent Example

This example demonstrates a complete software development workflow using TBH Secure Agents
with all framework features based on official documentation:
- Expert agents with specialized roles and memory capabilities  
- Template variables for dynamic behavior
- Conditional guardrails with select syntax
- Sequential Squad processes with automatic context passing
- Operations with result_destination configurations
- Multiple output formats (md, html, json)
- Security profiles (minimal for development examples)
- Memory integration for knowledge retention

The team consists of:
1. Software Architect - Designs system architecture
2. Senior Developer - Implements the code
3. QA Engineer - Tests and validates the implementation

All features demonstrated are based on the official framework documentation.
"""

import os
from SecureAgents import Expert, Operation, Squad

def main():
    """
    Main function demonstrating a comprehensive software development team workflow.
    """
    try:
        # Get API key from environment
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Please set your GOOGLE_API_KEY environment variable")

        print("🔧 TBH SECURE AGENTS - SOFTWARE DEVELOPMENT TEAM")
        print("=" * 60)

        # Create Software Architect Expert with template variables
        architect = Expert(
            specialty="Software Architect specializing in {technology_stack} applications",
            objective="Design scalable {architecture_type} architectures for {project_type} projects",
            background="""You are an experienced software architect with expertise in {technology_stack}.
            You follow {design_methodology} principles and prioritize {quality_attributes}.
            Your designs emphasize {architectural_patterns} patterns.""",
            memory=True,
            memory_type="long_term",
            user_id="dev_team_architect",
            security_profile="minimal",
            api_key=api_key
        )

        # Create Senior Developer Expert with template variables
        developer = Expert(
            specialty="Senior {technology_stack} Developer with {experience_level} experience",
            objective="Implement high-quality code following {coding_standards} standards",
            background="""You are a senior developer specializing in {technology_stack}.
            You write clean, maintainable code following {coding_standards} best practices.
            You prioritize {development_approach} and ensure {code_quality_focus}.""",
            memory=True,
            memory_type="long_term", 
            user_id="dev_team_developer",
            security_profile="minimal",
            api_key=api_key
        )

        # Create QA Engineer Expert with template variables
        qa_engineer = Expert(
            specialty="QA Engineer specializing in {testing_type} testing",
            objective="Ensure software quality through comprehensive {testing_approach} testing",
            background="""You are a quality assurance engineer with expertise in {testing_type} testing.
            You use {testing_tools} and follow {testing_methodology} methodologies.
            You focus on {quality_metrics} and ensure {compliance_requirements}.""",
            memory=True,
            memory_type="long_term",
            user_id="dev_team_qa",
            security_profile="minimal", 
            api_key=api_key
        )

        # Create Architecture Design Operation with conditional guardrails
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
            Design Methodology: {design_methodology}
            
            {quality_focus, select,
              performance:Prioritize performance optimization and scalability in your design.|
              security:Emphasize security patterns and secure design principles.|
              maintainability:Focus on maintainable, readable, and extensible architecture.
            }
            
            Include:
            - System architecture diagram description
            - Component breakdown and responsibilities
            - Data flow and integration patterns
            - Technology recommendations
            - Scalability considerations
            - Security design patterns
            """,
            output_format="Comprehensive architecture design document",
            expert=architect,
            result_destination="architecture_design.md"
        )

        # Create Implementation Operation with template variables
        implementation_operation = Operation(
            instructions="""
            Based on the provided architecture design, implement the core components.
            
            Technology Stack: {technology_stack}
            Coding Standards: {coding_standards}
            Development Approach: {development_approach}
            
            {implementation_scope, select,
              full:Implement all core components with complete functionality.|
              mvp:Focus on minimum viable product with essential features only.|
              prototype:Create a working prototype demonstrating key concepts.
            }
            
            {code_quality_focus, select,
              clean_code:Emphasize clean code principles with clear naming and structure.|
              performance:Optimize for performance and efficiency.|
              testability:Design code for maximum testability and maintainability.
            }
            
            Provide:
            - Complete code implementation
            - Code structure and organization
            - Key algorithms and business logic
            - Error handling and validation
            - Documentation and comments
            - Installation and setup instructions
            """,
            output_format="Complete code implementation with documentation",
            expert=developer,
            result_destination="implementation.md"
        )

        # Create Testing Operation with conditional logic
        testing_operation = Operation(
            instructions="""
            Create comprehensive tests for the implemented software components.
            
            Testing Type: {testing_type}
            Testing Approach: {testing_approach}
            Testing Tools: {testing_tools}
            Testing Methodology: {testing_methodology}
            
            {test_coverage_level, select,
              comprehensive:Create extensive test coverage including unit, integration, and end-to-end tests.|
              standard:Implement standard test coverage with focus on critical functionality.|
              targeted:Focus testing on high-risk areas and core business logic.
            }
            
            {quality_metrics, select,
              functional:Focus on functional correctness and requirement validation.|
              performance:Emphasize performance testing and benchmarking.|
              security:Prioritize security testing and vulnerability assessment.
            }
            
            Include:
            - Test strategy and approach
            - Test cases and scenarios
            - Automated test implementation
            - Test data and fixtures
            - Performance benchmarks
            - Quality assessment report
            - Compliance validation
            """,
            output_format="Complete testing suite with quality report",
            expert=qa_engineer,
            result_destination="testing_report.html"
        )

        # Create Final Integration Operation
        integration_operation = Operation(
            instructions="""
            Integrate all team outputs into a comprehensive software delivery package.
            
            Project Type: {project_type}
            Delivery Format: {delivery_format}
            Documentation Level: {documentation_level}
            
            {integration_approach, select,
              agile:Use agile integration practices with iterative delivery.|
              waterfall:Follow traditional waterfall integration methodology.|
              devops:Implement DevOps practices with CI/CD pipeline recommendations.
            }
            
            Create a complete software delivery package including:
            - Executive summary of the project
            - Architecture design and decisions
            - Implementation details and code
            - Testing results and quality metrics
            - Deployment and operational guidance
            - Risk assessment and mitigation
            - Future recommendations
            """,
            output_format="Complete software delivery package",
            expert=architect,
            result_destination="software_delivery_package.json"
        )

        # Create Squad with all experts and operations
        dev_team = Squad(
            experts=[architect, developer, qa_engineer],
            operations=[design_operation, implementation_operation, testing_operation, integration_operation],
            process="sequential",
            security_level="minimal"
        )

        # Define comprehensive guardrails based on documentation examples
        guardrails = {
            # Project configuration
            "project_type": "e-commerce platform",
            "technology_stack": "Python/Django",
            "architecture_type": "microservices",
            "architecture_scope": "microservices",
            
            # Development methodology
            "design_methodology": "Domain-Driven Design",
            "development_approach": "test-driven development",
            "coding_standards": "PEP 8",
            
            # Quality and testing
            "quality_attributes": "scalability and maintainability",
            "quality_focus": "maintainability", 
            "architectural_patterns": "hexagonal architecture",
            "code_quality_focus": "clean_code",
            
            # Testing configuration
            "testing_type": "automated",
            "testing_approach": "behavior-driven",
            "testing_tools": "pytest and Selenium",
            "testing_methodology": "risk-based testing",
            "test_coverage_level": "comprehensive",
            "quality_metrics": "functional",
            
            # Experience and compliance
            "experience_level": "10+ years",
            "compliance_requirements": "industry best practices",
            "implementation_scope": "mvp",
            
            # Integration and delivery
            "integration_approach": "agile",
            "delivery_format": "production-ready",
            "documentation_level": "comprehensive"
        }

        print("🚀 Deploying Software Development Team...")
        print("📋 Project Configuration:")
        print(f"   - Project Type: {guardrails['project_type']}")
        print(f"   - Technology Stack: {guardrails['technology_stack']}")
        print(f"   - Architecture: {guardrails['architecture_type']}")
        print(f"   - Methodology: {guardrails['design_methodology']}")
        print()

        # Deploy the squad with guardrails
        result = dev_team.deploy(guardrails=guardrails)

        # Save comprehensive output
        output_file = "software_development_team_output.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("TBH SECURE AGENTS - SOFTWARE DEVELOPMENT TEAM\n\n")
            f.write("Project Configuration:\n")
            for key, value in guardrails.items():
                f.write(f"  - {key}: {value}\n")
            f.write(f"\nTeam Result:\n\n")
            f.write(result)
        
        print(f"✅ Software development workflow completed!")
        print(f"📄 Full output saved to {output_file}")
        print(f"📁 Individual outputs saved to:")
        print(f"   - architecture_design.md")
        print(f"   - implementation.md") 
        print(f"   - testing_report.html")
        print(f"   - software_delivery_package.json")

    except Exception as e:
        print(f"❌ Error during software development workflow: {e}")

if __name__ == "__main__":
    main()
