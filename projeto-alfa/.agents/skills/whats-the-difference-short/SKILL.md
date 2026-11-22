---
name: whats-the-difference-short
description: "Create viral-style educational comparison Shorts with bold example images, an expressive stickman presenter, fast pacing, energetic Kokoro narration, and a data-driven Remotion timeline."
---

# What's the Difference Shorts Skill

## Core Frameworks

### Five-Scene Formula
Use this structure for every comparison Short:

1. **This is X** — one bold example image + stickman pointing
2. **This is Y** — matching layout with example
3. **What's the difference?** — questioning pose + both examples
4. **Visual explanation of X** — short animation
5. **Visual contrast for Y** — direct comparison

### Design Principles
- Large typography
- White meme-style canvas
- Expressive poses
- Immediate hook (0-3s)
- Rapid scene changes (every 2-4s)

## Key Concepts

| Term | Definition |
|------|------------|
| **Stickman** | Visual format character (can be any gender) |
| **Kokoro** | TTS voice engine for narration |
| **Remotion** | Video rendering framework |
| **Video ID** | Unique identifier for each production |

## Quick Reference

### Scene Timing
- Scene 1: 0-4s
- Scene 2: 4-8s
- Scene 3: 8-12s
- Scene 4: 12-20s
- Scene 5: 20-30s

### Installation
```bash
npx skills add SalimLouDev/whats-the-difference-shorts-skill
```

### Usage
```text
Create a Short about empathy vs. sympathy.
Create one Short for strategy vs. tactics and correlation vs. causation.
```

## File Structure
```
public/videos/<video-id>/
├── narration.mp3
├── source-record.txt
├── assets/
├── scenes/ (PNG/JPG frames)
├── timing.json
├── publish-copy.md
└── output.mp4
```

## Requirements
- Node.js 18+
- Python 3.10-3.12 (Kokoro)
- Git
- FFmpeg (optional)

## License
MIT — User responsible for media rights and platform policies