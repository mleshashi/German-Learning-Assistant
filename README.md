# German Learning Assistant 🇩🇪

AI-powered German language learning system with multi-agent architecture using completely free APIs.

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   German         │    │  Memory Cache   │
│ Learning Portal │────│  Orchestrator    │────│ Redis +ChromaDB │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
            ┌──────────┐ ┌─────────────┐ ┌──────────────┐
            │Grammar   │ │Vocabulary   │ │Conversation  │
            │Master    │ │Builder      │ │Practice      │
            │Agent     │ │Agent        │ │Agent         │
            └──────────┘ └─────────────┘ └──────────────┘
                    │           │           │
                    ▼           ▼           ▼
            ┌──────────┐ ┌─────────────┐ ┌──────────────┐
            │Groq Free │ │Wiktionary   │ │Text-to-Speech│
            │MCP Server│ │Free MCP     │ │Free MCP      │
            │          │ │Server       │ │Server        │
            └──────────┘ └─────────────┘ └──────────────┘
```

## Features

### Specialized German Learning Agents

- **Grammar Master Agent**: Explains German articles (der/die/das), cases, and verb conjugations
- **Vocabulary Builder Agent**: Breaks down compound words, teaches word families, handles A1-C2 levels
- **Conversation Practice Agent**: Simulates real German conversations with cultural context