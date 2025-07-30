# Automatic Memory - Quick Reference

## 🚀 TL;DR - Just Enable It!

```python
# That's it! Memory is now automatic
expert = Expert(
    expert_name="Your Agent",
    memory_enabled=True,
    memory_duration="auto"  # Framework handles everything
)
```

---

## 📋 Memory Duration Options

| Duration | Behavior | Storage | Best For |
|----------|----------|---------|----------|
| `"auto"` | Smart automatic | SQLite | **Most use cases** |
| `"long_term"` | Remember everything | SQLite | Customer service, learning |
| `"short_term"` | Session only | Memory | Temporary tasks |
| `"disabled"` | No memory | None | Stateless operations |

---

## ✅ What Happens Automatically

### ✅ Automatically Remembered
- User preferences and patterns
- Important conversation context
- Successful strategies and outcomes
- Key decisions and insights
- Cross-conversation continuity

### ✅ Automatically Optimized
- Memory storage and retrieval
- Context relevance scoring
- Storage cleanup and optimization
- Security and encryption
- Performance management

### ✅ Automatically Secured
- End-to-end encryption
- Access control validation
- Secure key management
- Privacy protection
- Data isolation

---

## 🎯 Common Patterns

### Customer Service Agent
```python
customer_agent = Expert(
    expert_name="Customer Service Rep",
    memory_enabled=True,
    memory_duration="long_term",  # Remember customers
    instructions="Provide helpful customer service and build relationships"
)
# Automatically remembers customer preferences, history, and context
```

### Personal Assistant
```python
assistant = Expert(
    expert_name="Personal Assistant", 
    memory_enabled=True,
    memory_duration="auto",  # Smart memory management
    instructions="Learn user preferences and provide personalized assistance"
)
# Automatically learns and adapts to user patterns
```

### Business Analyst
```python
analyst = Expert(
    expert_name="Business Analyst",
    memory_enabled=True, 
    memory_duration="long_term",  # Build knowledge base
    instructions="Analyze data and build business intelligence over time"
)
# Automatically builds business context and historical insights
```

---

## 🚫 What You DON'T Need

### ❌ Manual Memory Calls
```python
# OLD WAY - Don't do this anymore!
expert.remember(content="...", memory_type="LONG_TERM")
memories = expert.recall(query="...")
```

### ❌ Memory Management Code
```python
# OLD WAY - Framework handles this automatically!
if important_info:
    expert.remember(content=important_info)
    
context = expert.recall(query=user_query)
if context:
    # Use context in response
```

### ❌ Complex Memory Logic
```python
# OLD WAY - No longer needed!
def should_remember(content):
    # Complex logic to decide what to remember
    
def clean_old_memories():
    # Manual memory cleanup
```

---

## 🔧 Squad with Automatic Memory

```python
from SecureAgents.squad import Squad

# All experts with automatic memory
squad = Squad(
    squad_name="Research Team",
    experts=[expert1, expert2, expert3],  # All have memory_enabled=True
    operations=[research_op, analysis_op, report_op],
    memory_enabled=True  # Squad-level memory sharing
)

# Squad automatically maintains context across all operations
result = squad.kickoff(inputs={"topic": "AI trends"})
```

---

## 🎛️ Fine-Tuning Through Instructions

```python
expert = Expert(
    expert_name="Specialized Agent",
    memory_enabled=True,
    memory_duration="auto",
    instructions="""
    Your automatic memory should focus on:
    ✅ User preferences and communication style
    ✅ Successful problem-solving approaches  
    ✅ Important business context and decisions
    ✅ Patterns that improve future interactions
    
    Avoid automatically remembering:
    ❌ Temporary session data
    ❌ Sensitive personal information
    ❌ One-time password or security info
    """
)
```

---

## 🔍 Verification

### Check if Memory is Working
```python
# Create expert with memory
expert = Expert(
    expert_name="Test Agent",
    memory_enabled=True,
    memory_duration="auto"
)

# Run an operation
operation = Operations(
    operation_name="Test Operation",
    expert=expert,
    operation_steps=["Process user input", "Learn from interaction"],
    expected_output="Response with automatic learning"
)

result = operation.execute(inputs={"user_message": "I prefer morning meetings"})

# Memory automatically stored! No manual calls needed.
# Next operation will automatically have this context.
```

---

## 🚀 Migration Guide

### From Manual to Automatic

#### Before
```python
expert = Expert(expert_name="Agent", memory_enabled=True)

# Manual memory throughout code
expert.remember(content="User data", memory_type="LONG_TERM")
context = expert.recall(query="user preferences") 
expert.remember(content="New insight", memory_type="LONG_TERM")
```

#### After  
```python
expert = Expert(
    expert_name="Agent",
    memory_enabled=True,
    memory_duration="auto"  # 👈 Just add this!
)

# Remove ALL manual remember() and recall() calls
# Memory happens automatically!
```

---

## 🆘 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Memory not working | Add `memory_enabled=True, memory_duration="auto"` |
| Too much memory | Use `memory_duration="short_term"` |
| No persistence | Change from `"short_term"` to `"auto"` or `"long_term"` |
| Performance issues | Use `memory_duration="auto"` for optimization |

---

## 🎉 Benefits

- **Zero Code Changes** - Just enable and forget
- **Intelligent Context** - Framework decides what's important  
- **Production Ready** - Automatic optimization and security
- **Scalable** - Handles memory management automatically
- **Secure** - Built-in encryption and access controls

---

*Automatic memory makes intelligent agents effortless - no memory management required!*
