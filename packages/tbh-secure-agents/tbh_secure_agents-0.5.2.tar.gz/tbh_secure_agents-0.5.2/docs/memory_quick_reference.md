# Memory System Quick Reference

## TL;DR - Start Here

```python
from tbh_secure_agents import Expert
from tbh_secure_agents.memory.models import MemoryType, MemoryPriority

# 1. Create expert with memory
expert = Expert(
    specialty="Personal Assistant",
    objective="Help users",
    memory_duration="long_term"  # Enable persistent memory
)

# 2. Store important information
expert.remember(
    content="User prefers morning meetings",
    priority=MemoryPriority.HIGH
)

# 3. Recall information later
memories = expert.recall(query="morning meetings", limit=5)
```

## Memory Duration Cheat Sheet

| Use Case | Duration | Storage | Best For |
|----------|----------|---------|----------|
| 🤖 **Chatbots/Assistants** | `long_term` | SQLite | User preferences, history |
| 🔢 **Calculators/Tools** | `short_term` | Memory | Temporary calculations |
| 🔬 **Research/Analysis** | `auto` | Mixed | Smart storage decisions |
| ⚡ **Microservices** | `disabled` | None | Stateless operations |

## Common Patterns

### Store User Preferences
```python
expert.remember(
    content="User likes Italian food and morning workouts",
    memory_type=MemoryType.LONG_TERM,
    priority=MemoryPriority.HIGH,
    metadata={"type": "preference"}
)
```

### Build Conversation Context
```python
# Session 1
expert.remember(content="User planning trip to Paris")

# Session 2 - recall and build
previous = expert.recall(query="Paris trip", limit=5)
expert.remember(content="User wants to visit Eiffel Tower and Louvre")
```

### Customer Service Memory
```python
expert.remember(
    content="Customer John had billing issue resolved",
    metadata={
        "customer": "john",
        "issue": "billing",
        "status": "resolved"
    }
)
```

## Memory Types Quick Guide

- **LONG_TERM** → Persistent, encrypted, survives restarts
- **SESSION** → Temporary, fast, lost on restart  
- **AUTO** → Framework decides (recommended for most cases)

## Priority Levels

- **HIGH** → Critical info (allergies, important dates)
- **NORMAL** → Regular info (preferences, general context)
- **LOW** → Minor details (weather comments, casual mentions)

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Nothing stores | Set `memory_duration="long_term"` |
| Can't recall | Use broader search terms |
| Access errors | Use `MinimalSecurity()` profile |
| Slow performance | Limit recall results (`limit=10`) |

## Security Notes

- ✅ All long-term memory is encrypted
- ✅ Users can't access each other's memories
- ✅ Memory access controlled by security profiles

## File Locations

- **SQLite DBs**: `memory_user_{id}_longterm.db`
- **Debug Mode**: Set `DEBUG_MEMORY=true`

---

**Need more details?** See the [Complete Memory Guide](memory_guide.md)
