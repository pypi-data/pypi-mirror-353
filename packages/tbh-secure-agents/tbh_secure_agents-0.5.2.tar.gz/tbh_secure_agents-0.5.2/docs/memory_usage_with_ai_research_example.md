# Memory System Tutorial: AI Research Content Creation Team

This comprehensive tutorial demonstrates how to use the SecureAgents memory system through a real-world example: building an AI Research Content Creation Team with persistent memory capabilities.

## 🎯 What You'll Learn

- How to enable different memory types for Expert agents
- When to use `long_term`, `auto`, and `working` memory
- How memory enhances multi-agent workflows
- Best practices for storing and retrieving memories
- Using ChromaDB for vector-based memory storage

## 📋 Prerequisites

```bash
# Ensure you have your API key set
export GOOGLE_API_KEY="your_api_key_here"

# Install SecureAgents (if not already installed)
pip install tbh-secure-agents
```

## 🚀 Complete Example: AI Research Team with Memory

Let's build a 3-agent research team where each agent has specialized memory for their role:

### Step 1: Create Memory-Enabled Expert Agents

```python
import os
from tbh_secure_agents import Expert, Operation, Squad

# Set your API key
os.environ["GOOGLE_API_KEY"] = "your_api_key_here"

# 1. Research Specialist with Long-Term Memory
research_specialist = Expert(
    specialty="Research Specialist in {research_domain}",
    objective="Conduct comprehensive research on {research_topic}",
    background="Expert researcher with access to industry data",
    security_profile="minimal",
    memory_duration="long_term",    # 🧠 Persistent memory across sessions
    user_id="research_specialist_001"
)

# 2. Content Writer with Long-Term Memory  
content_writer = Expert(
    specialty="Content Writer specializing in {content_domain}",
    objective="Transform research into {content_type} for {target_audience}",
    background="Skilled at creating engaging business content",
    security_profile="minimal",
    memory_duration="long_term",    # 🧠 Remembers writing preferences
    user_id="content_writer_001"
)

# 3. Content Editor with Long-Term Memory
content_editor = Expert(
    specialty="Content Editor specializing in business content",
    objective="Review and enhance content ensuring publication quality",
    background="Expert editor focusing on clarity and engagement",
    security_profile="minimal", 
    memory_duration="long_term",    # 🧠 Learns editorial patterns
    user_id="content_editor_001"
)
```

### Step 2: Store Specialized Knowledge in Memory

```python
# Store domain expertise in Research Specialist's memory
print("📝 Storing specialized knowledge...")

# Long-term facts and insights
research_specialist.remember(
    content="AI customer service automation ROI typically ranges 200-400% within first year",
    memory_type="LONG_TERM"
)

research_specialist.remember(
    content="Key implementation challenges include data integration, staff training, and customer adoption",
    memory_type="LONG_TERM"
)

# Content Writer's style preferences
content_writer.remember(
    content="Business executives prefer content that balances technical details with strategic implications",
    memory_type="WORKING"
)

content_writer.remember(
    content="Most effective business content includes concrete ROI data and implementation timelines",
    memory_type="WORKING"
)

print("✅ Knowledge successfully stored in expert memories")
```

### Step 3: Create Operations That Leverage Memory

```python
# Research Operation - will access stored industry knowledge
research_operation = Operation(
    instructions="""
    Conduct thorough research on {research_topic} in the {research_domain} field.
    
    Research Requirements:
    - Provide comprehensive analysis including trends, challenges, and opportunities
    - Focus on {research_focus}
    - Include current market statistics and ROI data
    - Identify key players and innovations
    - Analyze implementation challenges and best practices
    
    Use your stored knowledge about industry insights and combine with new research.
    Target Audience: {target_audience}
    """,
    expected_output="Comprehensive research analysis on {research_topic}",
    expert=research_specialist,
    result_destination="outputs/research_team/01_research_analysis.md"
)

# Writing Operation - will use style preferences from memory
writing_operation = Operation(
    instructions="""
    Create a compelling {content_type} based on the research findings.
    
    Content Guidelines:
    - Structure: Introduction, main content with clear sections, recommendations, conclusion
    - Include specific data and ROI information from research
    - Balance technical details with strategic implications (from memory)
    - Target Audience: {target_audience}
    - Writing Style: {writing_style}
    - Include concrete implementation timelines and ROI data
    
    Apply your learned preferences about effective business content structure.
    """,
    expected_output="Well-structured {content_type} about {research_topic}",
    expert=content_writer,
    result_destination="outputs/research_team/02_content_draft.md"
)

# Editing Operation - applies learned editorial patterns
editing_operation = Operation(
    instructions="""
    Review and enhance the content ensuring exceptional quality.
    
    Editorial Focus:
    - Improve clarity, flow, and readability
    - Verify all facts and data accuracy  
    - Enhance reader engagement and content appeal
    - Ensure consistent tone for {target_audience}
    - Apply quality standards: {quality_standards}
    
    Use your editorial experience and learned patterns to polish the content.
    """,
    expected_output="Publication-ready {content_type}",
    expert=content_editor,
    result_destination="outputs/research_team/03_final_content.md"
)
```

