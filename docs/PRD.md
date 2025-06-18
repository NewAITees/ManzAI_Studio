# Project Requirements Document: Local Manzai Generator Web Application

## 1. Introduction

This document outlines the requirements for developing a web application that generates manzai (Japanese comedy) scripts using Ollama's Large Language Models (LLMs). The application will display animated anime characters using Live2D and generate voice output using VoiceVox. The entire application will run locally on the user's machine, requiring no internet connection after initial setup.

## 2. Project Objectives

- Create a web application that generates manzai scripts based on user-provided topics
- Implement Live2D character animations with synchronized mouth movements
- Generate voice audio using VoiceVox for the script dialogue
- Ensure all components run locally without requiring internet connection
- Provide a simple, intuitive user interface for topic input

## 3. User Requirements

### 3.1 Target Users
- Users interested in Japanese manzai comedy
- Users who want to see anime-style characters perform comedy routines
- Users who prefer applications that run locally without internet dependency

### 3.2 User Stories
- As a user, I want to input a topic and have the system generate a manzai script
- As a user, I want to see animated characters performing the generated script
- As a user, I want to hear voice acting that matches the script and character animations
- As a user, I want the application to run locally on my machine

## 4. Functional Requirements

### 4.1 User Input
- The application must provide a web form for users to input topics
- The system must validate and process user inputs

### 4.2 Script Generation
- The application must use Ollama's LLM (Phi-3 or Mistral recommended) to generate manzai scripts
- Scripts must follow a standard manzai format with two characters (tsukkomi and boke roles)
- The prompt should specify "Characters A and B performing manzai about [topic]"

### 4.3 Character Display
- The application must display Live2D character models
- Characters must have animations for mouth movements synchronized with audio
- Basic facial expressions should be implemented

### 4.4 Voice Output
- The application must use VoiceVox to generate voice for each line of dialogue
- Voice models appropriate for anime characters should be available (e.g., Shikoku Metan, Zundamon)
- Audio must be synchronized with character animations

### 4.5 Synchronization
- The application must synchronize script generation, visual display, and audio output
- Simple synchronization should start with opening the mouth when voice starts and closing when it ends
- More detailed lip-syncing can be added as needed using mora timing from VoiceVox

## 5. Technical Requirements

### 5.1 Development Framework
- The application will be built using Flask as a local web server
- Flask was chosen over Pygame because:
  - Live2D has better web integration with its Web SDK
  - Web applications provide better cross-platform compatibility
  - Live2D's web performance is optimized
  - Documentation and tools are more abundant for web development

### 5.2 Integration Components

#### 5.2.1 Ollama LLM
- Ollama must be installed locally
- Recommended models: Phi-3 (best for creative text) or Mistral
- Model comparison:
  | Model | Features | Suitability for Manzai |
  |-------|----------|------------------------|
  | Phi-3 | Lightweight, strong at creative text | High |
  | Mistral | Versatile, good for longer texts | Medium |
  | Llama 2 | Good for general tasks, medium creativity | Medium |
- Python integration using subprocess to call Ollama

#### 5.2.2 Live2D
- Live2D Cubism SDK for Web will be used
- Character models must be stored locally
- JavaScript implementation for character display and animation
- Parameters for mouth movements must be properly defined

#### 5.2.3 VoiceVox
- Local installation of VoiceVox is required
- Voice models must be downloaded and stored locally
- Python wrapper (e.g., pyvoicevox) will be used for integration
- Generated audio files will be stored locally and served by Flask

### 5.3 Hardware Requirements
- Storage: Sufficient for Ollama models (e.g., Phi-3: 2.2GB), VoiceVox voice models, and Live2D models
- Processing: CPU/GPU capable of running the LLM locally
- Memory: Sufficient for running all components simultaneously

### 5.4 Software Architecture
- Flask backend for server functionality and API endpoints
- JavaScript frontend for user interface and Live2D display
- Local file system for storing models and generated content
- Communication between components via Flask routes and JSON data

## 6. Implementation Details

### 6.1 Web Interface
```html
<!-- Sample HTML structure -->
<div id="input-form">
  <form method="POST" action="/generate">
    <input type="text" name="topic" placeholder="Enter a topic for manzai">
    <button type="submit">Generate</button>
  </form>
</div>

<div id="character-display">
  <div id="live2d" style="width: 512px; height: 512px;"></div>
</div>

<div id="controls">
  <button id="play-button">Play Manzai</button>
</div>
```

### 6.2 Live2D Integration
```javascript
// Sample JavaScript for Live2D integration
var live2d = new Live2D("live2d");
live2d.loadModel("path/to/model.json");

// Mouth movement control
function updateMouth(value) {
  live2d.setParamFloat("ParamMouthOpenY", value);
}

// Synchronize with audio
audioElement.addEventListener("play", () => updateMouth(1.0));
audioElement.addEventListener("ended", () => updateMouth(0.0));
```

### 6.3 Flask Backend Routes
```python
@app.route('/generate', methods=['POST'])
def generate_script():
    topic = request.form['topic']

    # Generate script with Ollama
    script = generate_manzai_script(topic)

    # Generate audio with VoiceVox
    audio_files = generate_audio(script)

    return jsonify({
        'script': script,
        'audio_files': audio_files
    })
```

## 7. Development Process

### 7.1 Setup Phase
1. Install Ollama and download appropriate LLM (Phi-3 or Mistral)
2. Set up Flask development environment
3. Install and configure VoiceVox locally
4. Prepare Live2D models and integration

### 7.2 Development Phase
1. Create basic Flask application with user input form
2. Implement Ollama integration for script generation
3. Add VoiceVox integration for voice generation
4. Implement Live2D display in the web interface
5. Develop synchronization between voice and animations

### 7.3 Testing Phase
1. Test script generation quality with various topics
2. Verify voice generation and pronunciation
3. Test animation synchronization
4. Performance testing on target hardware

## 8. Potential Challenges and Solutions

### 8.1 Live2D Animation Control
**Challenge**: Controlling mouth movements in Live2D can be complex.
**Solution**: Start with simple open-closed animations and gradually add more detailed lip-syncing as development progresses.

### 8.2 Script Quality
**Challenge**: LLM may not consistently generate high-quality comedy scripts.
**Solution**: Optimize prompts and compare multiple models (e.g., Phi-3 vs. Mistral) to identify the best performer.

### 8.3 Synchronization Precision
**Challenge**: Visual and audio timing may not align perfectly.
**Solution**: Use JavaScript event listeners for audio playback events and refine timing through testing.

### 8.4 Local Performance
**Challenge**: Running all components locally may strain system resources.
**Solution**: Optimize model selection and consider hardware requirements during development.

## 9. Conclusion

This web application utilizing Flask, Ollama, Live2D, and VoiceVox will enable users to generate and view manzai performances with animated characters based on user-provided topics. All components will run locally, eliminating the need for internet connection after initial setup. The application leverages web technologies to provide cross-platform compatibility and optimal performance for character animation through Live2D.

## 10. References

- Ollama Official Site
- Ollama GitHub Repository
- Live2D Official Site
- VoiceVox Official Site
- Enhance your writing skills with Ollama and Phi3
- Reddit: Best models for novel writing
