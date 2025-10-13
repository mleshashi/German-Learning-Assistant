# German Learning Assistant 🇩🇪

AI-powered German language learning app with multi-agent architecture.


## Architecture Overview

```
┌──────────────────────────────┐
│        Streamlit UI          │
│  (User interacts with app)   │
└─────────────┬────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│      GermanLearningOrchestrator             │
│  (Coordinates lesson generation & agents)   │
└───────┬───────────────────────┬─────────────┘
        │                       │
        ▼                       ▼
┌───────────────┐      ┌──────────────────────┐
│ProgressTracker│      │    Multi-Agents      │
│(Tracks user   │      │- Grammar Agent       │
│ progress &    │      │- Vocabulary Agent    │
│ plans lessons)│      │- Conversation Agent  │
└───────────────┘      └──────────────────────┘
        │                       │
        └─────────────┬─────────┘
                      ▼
      ┌─────────────────────────────┐
      │   Personalized Daily Lesson │
      │   (Generated for user)      │
      └─────────────────────────────┘
```

## Features

- Streamlit dashboard for personalized lessons
- Progress tracking and daily lesson generation
- Grammar, vocabulary, and conversation agents

## Work in Progress

- UI improvements
- Memory cache (Redis & ChromaDB)
- Multi-user scaling

*This project is under active development. Stay tuned for updates!*