### Step 4: Create Squad and Execute with Memory Integration

```python
# Create the research team squad
research_team_squad = Squad(
    experts=[research_specialist, content_writer, content_editor],
    operations=[research_operation, writing_operation, editing_operation],
    process="sequential",
    security_profile="minimal",
    result_destination="outputs/research_team/team_workflow_summary.json"
)

# Define the research project parameters
guardrails = {
    "research_topic": "AI-powered customer service automation",
    "research_domain": "business technology", 
    "research_focus": "ROI analysis and implementation best practices",
    "content_type": "strategic implementation guide",
    "content_domain": "business technology strategy",
    "writing_style": "clear and engaging",
    "target_audience": "C-level executives and IT decision makers",
    "quality_standards": "publication-ready with clear structure and compelling narrative"
}

# Execute the workflow - memory will be used throughout
print("🚀 Executing Research Team Workflow with Memory Integration...")

try:
    # Create outputs directory
    os.makedirs("outputs/research_team", exist_ok=True)
    
    # Deploy the squad
    result = research_team_squad.deploy(guardrails=guardrails)
    
    print("🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
    print(f"Squad Result: {result[:200]}...")
    
except Exception as e:
    print(f"❌ Error: {e}")
```

### Step 5: Demonstrate Memory Recall

```python
# Test memory recall capabilities
print("\n🔍 Demonstrating Memory Recall...")

# Research Specialist recalls industry data
print("💡 Research Specialist recalling ROI information:")
roi_memories = research_specialist.recall("ROI customer service", limit=3)
for i, memory in enumerate(roi_memories, 1):
    content = memory.get('content', 'No content')
    print(f"   {i}. {content[:100]}...")

# Content Writer recalls style preferences  
print("\n✏️ Content Writer recalling writing preferences:")
writing_memories = content_writer.recall("business content executives", limit=2)
for i, memory in enumerate(writing_memories, 1):
    content = memory.get('content', 'No content')
    print(f"   {i}. {content[:100]}...")
```

## 🧠 Memory Types Explained

### Long-Term Memory (`memory_duration="long_term"`)
- **Backend**: ChromaDB vector database
- **Encryption**: Yes, all content encrypted before storage
- **Persistence**: Survives application restarts
- **Use Cases**: Domain expertise, user preferences, learned patterns
- **Storage Location**: `./chroma_db_{user_id}/` directory

```python
# Expert with long-term memory
expert = Expert(
    specialty="Domain Expert",
    memory_duration="long_term",  # Persistent across sessions
    user_id="expert_001"
)

# Store persistent knowledge
expert.remember(
    content="Domain-specific insight that should persist",
    memory_type="LONG_TERM"
)
```

### Auto Memory (`memory_duration="auto"`)
- **Backend**: ChromaDB vector database  
- **Behavior**: Automatically stores conversation context
- **Use Cases**: Hands-off memory management
- **Benefits**: Zero manual memory management required

```python
# Expert with automatic memory
expert = Expert(
    specialty="Auto Expert", 
    memory_duration="auto"  # Automatically manages memory
)
# No manual remember() calls needed - memory happens automatically!
```

### Working Memory (`memory_type="WORKING"`)
- **Backend**: ChromaDB vector database
- **Scope**: Current session/task context
- **Use Cases**: Temporary notes, current task context

```python
expert.remember(
    content="Temporary context for current task",
    memory_type="WORKING"
)
```

