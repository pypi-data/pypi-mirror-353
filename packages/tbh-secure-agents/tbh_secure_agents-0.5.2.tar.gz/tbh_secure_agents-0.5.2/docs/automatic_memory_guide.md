# Automatic Memory System Guide

## Overview

The SecureAgents framework features a **completely automatic** memory system with ChromaDB backend. Agents intelligently store and retrieve information during processing **without any manual memory management required**.

## Key Features

- **Zero Manual Memory Management**: No `remember()` or `recall()` calls needed
- **ChromaDB Backend**: Vector-based storage for intelligent retrieval  
- **Automatic Intelligence**: System decides what to store and when
- **Multiple Memory Types**: Session, Working, Long-term, and Pattern memories
- **Encryption**: All memories are encrypted before storage
- **Context-Aware**: Automatic retrieval during operations
- **User Isolation**: Each user has isolated memory spaces

## 🚀 Quick Start - Automatic Memory

### Step 1: Create Expert with Automatic Memory

```python
from tbh_secure_agents import Expert

# Create expert with automatic memory - that's it!
expert = Expert(
    specialty="Research Specialist in AI Technology",
    objective="Conduct comprehensive research on AI implementations",
    background="Expert researcher with data analysis capabilities",
    memory_duration="auto",  # 👈 Everything automatic from here!
    user_id="researcher_001"
)
```

### Step 2: Use Normally - Memory Happens Automatically

```python
# Just process content - memory storage is completely automatic!
from tbh_secure_agents import Operation

operation = Operation(
    instructions="""
    Research AI-powered customer service automation.
    Focus on ROI data and implementation best practices.
    """,
    expected_output="Comprehensive research analysis",
    expert=expert  # 👈 Expert automatically stores important findings
)

# Execute - all important info is remembered automatically
result = operation.execute()

# The expert automatically remembers:
# - Research findings and data points
# - ROI statistics and trends  
# - Implementation best practices
# - Context for future operations
```
# - Product interest (wireless headphones)  
# - Customer communication style
# No manual memory calls needed!
```

### Step 3: Benefit from Automatic Context

```python
# Later conversation - expert automatically recalls previous context
later_operation = Operations(
    operation_name="Follow-up Support",
    operation_description="Continue helping customer", 
    expert=expert,  # Same expert with memory
    operation_steps=[
        "Recall customer's previous interests automatically",
        "Build on previous conversation context",
        "Provide personalized recommendations"
    ],
    expected_output="Personalized response using automatic memory"
)

# Expert automatically knows about the $200 budget and headphone interest!
result = later_operation.execute(inputs={
    "customer_message": "Do you have any sales on the headphones we discussed?"
})
```

---

## 🔧 Memory Duration Options

Choose how aggressively your Expert should remember information:

### `memory_duration="auto"` (Recommended)
- **What it does**: Framework automatically decides what's important to remember
- **Best for**: Most use cases - intelligent, balanced memory
- **Storage**: Persistent SQLite database
- **Behavior**: Remembers key information, decisions, and user preferences

```python
expert = Expert(
    expert_name="Smart Assistant",
    memory_enabled=True,
    memory_duration="auto"  # 👈 Smart automatic memory
)
```

### `memory_duration="long_term"`
- **What it does**: Remembers everything important for long-term use
- **Best for**: Customer service, personal assistants, learning applications
- **Storage**: Persistent SQLite database
- **Behavior**: Aggressive memory retention

```python
expert = Expert(
    expert_name="Personal Assistant", 
    memory_enabled=True,
    memory_duration="long_term"  # 👈 Remember everything important
)
```

### `memory_duration="short_term"`
- **What it does**: Remembers information only for current session
- **Best for**: Temporary tasks, privacy-sensitive applications
- **Storage**: In-memory (cleared when app restarts)
- **Behavior**: Session-only memory

```python
expert = Expert(
    expert_name="Session Helper",
    memory_enabled=True, 
    memory_duration="short_term"  # 👈 Session-only memory
)
```

### `memory_duration="disabled"`
- **What it does**: No automatic memory
- **Best for**: Stateless operations, high-privacy scenarios
- **Storage**: None
- **Behavior**: No memory retention

```python
expert = Expert(
    expert_name="Stateless Agent",
    memory_enabled=False,  # 👈 No memory
    memory_duration="disabled"
)
```

---

## 🎯 Real-World Examples

### Customer Service with Automatic Memory

```python
# Create customer service agent with automatic memory
customer_agent = Expert(
    expert_name="Customer Service Representative",
    description="Helpful customer service agent",
    instructions="""
    Provide excellent customer service by:
    - Understanding customer needs
    - Offering relevant solutions
    - Building rapport over time
    Memory will automatically track customer preferences and history.
    """,
    memory_enabled=True,
    memory_duration="long_term"  # Remember customers long-term
)

