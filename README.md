# AI Memory System

A lightweight AI memory system built as part of my **AI System Design learning journey**.

The primary goal of this project was not to build a large production application, but to understand **how memory is designed and integrated into AI systems** through hands-on implementation.

## 🎯 Goal

Build an AI assistant that can:

- Maintain short-term conversation context
- Store useful long-term user memories
- Retrieve relevant memories using semantic search
- Decide what information is worth remembering
- Manage memory lifecycle and context limits

## 🏗️ Architecture

```text
                         User
                          │
                          ▼
                       FastAPI
                          │
             ┌────────────┴────────────┐
             ▼                         ▼
      Short-Term Memory        Memory Retrieval
      (Session History)        (Semantic Search)
             │                         │
             └────────────┬────────────┘
                          ▼
                         LLM
                          │
                          ▼
                  Memory Extraction
                          │
                     Should Save?
                      /        \
                    YES         NO
                     │           │
                     ▼           X
              Memory Storage
                /        \
               ▼          ▼
            SQLite      Chroma
```

## 🧠 Key Design Concepts

- **Short-Term vs Long-Term Memory** — session context vs persistent user information
- **Semantic Memory Retrieval** — embeddings + vector similarity search
- **Retrieval-Augmented Memory** — retrieving relevant user memories before generating a response
- **Memory Extraction** — deciding whether a message is worth remembering
- **Structured LLM Output** — predictable memory extraction decisions
- **Memory Normalization** — converting conversations into concise memories
- **Conditional Persistence** — avoiding unnecessary memory storage
- **Top-K Retrieval** — limiting memories injected into the LLM context
- **User Isolation** — memories are scoped by `user_id`
- **Memory Lifecycle** — creating, updating, and deactivating memories
- **Storage vs Retrieval Separation** — SQLite as persistent storage and Chroma for semantic retrieval
- **Context Management** — controlling memory size and token usage

## 🛠️ Tech Stack

- Python
- FastAPI
- LangChain
- Groq
- SQLite
- SQLAlchemy
- Chroma
- Hugging Face Embeddings
- Pydantic

## 📚 Project Phases

### Phase 1 — Basic Conversation Memory

Session-based conversation history and short-term context.

### Phase 2 — Long-Term Memory

Persistent user memories using SQLite and `user_id`.

### Phase 3 — Semantic Memory Retrieval

Embeddings, vector storage, similarity search, and Top-K retrieval.

### Phase 4 — Intelligent Memory Management

Memory extraction, relevance decisions, normalization, and conditional persistence.

### Phase 5 — Production-Oriented Architecture

Memory lifecycle, metadata, user isolation, soft deletion, configurable limits, and basic observability.


## 🔄 Example

```text
User:
"I prefer Python over Java."

        ↓

Memory Extraction

        ↓

"User prefers Python over Java."

        ↓

SQLite + Chroma

        ↓

New Conversation

User:
"What language should I use for my next project?"

        ↓

Semantic Retrieval

        ↓

"User prefers Python over Java."

        ↓

       LLM

        ↓

Personalized Response

```

## 🎓 Learning Objective

This project was intentionally kept **small and focused**.

The objective was to understand **AI Memory Architecture** and the system-design decisions behind it, rather than introduce unnecessary infrastructure or build a large production platform.

The main progression was:

```text
Conversation Context
        ↓
Persistent Memory
        ↓
Semantic Retrieval
        ↓
Intelligent Memory Extraction
        ↓
Memory Lifecycle Management
```

