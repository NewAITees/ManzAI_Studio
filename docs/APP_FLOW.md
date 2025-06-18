# APP_FLOW.md

# ManzAI Studio Application Flow

This document describes the user flows and screen transitions in ManzAI Studio, focusing on the user experience rather than technical implementation.

## Overview

ManzAI Studio follows a simple, linear flow where users:
1. Enter a topic
2. Generate a manzai script
3. View and listen to the performance

```mermaid
graph LR
    A[Enter Topic] --> B[Generate Script]
    B --> C[View Performance]
    C --> D[Save/Export]
    C --> E[Modify Settings]
    E --> B
    D --> A
```

## User Journey Map

```mermaid
journey
    title ManzAI Studio User Journey
    section Initial Setup
        Install application: 3: User
        Launch application: 5: User
    section Content Creation
        Enter topic: 5: User
        Generate script: 3: System
        View script: 4: User
        Watch performance: 5: User
    section Customization
        Adjust settings: 3: User
        Select different characters: 4: User
        Customize prompts: 2: User
    section Export
        Save performance: 3: User
        Configure for streaming: 2: User
```

## Main Screens and Transitions

### Home Screen

The home screen is the main interface where users input topics and generate content.

**Elements:**
- Topic input field
- Generation button
- Character display area
- Settings menu access

**Actions:**
- Enter topic → Generate script
- Access settings → Navigate to Settings screen
- Select model → Model selection view

```mermaid
graph TD
    Home[Home Screen] --> Generate[Generate Script]
    Home --> Settings[Settings Screen]
    Generate --> Performance[Performance View]
    Settings --> ModelSettings[Character Model Settings]
    Settings --> PromptSettings[Prompt Template Settings]
```

### Performance View

After script generation, the application shows the performance with animated characters and audio.

**Elements:**
- Live2D character displays
- Script text display
- Playback controls
- Settings access

**Actions:**
- Play/pause performance
- Restart performance
- Return to home for new generation
- Access display settings

```mermaid
sequenceDiagram
    participant User
    participant UI as User Interface
    participant Audio as Audio System
    participant Animation as Character Animation

    User->>UI: Click Play button
    UI->>Audio: Start audio playback
    UI->>Animation: Sync character animation

    loop For each line in script
        Audio->>Animation: Trigger mouth movements
        Animation->>UI: Update character display
        UI->>User: Show current line highlight
    end

    Audio->>UI: Playback complete
    UI->>Animation: Reset characters
    UI->>User: Show replay option
```

### Settings Screen

The settings screen allows users to customize the application behavior.

**Elements:**
- Character model selection
- Voice settings
- Prompt template management
- Display options

**Actions:**
- Select character models → Update character display
- Modify prompts → Save prompt template
- Adjust display settings → Update display configuration
- Return to home screen

```mermaid
graph TD
    Settings[Settings Screen] --> Characters[Character Selection]
    Settings --> Voices[Voice Settings]
    Settings --> Prompts[Prompt Management]
    Settings --> Display[Display Options]

    Characters --> CharacterList[Character List]
    CharacterList --> CharacterDetail[Character Detail]
    CharacterDetail --> UpdateCharacter[Update Character]

    Prompts --> PromptList[Prompt List]
    PromptList --> PromptEdit[Edit Prompt]
    PromptList --> PromptCreate[Create Prompt]
    PromptEdit --> SavePrompt[Save Prompt]
    PromptCreate --> SavePrompt
```

## Key User Scenarios

### Scenario 1: First-time User

```mermaid
sequenceDiagram
    participant User
    participant App

    User->>App: Open application
    App->>User: Display home screen
    User->>App: Enter topic "Travel"
    User->>App: Click Generate
    App->>User: Show loading indicator
    Note over App: Generate script using default models/prompts
    App->>User: Display generated script
    App->>User: Play audio with character animation
    User->>App: Watch performance
```

### Scenario 2: Customizing Characters

```mermaid
sequenceDiagram
    participant User
    participant App
    participant Settings

    User->>App: Open application
    App->>User: Display home screen
    User->>App: Click Settings
    App->>Settings: Open settings screen
    User->>Settings: Select Character tab
    Settings->>User: Display character options
    User->>Settings: Select different character model
    Settings->>App: Update character configuration
    User->>Settings: Return to home
    User->>App: Enter topic
    User->>App: Generate and view with new character
```

### Scenario 3: Creating Custom Prompt

```mermaid
sequenceDiagram
    participant User
    participant App
    participant Settings
    participant PromptEditor

    User->>App: Open application
    App->>User: Display home screen
    User->>App: Click Settings
    App->>Settings: Open settings screen
    User->>Settings: Select Prompts tab
    Settings->>User: Display prompt list
    User->>Settings: Click "Create New Prompt"
    Settings->>PromptEditor: Open prompt editor
    User->>PromptEditor: Enter prompt name and content
    User->>PromptEditor: Save prompt
    PromptEditor->>Settings: Update prompt list
    User->>Settings: Return to home
    User->>App: Select custom prompt from dropdown
    User->>App: Generate using custom prompt
```