# First interaction
first_call = Operations(
    operation_name="Initial Customer Contact",
    expert=customer_agent,
    operation_steps=[
        "Greet customer professionally", 
        "Understand their needs",
        "Provide helpful information"
    ],
    expected_output="Helpful response with relationship building"
)

result1 = first_call.execute(inputs={
    "customer_message": "Hi, I'm John. I need help choosing a laptop for video editing."
})
# Automatically remembers: Customer name (John), need (video editing laptop)

# Second interaction (days later)
follow_up = Operations(
    operation_name="Follow-up Contact",
    expert=customer_agent,  # Same agent with memory
    operation_steps=[
        "Recognize returning customer",
        "Reference previous conversation", 
        "Provide continuous service"
    ],
    expected_output="Personalized follow-up using memory"
)

result2 = follow_up.execute(inputs={
    "customer_message": "Hi, it's John again. I'm ready to make that purchase."
})
# Agent automatically remembers John and the video editing laptop discussion!
```

### Personal Assistant with Learning

```python
# Personal assistant that learns your preferences
personal_assistant = Expert(
    expert_name="AI Personal Assistant",
    description="Smart personal assistant that learns and adapts",
    instructions="""
    Act as a helpful personal assistant that:
    - Learns user preferences over time
    - Adapts to communication style
    - Remembers important information automatically
    - Provides increasingly personalized assistance
    """,
    memory_enabled=True,
    memory_duration="auto"  # Intelligent memory management
)

# Morning routine help
morning_routine = Operations(
    operation_name="Morning Assistance",
    expert=personal_assistant,
    operation_steps=[
        "Greet user appropriately for time of day",
        "Provide relevant morning information",
        "Learn from user preferences"
    ],
    expected_output="Personalized morning assistance"
)

# Over time, the assistant automatically learns:
# - User's preferred wake-up time
# - Favorite news topics
# - Coffee preferences
# - Meeting patterns
# All without manual memory programming!
```

### Business Intelligence with Context

```python
# Business analyst that builds knowledge over time
business_analyst = Expert(
    expert_name="Business Intelligence Analyst",
    description="Data-driven business analyst",
    instructions="""
    Provide business intelligence by:
    - Analyzing data and trends
    - Building knowledge of business context
    - Connecting insights across time periods
    - Learning industry patterns automatically
    """,
    memory_enabled=True,
    memory_duration="long_term"  # Build long-term business knowledge
)

# Monthly analysis - agent automatically builds context over time
monthly_analysis = Operations(
    operation_name="Monthly Business Review",
    expert=business_analyst,
    operation_steps=[
        "Analyze current month data",
        "Compare with previous periods automatically",
        "Identify trends using accumulated knowledge",
        "Provide actionable insights"
    ],
    expected_output="Comprehensive business analysis with historical context"
)

