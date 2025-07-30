# Memory System Examples

This document provides practical, real-world examples of using the SecureAgents memory system across different domains and use cases.

## Table of Contents

1. [Personal Assistant Examples](#personal-assistant-examples)
2. [Customer Service Examples](#customer-service-examples)
3. [Educational Assistant Examples](#educational-assistant-examples)
4. [Business Intelligence Examples](#business-intelligence-examples)
5. [Healthcare Assistant Examples](#healthcare-assistant-examples)
6. [E-commerce Examples](#e-commerce-examples)
7. [Content Creation Examples](#content-creation-examples)
8. [Multi-Agent Team Examples](#multi-agent-team-examples)

---

## Personal Assistant Examples

### Daily Routine Assistant

```python
from tbh_secure_agents import Expert
from tbh_secure_agents.memory.models import MemoryType, MemoryPriority

# Create personal assistant
assistant = Expert(
    specialty="Personal Assistant",
    objective="Help manage daily routines and preferences",
    memory_duration="long_term"
)

# Store daily preferences
assistant.remember(
    content="User wakes up at 6:30 AM, drinks coffee immediately, prefers 30-minute morning workout",
    priority=MemoryPriority.HIGH,
    metadata={
        "type": "routine",
        "time": "morning",
        "importance": "daily"
    }
)

assistant.remember(
    content="User has standing meeting every Tuesday at 2 PM with the marketing team",
    priority=MemoryPriority.HIGH,
    metadata={
        "type": "calendar",
        "frequency": "weekly",
        "day": "tuesday"
    }
)

# Store preferences
assistant.remember(
    content="User prefers outdoor restaurants when weather is nice, indoor when cold",
    priority=MemoryPriority.NORMAL,
    metadata={
        "type": "preference",
        "category": "dining"
    }
)

# Later: Recall context for recommendations
def get_morning_routine():
    routine = assistant.recall(
        query="morning routine workout coffee",
        limit=5
    )
    return routine

def get_meeting_context():
    meetings = assistant.recall(
        query="tuesday meeting marketing",
        limit=3
    )
    return meetings
```

### Travel Planning Assistant

```python
# Travel planning across multiple conversations
travel_assistant = Expert(
    specialty="Travel Planner",
    objective="Help plan and organize trips",
    memory_duration="long_term"
)

# Conversation 1: Initial preferences
travel_assistant.remember(
    content="User loves cultural activities, museums, and local food experiences. Budget range $2000-3000 for international trips.",
    priority=MemoryPriority.HIGH,
    metadata={
        "type": "travel_preferences",
        "budget_range": "2000-3000",
        "interests": ["culture", "museums", "food"]
    }
)

# Conversation 2: Specific trip planning
travel_assistant.remember(
    content="Planning 10-day trip to Japan in September 2025. Interested in Tokyo, Kyoto, and Osaka. Wants mix of traditional and modern experiences.",
    priority=MemoryPriority.HIGH,
    metadata={
        "trip_id": "japan_2025",
        "duration": "10_days",
        "destinations": ["tokyo", "kyoto", "osaka"],
        "month": "september"
    }
)

# Conversation 3: Recall and build itinerary
def create_japan_itinerary():
    preferences = travel_assistant.recall(
        query="Japan trip cultural museums food Tokyo Kyoto",
        limit=10
    )
    
    # Use memories to create personalized itinerary
    return preferences
```

---

## Customer Service Examples

### Support Ticket System

```python
# Customer service with memory of interactions
support_agent = Expert(
    specialty="Customer Support",
    objective="Provide personalized customer service",
    memory_duration="long_term"
)

# Store customer interaction
def handle_customer_issue(customer_id, issue, resolution):
    support_agent.remember(
        content=f"Customer {customer_id} reported {issue}. Resolution: {resolution}. Customer satisfaction: High",
        priority=MemoryPriority.NORMAL,
        metadata={
            "customer_id": customer_id,
            "issue_type": issue,
            "resolution_type": resolution,
            "date": "2025-06-05",
            "satisfaction": "high"
        }
    )

# Example usage
handle_customer_issue("CUST_12345", "billing_error", "refund_processed")
handle_customer_issue("CUST_12345", "login_issue", "password_reset")

# Recall customer history
def get_customer_history(customer_id):
    history = support_agent.recall(
        query=f"customer {customer_id}",
        limit=20
    )
    return history

# When customer contacts again
customer_context = get_customer_history("CUST_12345")
# Agent now knows: previous billing issue, login problems, satisfaction level
```

### Account Management

```python
# Account manager with client memory
account_manager = Expert(
    specialty="Account Manager",
    objective="Manage client relationships and preferences",
    memory_duration="long_term"
)

# Store client preferences and history
account_manager.remember(
    content="Client ABC Corp prefers quarterly business reviews, email communication over calls, and focuses on ROI metrics",
    priority=MemoryPriority.HIGH,
    metadata={
        "client": "ABC_Corp",
        "communication_pref": "email",
        "meeting_frequency": "quarterly",
        "focus": "ROI"
    }
)

account_manager.remember(
    content="ABC Corp's Q1 2025 revenue increased 25% after implementing our solution. Key contact: Sarah Johnson, CTO",
    priority=MemoryPriority.HIGH,
    metadata={
        "client": "ABC_Corp",
        "quarter": "Q1_2025",
        "growth": "25%",
        "contact": "Sarah Johnson"
    }
)

# Prepare for client meeting
def prepare_client_meeting(client_name):
    client_info = account_manager.recall(
        query=f"client {client_name} preferences revenue contact",
        limit=15
    )
    return client_info
```

---

## Educational Assistant Examples

### Learning Progress Tracker

```python
# Educational assistant tracking student progress
tutor = Expert(
    specialty="Math Tutor",
    objective="Help students learn mathematics",
    memory_duration="long_term"
)

# Track learning progress
tutor.remember(
    content="Student struggles with algebraic equations but excels at geometry. Prefers visual learning methods.",
    priority=MemoryPriority.HIGH,
    metadata={
        "student_id": "STU_001",
        "strengths": ["geometry"],
        "weaknesses": ["algebra"],
        "learning_style": "visual"
    }
)

tutor.remember(
    content="Completed fractions unit with 85% accuracy. Took 3 weeks, needed extra practice with mixed numbers.",
    priority=MemoryPriority.NORMAL,
    metadata={
        "student_id": "STU_001",
        "unit": "fractions",
        "score": "85%",
        "duration": "3_weeks",
        "challenge": "mixed_numbers"
    }
)

# Personalize learning path
def get_personalized_lesson(student_id):
    student_profile = tutor.recall(
        query=f"student {student_id} strengths weaknesses learning",
        limit=10
    )
    return student_profile
```

### Course Recommendation System

```python
# Academic advisor with course history
advisor = Expert(
    specialty="Academic Advisor",
    objective="Guide students in course selection",
    memory_duration="long_term"
)

# Store academic history
advisor.remember(
    content="Student completed Computer Science 101 with A grade. Enjoyed programming assignments, struggled with theoretical concepts.",
    priority=MemoryPriority.NORMAL,
    metadata={
        "student": "john_doe",
        "course": "CS101",
        "grade": "A",
        "enjoyed": ["programming"],
        "struggled": ["theory"]
    }
)

# Recommend next courses
def recommend_courses(student_name):
    academic_history = advisor.recall(
        query=f"student {student_name} course grade programming",
        limit=8
    )
    return academic_history
```

---

## Business Intelligence Examples

### Market Research Assistant

```python
# Market research with trend tracking
researcher = Expert(
    specialty="Market Research Analyst",
    objective="Track market trends and provide insights",
    memory_duration="auto"
)

# Store market insights
researcher.remember(
    content="AI adoption in healthcare sector increased 300% in Q1 2025. Key drivers: efficiency and cost reduction.",
    priority=MemoryPriority.HIGH,
    metadata={
        "sector": "healthcare",
        "technology": "AI",
        "period": "Q1_2025",
        "growth": "300%",
        "drivers": ["efficiency", "cost_reduction"]
    }
)

researcher.remember(
    content="Competitor XYZ Corp launched new product with 40% market penetration in first month. Price point: $99.",
    priority=MemoryPriority.HIGH,
    metadata={
        "competitor": "XYZ_Corp",
        "product_type": "new_launch",
        "penetration": "40%",
        "price": "99",
        "timeframe": "first_month"
    }
)

# Generate market report
def generate_market_report(sector):
    market_data = researcher.recall(
        query=f"{sector} growth trends competition",
        limit=20
    )
    return market_data
```

### Sales Intelligence

```python
# Sales assistant with lead tracking
sales_assistant = Expert(
    specialty="Sales Intelligence",
    objective="Track leads and optimize sales processes",
    memory_duration="long_term"
)

# Track lead interactions
sales_assistant.remember(
    content="Lead ABC Manufacturing showed strong interest in enterprise package. Decision timeline: Q3 2025. Budget: $50K+",
    priority=MemoryPriority.HIGH,
    metadata={
        "lead": "ABC_Manufacturing",
        "interest_level": "high",
        "package": "enterprise",
        "timeline": "Q3_2025",
        "budget": "50K+"
    }
)

# Sales performance tracking
sales_assistant.remember(
    content="Closed deal with DEF Corp for $75K. Sales cycle: 3 months. Key factor: ROI demonstration",
    priority=MemoryPriority.NORMAL,
    metadata={
        "client": "DEF_Corp",
        "value": "75K",
        "cycle_length": "3_months",
        "success_factor": "ROI_demo"
    }
)

# Optimize sales approach
def optimize_sales_strategy():
    sales_data = sales_assistant.recall(
        query="closed deals success factors timeline budget",
        limit=25
    )
    return sales_data
```

---

## Healthcare Assistant Examples

### Patient Care Assistant

```python
# Healthcare assistant (anonymized patient data)
care_assistant = Expert(
    specialty="Patient Care Coordinator",
    objective="Coordinate patient care and track preferences",
    memory_duration="long_term"
)

# Store patient preferences (anonymized)
care_assistant.remember(
    content="Patient ID P001 prefers morning appointments, has mobility limitations, needs wheelchair accessible facilities",
    priority=MemoryPriority.HIGH,
    metadata={
        "patient_id": "P001",
        "appointment_pref": "morning",
        "accessibility": ["wheelchair"],
        "special_needs": ["mobility_limited"]
    }
)

# Track care plan progress
care_assistant.remember(
    content="Patient P001 completed physical therapy week 3 of 6. Progress: improved range of motion by 15%",
    priority=MemoryPriority.NORMAL,
    metadata={
        "patient_id": "P001",
        "treatment": "physical_therapy",
        "week": "3_of_6",
        "improvement": "15%_ROM"
    }
)

# Coordinate care
def coordinate_patient_care(patient_id):
    patient_info = care_assistant.recall(
        query=f"patient {patient_id} preferences appointments accessibility",
        limit=10
    )
    return patient_info
```

---

## E-commerce Examples

### Shopping Assistant

```python
# E-commerce personal shopper
shopper = Expert(
    specialty="Personal Shopping Assistant",
    objective="Provide personalized shopping recommendations",
    memory_duration="long_term"
)

# Store shopping preferences
shopper.remember(
    content="Customer prefers sustainable brands, size Medium, budget $50-100 for clothing, likes minimalist style",
    priority=MemoryPriority.HIGH,
    metadata={
        "customer_id": "SHOP_123",
        "brand_pref": "sustainable",
        "size": "Medium",
        "budget_clothing": "50-100",
        "style": "minimalist"
    }
)

# Track purchase history
shopper.remember(
    content="Customer purchased organic cotton t-shirt ($45) and eco-friendly jeans ($85). High satisfaction rating.",
    priority=MemoryPriority.NORMAL,
    metadata={
        "customer_id": "SHOP_123",
        "items": ["cotton_tshirt", "eco_jeans"],
        "total": "130",
        "satisfaction": "high"
    }
)

# Generate recommendations
def get_product_recommendations(customer_id):
    preferences = shopper.recall(
        query=f"customer {customer_id} preferences style budget sustainable",
        limit=15
    )
    return preferences
```

---

## Content Creation Examples

### Writing Assistant

```python
# Content creation assistant
writer = Expert(
    specialty="Content Writing Assistant",
    objective="Help create consistent, branded content",
    memory_duration="long_term"
)

# Store brand guidelines
writer.remember(
    content="Brand voice: Professional but approachable. Avoid jargon. Use active voice. Target audience: small business owners",
    priority=MemoryPriority.HIGH,
    metadata={
        "type": "brand_guidelines",
        "voice": "professional_approachable",
        "audience": "small_business_owners",
        "style": "active_voice"
    }
)

# Track successful content
writer.remember(
    content="Blog post 'Small Business Marketing Tips' received 500 shares, 50 comments. Key elements: actionable tips, real examples",
    priority=MemoryPriority.NORMAL,
    metadata={
        "content_type": "blog_post",
        "title": "Small Business Marketing Tips",
        "engagement": "high",
        "success_factors": ["actionable", "real_examples"]
    }
)

# Create consistent content
def create_blog_post(topic):
    brand_context = writer.recall(
        query="brand voice guidelines audience style successful",
        limit=10
    )
    return brand_context
```

---

## Multi-Agent Team Examples

### Research and Content Team

```python
from tbh_secure_agents import Squad, Operation

# Create team with shared memory
researcher = Expert(
    specialty="Research Specialist",
    objective="Conduct thorough research",
    memory_duration="long_term"
)

writer = Expert(
    specialty="Content Writer",
    objective="Create engaging content",
    memory_duration="long_term"
)

# Research phase
researcher.remember(
    content="AI market size projected to reach $1.8 trillion by 2030. Key growth areas: healthcare, finance, autonomous vehicles",
    priority=MemoryPriority.HIGH,
    metadata={
        "topic": "AI_market",
        "projection": "1.8T_by_2030",
        "sectors": ["healthcare", "finance", "autonomous"]
    }
)

# Content creation using research
def create_content_operation():
    # Writer recalls researcher's findings
    research_data = researcher.recall(
        query="AI market growth healthcare finance",
        limit=10
    )
    
    # Create operation using research context
    operation = Operation(
        instructions=f"Create an article about AI market growth using this research data: {research_data}",
        expert=writer
    )
    
    return operation

# Squad coordination
team = Squad(
    experts=[researcher, writer],
    operations=[create_content_operation()],
    process="sequential"
)
```

### Customer Service Team

```python
# Multi-agent customer service
tier1_agent = Expert(
    specialty="Tier 1 Support",
    objective="Handle basic customer inquiries",
    memory_duration="long_term"
)

specialist_agent = Expert(
    specialty="Technical Specialist",
    objective="Resolve complex technical issues",
    memory_duration="long_term"
)

# Tier 1 handles initial contact
tier1_agent.remember(
    content="Customer CUST_999 has recurring login issues. Basic troubleshooting unsuccessful. Escalating to specialist.",
    metadata={
        "customer": "CUST_999",
        "issue": "login_recurring",
        "status": "escalated",
        "attempted": "basic_troubleshooting"
    }
)

# Specialist accesses tier 1 notes
def specialist_takeover(customer_id):
    tier1_notes = tier1_agent.recall(
        query=f"customer {customer_id} escalated",
        limit=5
    )
    
    # Specialist continues with context
    specialist_agent.remember(
        content=f"Taking over case for {customer_id}. Previous notes reviewed: {tier1_notes}",
        metadata={
            "customer": customer_id,
            "handoff": "tier1_to_specialist",
            "context_preserved": True
        }
    )
```

---

## Best Practices from Examples

### 1. Use Descriptive Content
```python
# Good
expert.remember(
    content="Customer John Smith from ABC Corp prefers email communication and quarterly reviews"
)

# Better
expert.remember(
    content="Customer John Smith (john@abccorp.com) from ABC Corp prefers email over phone, quarterly business reviews on first Tuesday of quarter, focuses on ROI metrics",
    metadata={
        "customer": "john_smith",
        "company": "ABC_Corp",
        "contact_pref": "email",
        "meeting_schedule": "quarterly_first_tuesday"
    }
)
```

### 2. Organize with Metadata
```python
expert.remember(
    content="Important customer information",
    metadata={
        "type": "customer_data",
        "importance": "high",
        "category": "preferences",
        "last_updated": "2025-06-05"
    }
)
```

### 3. Use Appropriate Priorities
```python
# Critical information
expert.remember(content="Customer has severe allergy", priority=MemoryPriority.HIGH)

# Regular information  
expert.remember(content="Customer prefers morning meetings", priority=MemoryPriority.NORMAL)

# Minor details
expert.remember(content="Customer mentioned nice weather", priority=MemoryPriority.LOW)
```

### 4. Build Context Over Time
```python
# Session 1
expert.remember(content="Customer interested in Product A")

# Session 2 - Build on previous
previous = expert.recall(query="Product A interest")
expert.remember(content="Customer wants demo of Product A, budget approved")

# Session 3 - Continue building
expert.remember(content="Demo completed, customer ready to purchase Product A")
```

---

These examples show how the memory system enables rich, contextual interactions across various domains. The key is to store meaningful, searchable content with appropriate metadata and priorities.