### Scenario 4: Streaming Setup

```mermaid
sequenceDiagram
    participant User
    participant App
    participant Settings
    participant OBS as "OBS/Streaming Software"

    User->>App: Open application
    App->>User: Display home screen
    User->>App: Click Settings
    App->>Settings: Open settings screen
    User->>Settings: Select Display tab
    User->>Settings: Enable "Streaming Mode"
    User->>Settings: Set background to chroma key green
    User->>Settings: Open display window
    Settings->>User: Open separate display window
    User->>OBS: Add window capture
    User->>OBS: Apply chroma key filter
    User->>App: Return to main window
    User->>App: Generate content
    App->>OBS: Display characters in stream window
```

## Error Handling Flows

### Script Generation Error

```mermaid
sequenceDiagram
    participant User
    participant App
    participant LLM

    User->>App: Enter topic
    User->>App: Click Generate
    App->>LLM: Request script generation
    LLM-->>App: Return error
    App->>User: Display error message
    App->>User: Show retry option
    User->>App: Click Retry
    App->>LLM: Retry script generation
```

### Voice Synthesis Error

```mermaid
sequenceDiagram
    participant User
    participant App
    participant VoiceVox

    User->>App: Play generated script
    App->>VoiceVox: Request voice synthesis
    VoiceVox-->>App: Return error
    App->>User: Display error message
    App->>User: Continue with partial audio
    Note over App,User: App plays available audio and shows missing parts in script
```

### Internet Connection Check

```mermaid
flowchart TD
    A[Start Application] --> B{Check Dependencies}
    B -->|Missing| C[Show Setup Guide]
    B -->|Available| D[Enable Features]

    C --> E{Install Missing}
    E -->|Success| D
    E -->|Fail| F[Limited Mode]

    subgraph "Error Handling"
    F --> G[Show Offline Features]
    G --> H[Provide Troubleshooting]
    end

    D --> I[Normal Operation]
```

## Decision Points and Flow Control

```mermaid
flowchart TD
    A[User Input] --> B{Input Valid?}
    B -->|Yes| C[Process Input]
    B -->|No| D[Show Error]
    D --> A

    C --> E{Model Available?}
    E -->|Yes| F[Generate Script]
    E -->|No| G[Show Model Error]
    G --> H[Offer Alternatives]
    H --> E

    F --> I{Generation Success?}
    I -->|Yes| J[Display Results]
    I -->|No| K[Show Generation Error]
    K --> L{Retry?}
    L -->|Yes| F
    L -->|No| A

    J --> M{Play Performance?}
    M -->|Yes| N[Play Audio/Animation]
    M -->|No| A

    N --> O{Voice Error?}
    O -->|Yes| P[Show Voice Error]
    O -->|No| Q[Complete Performance]
    P --> R[Continue with Text Only]
    R --> Q
    Q --> A
```

## Mobile Device Flow Differences

For mobile devices, the application flow is adjusted to accommodate smaller screens:

```mermaid
graph TD
    A[Home Screen] --> B[Input Topic]
    B --> C[Generate]
    C --> D[Script View]
    D --> E[Performance View]

    subgraph "Mobile Adaptations"
    F[Tabbed Interface]
    G[Simplified Controls]
    H[Portrait Orientation Focus]
    end

    F --> A
    G --> E
    H --> D
```

## User Preferences and Settings Flow

```mermaid
graph TD
    A[Settings Screen] --> B[User Preferences]
    B --> C{Save Preferences}
    C -->|Success| D[Apply Settings]
    C -->|Failure| E[Show Error]

    B --> F[Character Models]
    F --> G[Preview Model]
    G --> H{Accept Model}
    H -->|Yes| I[Update Character]
    H -->|No| F

    B --> J[Voice Settings]
    J --> K[Preview Voice]
    K --> L{Accept Voice}
    L -->|Yes| M[Update Voice]
    L -->|No| J

    B --> N[Prompt Templates]
    N --> O[Edit Template]
    O --> P{Save Template}
    P -->|Success| Q[Update Prompts]
    P -->|Failure| R[Show Error]
```

## Performance and Resource Management

The application monitors resource usage and adapts accordingly:

```mermaid
graph TD
    A[Monitor Resources] --> B{Resource Check}
    B -->|Normal| C[Full Features]
    B -->|Limited| D[Optimize Performance]

    D --> E[Reduce Animation Quality]
    D --> F[Simplify Audio Processing]
    D --> G[Use Smaller Models]

    C --> H[Normal Operation]
    E --> I[Degraded Operation]
    F --> I
    G --> I

    I --> J[Notify User]
    J --> K[Suggest Optimizations]
```

## Conclusion

This document provides a comprehensive overview of the user flows in ManzAI Studio. Understanding these flows helps in developing a cohesive and intuitive user experience. The application is designed to guide users through the process of creating, customizing, and enjoying AI-generated manzai performances, with appropriate error handling and adaptation to different usage scenarios.