## 🔧 Memory Configuration Options

### Basic Configuration
```python
# Minimal setup
expert = Expert(
    specialty="Your Expert",
    memory_duration="long_term",  # or "auto", "short_term", "disabled"
    user_id="unique_user_id"     # Required for memory persistence
)
```

### Advanced Configuration
```python
# With custom memory settings
expert = Expert(
    specialty="Advanced Expert",
    memory_duration="long_term",
    user_id="advanced_user",
    security_profile="standard",    # Enhanced security
    # Memory automatically uses ChromaDB backend
)
```

## 📊 Memory Storage Backend: ChromaDB

The SecureAgents memory system uses ChromaDB for intelligent vector-based storage:

### Features:
- **Vector Embeddings**: Content stored as searchable embeddings
- **Semantic Search**: Find related memories by meaning, not just keywords  
- **Encryption**: All content encrypted before storage
- **Persistence**: Data survives application restarts
- **Collections**: Organized by user and memory type

### Storage Locations:
```
./chroma_db_{user_id}/               # ChromaDB database directory
├── memory_{user_id}_longterm        # Long-term memory collection
├── memory_{user_id}_working         # Working memory collection  
└── memory_{user_id}_auto           # Auto memory collection
```

## 💡 Best Practices

### 1. Choose Appropriate Memory Duration
```python
# For persistent domain knowledge
research_expert = Expert(memory_duration="long_term")

# For automatic conversation management  
assistant_expert = Expert(memory_duration="auto")

# For temporary task context
task_expert = Expert(memory_duration="short_term")
```

### 2. Use Descriptive User IDs
```python
# Good: Descriptive and unique
expert = Expert(user_id="customer_service_specialist_v1")

# Avoid: Generic or non-unique
expert = Expert(user_id="user1")
```

### 3. Store Relevant Context
```python
# Good: Specific, actionable information
expert.remember(
    content="Customer prefers email communication over phone calls, timezone: PST",
    memory_type="LONG_TERM"
)

# Avoid: Vague or overly broad information
expert.remember(
    content="Customer likes stuff",
    memory_type="LONG_TERM" 
)
```

### 4. Use Semantic Search for Recall
```python
# Good: Search by meaning and context
memories = expert.recall("customer communication preferences", limit=5)

# Works: Related concepts will be found
memories = expert.recall("how user likes to be contacted", limit=5)
```

## 🔍 Debugging Memory Issues

### Check Memory Status
```python
# Verify memory is enabled
if expert.memory_enabled:
    print("✅ Memory is enabled")
else:
    print("❌ Memory is disabled")

# Check memory manager
if expert.memory_manager:
    print("✅ Memory manager initialized")
else:
    print("❌ Memory manager not found")
```

### Test Memory Storage
```python
# Test basic memory operations
memory_id = expert.remember("Test memory content", memory_type="WORKING")
if memory_id != "memory_disabled":
    print(f"✅ Memory stored with ID: {memory_id}")
else:
    print("❌ Memory storage failed")
```

### Check Storage Directory
```python
import os

user_id = expert.user_id
chroma_dir = f"./chroma_db_{user_id}"

if os.path.exists(chroma_dir):
    print(f"✅ ChromaDB directory exists: {chroma_dir}")
    files = os.listdir(chroma_dir)
    print(f"Contents: {files}")
else:
    print(f"❌ ChromaDB directory not found: {chroma_dir}")
```

## 🚀 Next Steps

1. **Run the Complete Example**: Copy the AI Research team code above and run it
2. **Experiment with Memory Types**: Try different `memory_duration` settings
3. **Explore Advanced Features**: Check out [Memory Examples](memory_examples.md)
4. **Production Deployment**: Review [Security Guide](security_guide.md) for production settings

## 📚 Related Documentation

- [Memory Quick Reference](memory_quick_reference.md) - Quick syntax reference
- [Automatic Memory Guide](automatic_memory_guide.md) - Zero-config memory management
- [Security Profiles](security_profiles_guide.md) - Memory security settings
- [Best Practices](best_practices.md) - Framework best practices

---

🎉 **You now have a complete understanding of how to use memory in SecureAgents!** The AI Research Content Creation team example shows how memory transforms simple agents into intelligent assistants that learn and remember across conversations.
