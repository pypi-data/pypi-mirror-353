# Memory Quick Start Guide

Get started with SecureAgents memory in 5 minutes using the AI Research example.

## 🚀 Quick Setup

```python
import os
from tbh_secure_agents import Expert

# Set your API key
os.environ["GOOGLE_API_KEY"] = "your_api_key_here"

# Create an expert with memory
expert = Expert(
    specialty="Research Specialist",
    objective="Conduct AI research",
    background="Expert researcher",
    memory_duration="long_term",    # 🧠 ChromaDB backend
    user_id="research_001"          # Required for persistence
)
```

## 📝 Store & Recall Memories

```python
# Store domain knowledge
expert.remember(
    content="AI automation ROI typically 200-400% in first year",
    memory_type="LONG_TERM"
)

# Recall related information
memories = expert.recall("AI automation ROI", limit=3)
for memory in memories:
    print(f"📋 {memory.get('content', '')}")
```

## 🔧 Memory Types

| Type | Backend | Use Case | Example |
|------|---------|----------|---------|
| `long_term` | ChromaDB | Persistent knowledge | Domain expertise, user preferences |
| `auto` | ChromaDB | Automatic memory | Zero-config conversation memory |
| `working` | ChromaDB | Session context | Current task notes |

## 💡 Quick Examples

### Research Expert with Persistent Memory
```python
research_expert = Expert(
    specialty="AI Research Specialist",
    memory_duration="long_term",
    user_id="researcher_001"
)

# Store industry insights
research_expert.remember(
    "Key AI implementation challenges: data integration, staff training, adoption",
    memory_type="LONG_TERM"
)
```

### Content Writer with Style Memory
```python
writer = Expert(
    specialty="Content Writer", 
    memory_duration="auto",        # Automatic memory management
    user_id="writer_001"
)

# Memory automatically stored during conversations
```

### Multi-Agent Team with Shared Knowledge
```python
# Each expert has specialized memory
team = [
    Expert(specialty="Researcher", memory_duration="long_term", user_id="team_researcher"),
    Expert(specialty="Writer", memory_duration="long_term", user_id="team_writer"),
    Expert(specialty="Editor", memory_duration="long_term", user_id="team_editor")
]

# Store team knowledge
team[0].remember("Research methodology: focus on ROI and implementation")
team[1].remember("Writing style: balance technical details with strategic insights") 
team[2].remember("Editorial focus: clarity, engagement, accuracy")
```

## 🔍 Memory Status Check

```python
# Verify memory is working
if expert.memory_enabled:
    print("✅ Memory enabled")
    
    # Test storage
    memory_id = expert.remember("Test content", memory_type="WORKING")
    if memory_id != "memory_disabled":
        print("✅ Memory storage working")
        
        # Test recall
        memories = expert.recall("test", limit=1)
        print(f"✅ Found {len(memories)} memories")
```

## 🗂️ ChromaDB Storage

Memory is stored in ChromaDB vector database:

```
./chroma_db_{user_id}/
├── memory_{user_id}_longterm    # Persistent memories
├── memory_{user_id}_working     # Session memories  
└── memory_{user_id}_auto       # Auto memories
```

## 🔧 Common Patterns

### Knowledge Base Expert
```python
kb_expert = Expert(
    specialty="Knowledge Base Specialist",
    memory_duration="long_term",
    user_id="kb_specialist"
)

# Build knowledge base
knowledge_items = [
    "AI ROI best practices: measure efficiency gains, cost savings, revenue impact",
    "Implementation timeline: 3-6 months for basic automation, 12+ for advanced AI",
    "Success factors: executive buy-in, staff training, gradual rollout"
]

for item in knowledge_items:
    kb_expert.remember(item, memory_type="LONG_TERM")
```

### Automatic Context Expert
```python
context_expert = Expert(
    specialty="Context-Aware Assistant",
    memory_duration="auto"    # Zero configuration needed
)

# Memory automatically managed during conversations
# No manual remember() calls required
```

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| `memory_disabled` returned | Check `memory_duration` is not "disabled" |
| No memories found | Verify `user_id` matches between store/recall |
| Import errors | Ensure `pip install tbh-secure-agents` completed |
| ChromaDB errors | Check write permissions in current directory |

## 📚 Next Steps

1. **Full Tutorial**: [Memory Usage with AI Research Example](memory_usage_with_ai_research_example.md)
2. **Advanced Features**: [Memory Guide](memory_guide.md)
3. **Production Setup**: [Security Guide](security_guide.md)
4. **Examples**: Run the AI Research Content Creation team example

---

🎯 **Ready to build memory-enabled agents!** Start with the patterns above and explore the full AI Research example for advanced usage.
