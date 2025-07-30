# Memory System Guide

## Overview

The SecureAgents framework includes a powerful memory system that enables your Expert agents to store, recall, and build upon information across conversations and operations. This guide provides comprehensive documentation on how to use the memory features effectively.

## Table of Contents

1. [Memory Types](#memory-types)
2. [Memory Duration Options](#memory-duration-options)
3. [Basic Usage](#basic-usage)
4. [Advanced Features](#advanced-features)
5. [Storage Backends](#storage-backends)
6. [Security and Encryption](#security-and-encryption)
7. [Best Practices](#best-practices)
8. [Examples](#examples)
9. [Troubleshooting](#troubleshooting)

---

## Memory Types

The framework supports several memory types for different use cases:

### MemoryType.LONG_TERM
- **Purpose**: Persistent storage across sessions
- **Use Case**: User preferences, important context, learned patterns
- **Storage**: SQLite database with encryption
- **Retention**: Permanent (until explicitly deleted)

```python
from tbh_secure_agents.memory.models import MemoryType

expert.remember(
    content="User prefers morning meetings and dislikes loud restaurants",
    memory_type=MemoryType.LONG_TERM
)
```

### MemoryType.SESSION
- **Purpose**: Temporary storage for current conversation
- **Use Case**: Current conversation context, temporary notes
- **Storage**: In-memory (RAM)
- **Retention**: Until session ends or application restarts

```python
expert.remember(
    content="User is currently planning a weekend trip to San Francisco",
    memory_type=MemoryType.SESSION
)
```

### MemoryType.AUTO
- **Purpose**: Framework automatically decides storage type
- **Use Case**: General-purpose memory when you want the system to optimize
- **Storage**: Mixed (important items go to SQLite, temporary to memory)
- **Retention**: Varies based on content importance

```python
expert.remember(
    content="User asked about restaurant recommendations",
    memory_type=MemoryType.AUTO
)
```

---

## Memory Duration Options

When creating an Expert, you can specify the memory duration to control default behavior:

### Available Options

| Duration | Description | Default Memory Type | Storage Backend | Max Entries |
|----------|-------------|-------------------|-----------------|-------------|
| `short_term` | Temporary memory only | SESSION | In-memory | 200 |
| `long_term` | Persistent memory | LONG_TERM | SQLite | 2000 |
| `auto` | Intelligent mixed storage | AUTO | SQLite + Memory | 1000 |
| `disabled` | No memory storage | None | None | 0 |

### Usage

```python
from tbh_secure_agents import Expert

# Long-term memory expert (recommended for most use cases)
expert = Expert(
    specialty="Personal Assistant",
    objective="Help users and remember their preferences",
    memory_duration="long_term"  # Enables persistent memory
)

# Short-term memory expert (for temporary tasks)
expert = Expert(
    specialty="Quick Calculator",
    objective="Perform calculations",
    memory_duration="short_term"  # Only session memory
)

# Auto-managed memory (intelligent storage)
expert = Expert(
    specialty="Research Assistant",
    objective="Help with research tasks",
    memory_duration="auto"  # Framework decides storage
)

# No memory (for stateless operations)
expert = Expert(
    specialty="Simple Converter",
    objective="Convert units",
    memory_duration="disabled"  # No memory storage
)
```

---

## Basic Usage

### Storing Memories

The `remember()` method stores information in the expert's memory:

```python
# Basic memory storage
memory_id = expert.remember(
    content="User wants to learn Python programming"
)

# With specific memory type
memory_id = expert.remember(
    content="User's favorite programming language is Python",
    memory_type=MemoryType.LONG_TERM
)

# With priority (affects retrieval order)
from tbh_secure_agents.memory.models import MemoryPriority

memory_id = expert.remember(
    content="IMPORTANT: User has a meeting at 2 PM tomorrow",
    memory_type=MemoryType.LONG_TERM,
    priority=MemoryPriority.HIGH
)

# With metadata for organization
memory_id = expert.remember(
    content="User completed Python basics course",
    memory_type=MemoryType.LONG_TERM,
    metadata={
        "category": "education",
        "subject": "python",
        "status": "completed"
    }
)
```

### Retrieving Memories

The `recall()` method searches and retrieves stored memories:

```python
# Basic memory recall
memories = expert.recall(
    query="Python programming",
    limit=5
)

# With specific memory type
memories = expert.recall(
    query="user preferences",
    memory_type=MemoryType.LONG_TERM,
    limit=10
)

# Process retrieved memories
for memory in memories:
    print(f"Content: {memory.content}")
    print(f"Timestamp: {memory.timestamp}")
    print(f"Metadata: {memory.metadata}")
```

---

## Advanced Features

### Memory Priorities

Control the importance and retrieval order of memories:

```python
from tbh_secure_agents.memory.models import MemoryPriority

# High priority (appears first in searches)
expert.remember(
    content="User is allergic to peanuts",
    priority=MemoryPriority.HIGH
)

# Normal priority (default)
expert.remember(
    content="User likes Italian food",
    priority=MemoryPriority.NORMAL
)

# Low priority (appears last in searches)
expert.remember(
    content="User mentioned the weather was nice",
    priority=MemoryPriority.LOW
)
```

### Metadata and Organization

Use metadata to organize and filter memories:

```python
# Store with categories
expert.remember(
    content="User completed project X successfully",
    metadata={
        "type": "achievement",
        "project": "project_x",
        "date": "2025-06-05",
        "status": "completed"
    }
)

# Store personal preferences
expert.remember(
    content="User prefers email over phone calls",
    metadata={
        "type": "preference",
        "category": "communication",
        "importance": "high"
    }
)
```

### Continuous Conversations

Build context across multiple conversation sessions:

```python
# Session 1: Store initial context
expert.remember(
    content="User is planning a vacation to Europe in July",
    memory_type=MemoryType.LONG_TERM,
    metadata={"session": "1", "topic": "vacation_planning"}
)

# Session 2: Add more details
expert.remember(
    content="User wants to visit Paris and Rome, budget is $3000",
    memory_type=MemoryType.LONG_TERM,
    metadata={"session": "2", "topic": "vacation_details"}
)

# Session 3: Recall previous context
vacation_context = expert.recall(
    query="vacation Europe Paris Rome",
    memory_type=MemoryType.LONG_TERM,
    limit=10
)

# Use context in operations
operation = Operation(
    instructions=f"Based on previous conversations about the Europe vacation, provide a detailed itinerary for Paris and Rome within the $3000 budget.",
    expert=expert
)
```

---

## Storage Backends

### SQLite Storage (Long-term Memory)
- **File Location**: `memory_user_{user_id}_{duration}.db`
- **Encryption**: AES-256 encryption for all content
- **Search**: Full-text search capabilities
- **Performance**: Optimized for frequent reads
- **Backup**: Database files can be backed up

### In-Memory Storage (Session Memory)
- **Storage**: Python dictionaries in RAM
- **Speed**: Fastest access times
- **Limitation**: Lost when application restarts
- **Use Case**: Temporary conversation context

### Hybrid Storage (Auto Mode)
- **Logic**: Important content → SQLite, temporary → memory
- **Benefits**: Best of both worlds
- **Automatic**: Framework handles storage decisions

---

## Security and Encryption

### Data Protection

All long-term memories are automatically encrypted:

```python
# Content is automatically encrypted when stored
expert.remember(
    content="Sensitive user information",
    memory_type=MemoryType.LONG_TERM
)
# Stored as: "eyJlbmNyeXB0ZWRfY29udGVudCI6..."

# Content is automatically decrypted when retrieved
memories = expert.recall(query="sensitive information")
# Returns: "Sensitive user information"
```

### Access Control

Memory access is controlled by the security profile:

```python
from tbh_secure_agents.security_models.minimal_security import MinimalSecurity

expert = Expert(
    specialty="Personal Assistant",
    objective="Help users",
    security_profile=MinimalSecurity(),  # Controls memory access
    memory_duration="long_term"
)
```

### User Isolation

Each user gets isolated memory storage:

- Memories are tied to user IDs
- Users cannot access each other's memories
- Memory files are separate per user

---

## Best Practices

### 1. Choose Appropriate Memory Duration

```python
# For chatbots and personal assistants
memory_duration="long_term"

# For calculation tools and converters
memory_duration="short_term"

# For research and analysis tools
memory_duration="auto"

# For stateless microservices
memory_duration="disabled"
```

### 2. Use Descriptive Content

```python
# Good: Descriptive and searchable
expert.remember(
    content="User John Smith prefers morning meetings at 9 AM and works in the marketing department",
    metadata={"user": "john_smith", "type": "preference"}
)

# Avoid: Vague or unclear
expert.remember(content="User likes meetings")
```

### 3. Organize with Metadata

```python
expert.remember(
    content="Project Alpha milestone 1 completed on schedule",
    metadata={
        "project": "alpha",
        "milestone": "1",
        "status": "completed",
        "date": "2025-06-05"
    }
)
```

### 4. Use Appropriate Priorities

```python
# Critical information
expert.remember(
    content="User has severe allergy to shellfish",
    priority=MemoryPriority.HIGH
)

# General preferences
expert.remember(
    content="User likes Italian restaurants",
    priority=MemoryPriority.NORMAL
)

# Minor details
expert.remember(
    content="User mentioned it was raining today",
    priority=MemoryPriority.LOW
)
```

### 5. Regular Memory Cleanup

```python
# For high-volume applications, consider periodic cleanup
# (This is handled automatically by the framework based on max_entries)
```

---

## Examples

### Personal Assistant Example

```python
from tbh_secure_agents import Expert
from tbh_secure_agents.memory.models import MemoryType, MemoryPriority

# Create assistant with long-term memory
assistant = Expert(
    specialty="Personal Assistant",
    objective="Help with daily tasks and remember user preferences",
    memory_duration="long_term"
)

# Store user preferences
assistant.remember(
    content="User wakes up at 6 AM and prefers morning workouts",
    priority=MemoryPriority.HIGH,
    metadata={"type": "daily_routine"}
)

assistant.remember(
    content="User's favorite coffee shop is Blue Bottle on Main Street",
    priority=MemoryPriority.NORMAL,
    metadata={"type": "preference", "category": "food"}
)

# Later, recall preferences for recommendations
morning_routine = assistant.recall(
    query="morning workout routine",
    limit=5
)

coffee_preferences = assistant.recall(
    query="coffee shop favorite",
    limit=3
)
```

### Customer Service Example

```python
# Create customer service expert
service_expert = Expert(
    specialty="Customer Service",
    objective="Provide personalized customer support",
    memory_duration="auto"
)

# Store customer interaction history
service_expert.remember(
    content="Customer ID 12345 had billing issue resolved on 2025-06-01. Refund of $50 processed.",
    metadata={
        "customer_id": "12345",
        "issue_type": "billing",
        "resolution": "refund",
        "amount": 50,
        "date": "2025-06-01"
    }
)

# Recall customer history in future interactions
customer_history = service_expert.recall(
    query="customer 12345 billing",
    limit=10
)
```

### Research Assistant Example

```python
# Research assistant with intelligent memory
researcher = Expert(
    specialty="Research Assistant",
    objective="Help with academic and business research",
    memory_duration="auto"
)

# Store research findings
researcher.remember(
    content="Study from MIT shows AI adoption in healthcare increased 300% in 2024",
    priority=MemoryPriority.HIGH,
    metadata={
        "source": "MIT",
        "topic": "AI healthcare",
        "year": "2024",
        "type": "statistic"
    }
)

# Recall for literature reviews
ai_healthcare_studies = researcher.recall(
    query="AI healthcare adoption statistics",
    limit=20
)
```

---

## Troubleshooting

### Common Issues

#### 1. Memory Not Storing

**Problem**: `remember()` returns None or fails

**Solutions**:
```python
# Check memory duration setting
expert = Expert(
    specialty="Assistant",
    objective="Help users",
    memory_duration="long_term"  # Ensure not "disabled"
)

# Verify content is not empty
expert.remember(content="Valid content here")  # Not empty string
```

#### 2. Cannot Recall Memories

**Problem**: `recall()` returns empty list

**Solutions**:
```python
# Check memory type matches
expert.remember(content="Test", memory_type=MemoryType.LONG_TERM)
memories = expert.recall(query="Test", memory_type=MemoryType.LONG_TERM)

# Use broader search terms
memories = expert.recall(query="test content", limit=10)

# Check if memories exist
all_memories = expert.recall(query="", limit=100)  # Get all memories
```

#### 3. Access Control Issues

**Problem**: "Access validation failed" errors

**Solutions**:
```python
# Ensure proper security profile
from tbh_secure_agents.security_models.minimal_security import MinimalSecurity

expert = Expert(
    specialty="Assistant",
    objective="Help users",
    security_profile=MinimalSecurity(),
    memory_duration="long_term"
)
```

#### 4. Performance Issues

**Problem**: Slow memory operations

**Solutions**:
```python
# Use appropriate limits
memories = expert.recall(query="search", limit=10)  # Not 1000

# Use specific memory types
memories = expert.recall(
    query="search",
    memory_type=MemoryType.LONG_TERM,  # More efficient than AUTO
    limit=5
)
```

### Debug Information

Enable debug mode to see memory operations:

```python
import os
os.environ['DEBUG_MEMORY'] = 'true'

# Memory operations will now show debug output
expert.remember(content="Debug test")
```

### Database File Locations

Memory database files are stored as:
- `memory_user_{user_id}_longterm.db` - Long-term memories
- `memory_user_{user_id}_auto.db` - Auto-managed memories

### Getting Help

For additional support:
1. Check the [FAQ](faq.md)
2. Review [Best Practices](best_practices.md)
3. See [Examples](../examples/)
4. Check framework logs for error details

---

## Version Information

- **Memory System Version**: 5.0
- **Framework Compatibility**: SecureAgents v0.4+
- **Last Updated**: June 5, 2025

For version-specific changes, see [Version Changes](version_changes.md).
