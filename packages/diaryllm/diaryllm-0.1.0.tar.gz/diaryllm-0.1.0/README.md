# DiaryLLM

**Personal Journaling and Diary Management for Large Language Models**

[![PyPI version](https://badge.fury.io/py/diaryllm.svg)](https://badge.fury.io/py/diaryllm)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

THIS PACKAGE IS A PLACEHOLDER FOR A WORK IN PROGRESS. DO NOT PAY TOO MUCH ATTENTION FOR NOW.

## Overview

DiaryLLM is a Python library designed to enable Large Language Models to maintain personal journals and diaries across conversations and over time. While LLMs excel at understanding and generating text within a single conversation, they typically lose all personal context and learned preferences once the session ends. DiaryLLM solves this by providing a structured approach to personal memory management.

## The Problem

Large Language Models face several challenges in maintaining personal relationships and context:

- **Session Isolation**: Each new conversation starts with zero personal context
- **Context Window Limitations**: Long conversations hit token limits, losing personal details
- **No Personal Learning**: Insights about user preferences and personality are lost
- **Inefficient Repetition**: Users must re-explain personal details, preferences, and history
- **Lack of Continuity**: No ability to build upon previous personal interactions or maintain ongoing relationships

## The Solution

DiaryLLM provides a comprehensive personal journaling layer for LLM applications, enabling:

### 🧠 **Personal Context Storage**
- Store and retrieve personal conversations and interactions
- Maintain user preferences, personality insights, and learned patterns
- Preserve personal context and ongoing relationships

### 🔍 **Intelligent Personal Retrieval**
- Semantic search through personal conversation history
- Context-aware personal memory selection based on current topics
- Automatic relevance scoring and filtering for personal information

### 🔗 **Seamless Integration**
- Framework-agnostic design works with any LLM provider
- Simple API that integrates with existing applications
- Minimal code changes required for existing projects

### 📊 **Personal Memory Management**
- Configurable personal memory retention policies
- Automatic personal context compression and summarization
- Privacy controls and personal data lifecycle management

## Key Features

- **Personal Multi-Modal Memory**: Store personal text, preferences, documents, and structured data
- **Personal Vector-Based Search**: Semantic similarity search for personal contextual retrieval
- **Personal Memory Hierarchies**: Organize personal memories by importance, recency, and emotional relevance
- **Privacy-First**: Local storage options with encryption for personal data
- **Scalable Architecture**: From simple file storage to enterprise personal databases
- **Personal Analytics**: Insights into personal memory usage and relationship patterns

## Quick Start

```python
from diaryllm import DiaryManager, PersonalMemory

# Initialize personal diary manager
diary = DiaryManager(storage_path="./personal_diary")

# Store personal conversation context
diary.store_personal_interaction(
    user_id="user_123",
    messages=[...],
    metadata={"mood": "happy", "topic": "career", "relationship_context": "friend"}
)

# Retrieve relevant personal context for new conversation
personal_context = diary.retrieve_personal_context(
    user_id="user_123",
    query="How is my career going?",
    max_results=5
)

# Continue conversation with personal memory
llm_response = your_llm.chat(
    messages=personal_context + new_messages
)
```

## Use Cases

### 🤖 **Personal AI Assistants**
- Maintain user personality profiles and communication styles
- Remember personal projects and their emotional significance
- Build upon previous personal problem-solving sessions

### 💻 **Personal Development**
- Preserve personal growth context and milestone decisions
- Remember personal debugging patterns and solutions
- Maintain personal coding standards and preferences

### 📚 **Personal Knowledge Management**
- Store and retrieve personal research findings and insights
- Build cumulative understanding of personal interests
- Connect related personal concepts across conversations

### 🎯 **Personalized Applications**
- Learn individual user behavior and emotional patterns
- Adapt responses based on personal historical interactions
- Provide consistent personalized experience across sessions

## Architecture

DiaryLLM is built with personal privacy and flexibility in mind:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Application   │    │   DiaryLLM      │    │Personal Storage │
│                 │◄──►│                 │◄──►│                 │
│  Your LLM App   │    │Personal Manager │    │ Personal DB     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Storage Backends
- **Local Files**: Simple JSON/pickle storage for personal development
- **SQLite**: Structured storage with personal SQL queries
- **Vector Databases**: Chroma, Pinecone, Weaviate support for personal vectors
- **Cloud Storage**: S3, GCS, Azure Blob integration for personal data

### Memory Types
- **Personal Episodic Memory**: Specific personal conversation episodes
- **Personal Semantic Memory**: Extracted personal knowledge and concepts  
- **Personal Procedural Memory**: Learned personal processes and workflows
- **Personal Meta Memory**: Memory about personal memory usage patterns

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Laurent-Philippe Albou**  
*June 5th, 2025*

---

*DiaryLLM: Because every personal conversation should build upon the relationship.*