# Each month, the analyst automatically remembers:
# - Previous analysis results
# - Seasonal patterns
# - Successful recommendations
# - Business context and decisions
```

---

## 🔐 Security and Privacy

Automatic memory includes built-in security:

### Encrypted Storage
- All automatic memory is encrypted at rest
- Secure key management
- No plaintext storage of sensitive information

### Access Controls
- Memory access tied to Expert identity
- Secure memory isolation between experts
- Configurable privacy levels

### Data Retention
- Automatic cleanup of old, irrelevant memories
- Configurable retention policies
- GDPR-compliant data handling

---

## 🛠️ Advanced Configuration

### Custom Memory Behavior

```python
# Fine-tune automatic memory behavior
expert = Expert(
    expert_name="Specialized Agent",
    memory_enabled=True,
    memory_duration="auto",
    security_profile=MinimalSecurity(),
    # Memory will automatically adapt to these instructions
    instructions="""
    Focus memory on:
    - User preferences and patterns
    - Successful interaction strategies  
    - Important business context
    - Learning from outcomes
    
    Avoid remembering:
    - Temporary session data
    - Sensitive personal information
    - One-time requests
    """
)
```

### Memory with Squad Operations

```python
from SecureAgents.squad import Squad

# Create squad where experts share automatic memory
research_squad = Squad(
    squad_name="Research Team",
    experts=[expert1, expert2, expert3],  # All with memory_enabled=True
    operations=[research_op, analysis_op, report_op],
    process_type="sequential",
    memory_enabled=True  # Enable squad-level memory sharing
)

# Squad automatically maintains context across all expert operations
result = research_squad.kickoff(inputs={"research_topic": "AI trends"})

# All experts automatically remember:
# - Research findings
# - Analysis insights  
# - Cross-expert collaboration patterns
# - Successful research strategies
```

---

## 🎉 Benefits of Automatic Memory

### For Developers
- **Zero Memory Management**: No manual `remember()` or `recall()` calls
- **Intelligent Context**: Framework decides what's important
- **Seamless Integration**: Works with existing Expert and Squad code
- **Production Ready**: Automatic error handling and optimization

### For Users  
- **Continuous Context**: Agents remember across conversations
- **Personalized Experience**: Automatic learning of preferences
- **Intelligent Assistance**: Context-aware responses
- **Natural Interactions**: No memory management overhead

### For Applications
- **Scalable**: Automatic optimization and cleanup
- **Secure**: Built-in encryption and access controls
- **Reliable**: Production-tested memory management
- **Flexible**: Adapts to different use cases automatically

---

## 🚀 Migration from Manual Memory

If you have existing code with manual `remember()` calls:

### Before (Manual)
```python
# Old manual approach
expert = Expert(expert_name="Agent", memory_enabled=True)

# Manual memory calls throughout code
expert.remember(content="User likes mornings", memory_type="LONG_TERM")
result = expert.recall(query="user preferences")
expert.remember(content="Successful strategy", memory_type="LONG_TERM")
```

### After (Automatic)
```python
# New automatic approach  
expert = Expert(
    expert_name="Agent", 
    memory_enabled=True,
    memory_duration="auto"  # 👈 Just enable automatic memory
)

# Remove all manual remember() and recall() calls
# Memory happens automatically during operations!
```

---

## 📋 Best Practices

1. **Use `memory_duration="auto"`** for most applications
2. **Enable memory at Expert creation** for best performance
3. **Write clear instructions** to guide what should be remembered
4. **Test memory behavior** in development environment
5. **Monitor memory usage** in production applications
6. **Use appropriate security profiles** for sensitive data

---

## 🔍 Troubleshooting

### Common Issues

**Q: Memory not working?**
- Ensure `memory_enabled=True` when creating Expert
- Check that `memory_duration` is not "disabled"
- Verify security profile allows memory operations

**Q: Too much memory usage?**
- Use `memory_duration="short_term"` for temporary tasks
- Consider `memory_duration="auto"` for intelligent management
- Review Expert instructions for memory guidance

**Q: Memory not accessible across sessions?**
- Use `memory_duration="long_term"` or `memory_duration="auto"`
- Avoid `memory_duration="short_term"` for persistent memory
- Check Expert identity consistency

---

## 📚 Next Steps

- [Memory Examples](memory_examples.md) - Real-world usage patterns
- [Security Guide](security_guide.md) - Memory security best practices  
- [Performance Guide](performance_optimization.md) - Memory optimization
- [API Reference](api_reference.md) - Complete memory API documentation

---

*The automatic memory system makes building intelligent, context-aware agents effortless. No memory management code required!*
