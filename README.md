# GitTranslate

A full-stack web app for translating and localizing content using OpenAI’s APIs.  
GitTranslate lets you:

- **Fetch and browse** Git repositories (GitHub, GitLab)
- **Translate** code comments, filenames, and documentation into your chosen language via GPT-3.5 Turbo
- **(Bonus)** Upload podcast or other audio files to **transcribe** with Whisper, **translate** the transcript, and **synthesize** new audio in the target language
- **Deploy** easily: frontend on Vercel, backend on any Python-friendly host (Heroku, AWS, etc.)
- **Automate** workflows with the included Orkes FE script

<br />

## Demo

Live at: [git-translate-indol.vercel.app](https://git-translate-indol.vercel.app)

<br />

## Features

- **Frontend**: Next.js + React + TypeScript + Tailwind CSS  
- **Backend**: Python (FastAPI)  
- **Audio**: Whisper for transcription, TTS for speech synthesis  
- **Translation**: OpenAI GPT-3.5 Turbo for text translation  
- **Workflow**: `scripts/orkes-fe-script.py` for Orkes integration  
- **Configurable**: .env-driven, ready for local or cloud deployment  

<br />

## Table of Contents

1. [Getting Started](#getting-started)  
2. [Prerequisites](#prerequisites)  
3. [Installation](#installation)  
4. [Configuration](#configuration)  
5. [Running Locally](#running-locally)  
6. [Deployment](#deployment)  
7. [Project Structure](#project-structure)  
8. [Contributing](#contributing)  
9. [License](#license)  

<br />

---

## Getting Started

### Prerequisites

- **Node.js** v16+  
- **Python** 3.9+  
- A valid **OpenAI API Key**

### Installation

1. **Clone** this repo  
   ```bash
   git clone https://github.com/sakshat-patil/GitTranslate.git
   cd GitTranslate
