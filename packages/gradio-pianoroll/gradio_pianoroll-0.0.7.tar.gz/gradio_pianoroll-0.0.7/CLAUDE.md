# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Frontend Development
```bash
cd frontend
npm install                    # Install dependencies
npm run dev                   # Development server with hot reload
npm run build                 # Build production frontend
npm run check                 # TypeScript type checking
```

### Backend Development
```bash
pip install -e .              # Install package in development mode
pip install -r demo/requirements.txt  # Install demo dependencies
```

### Demo Application
```bash
cd demo
python app.py                 # Run Gradio demo application
```

### Package Building
```bash
python -m build              # Build Python package
```

## Architecture Overview

### Frontend Architecture

The frontend is a Svelte-based Gradio custom component with a sophisticated **canvas-based layer rendering system**:

#### Component Hierarchy
- `PianoRoll.svelte` - Main coordinator component
- `GridComponent.svelte` - Central editing area using layer system
- `KeyboardComponent.svelte` - Piano keyboard interface
- `TimeLineComponent.svelte` - Timeline with beats/measures
- `Toolbar.svelte` - Playback and editing controls

#### Layer System (`/frontend/utils/layers/`)
The core rendering uses a Z-ordered layer system:
- `GridLayer` (Z: 10) - Background grid and piano key highlighting
- `WaveformLayer` (Z: 20) - Audio waveform visualization
- `LineLayer` (Z: 25) - Dynamic curves (F0, loudness, pitch)
- `NotesLayer` (Z: 30) - Piano roll notes with lyrics
- `PlayheadLayer` (Z: 50) - Playback position indicator

Each layer renders independently for performance optimization.

#### Audio Engine System
**Dual audio architecture** supporting both synthesis and playback:
- `AudioEngine` - Web Audio API synthesis with ADSR envelopes
- `BackendAudioEngine` - Pre-rendered audio playback from backend
- `KeyboardAudioEngine` - Lightweight keyboard preview audio

#### Timing System (`/frontend/utils/flicks.ts`)
Uses **Facebook's Flicks** (1/705,600,000 second) for precise musical timing:
- Avoids floating-point errors in audio/MIDI synchronization
- Supports conversion between beats, seconds, pixels, MIDI ticks, and audio samples
- All notes store timing in multiple formats simultaneously

### Backend Architecture

The backend is a **Gradio custom component** in Python:

#### Core Structure
- `PianoRoll` class extends `gradio.components.base.Component`
- Supports comprehensive timing data with multiple representations
- Integrates backend audio, curve data (F0, loudness), and timing segments
- Provides bidirectional data processing (preprocess/postprocess)

#### Key Features
- **Multi-format timing**: pixels, flicks, seconds, beats, MIDI ticks, audio samples
- **Backend data overlay**: Optional audio analysis data integration
- **Event system**: change, input, play, pause, stop, clear events
- **Timing utilities**: Comprehensive conversion functions in `timing_utils.py`

## Key Patterns

### Note Data Structure
Notes contain multiple timing representations:
```typescript
{
  start: number,           // Pixels (visual)
  startFlicks: number,     // Flicks (precise)
  startSeconds: number,    // Audio timing
  startBeats: number,      // Musical timing
  startTicks: number,      // MIDI compatibility
  startSample: number,     // Audio samples
  // ... duration fields follow same pattern
}
```

### Layer Rendering Pattern
1. Each layer implements `BaseLayer` interface
2. `LayerManager` coordinates all layers with Z-ordering
3. Only visible layers are rendered for performance
4. Independent opacity and visibility controls per layer

### Component Communication
- **Props down, events up** - Standard Svelte pattern
- **Custom events** for inter-component communication  
- **Reactive statements** for automatic UI updates
- **Audio callbacks** for playback synchronization

### Backend Integration
The component supports optional backend data:
```python
PianoRoll(
    value=note_data,
    audio_data="base64_or_url",           # Backend audio
    curve_data={"f0": [...], "loudness": [...]},  # Analysis curves
    segment_data=[...],                   # Timing segments
    use_backend_audio=True               # Audio engine selection
)
```

## Important Implementation Notes

- **Canvas performance**: All main visualization uses HTML5 Canvas for hardware acceleration
- **Memory management**: Audio engines use singleton pattern to prevent memory leaks
- **Type safety**: Full TypeScript typing throughout frontend
- **Viewport optimization**: Only render visible elements during scroll
- **Event-driven updates**: Changes propagate through reactive event system
- **Modular architecture**: Easy to extend with new layer types or audio engines