# NLP Mock Interview Bot

An AI-powered mock interview platform with two modes: a **behavioral interview bot** (Gradio, notebook-based) and a **real-time technical interview platform** (full-stack web app). Both use voice-to-voice interaction powered by OpenAI's Whisper and TTS APIs.

**Tech Stack (Tools):** Python, FastAPI, LangChain, OpenAI GPT-4, Whisper, Next.js, TypeScript, Material UI, Monaco Editor, WebSockets, Gradio

---

## Project Structure
```
Mock-Interview-Project/
├── mock-interview-behavioural-platform/   # Behavioral interview bot (Gradio + Colab)
│   └── Mock_interview_final_changed_to_whisperAI.ipynb
└── mock-interview-platform/              # Technical interview web app
    ├── backend/
    │   ├── main.py                        # FastAPI WebSocket server
    │   └── test_prompts.py                # Interview question generation tests
    └── frontend/                          # Next.js + TypeScript UI
        └── src/app/
            ├── page.tsx                   # Landing page
            └── interview/page.tsx         # Interview interface
```

---

## Platform 1: Behavioral Interview Bot

Gradio-based bot that conducts a personalized behavioral interview from any job posting URL.

- Scrapes the job URL to extract the role summary
- Fetches company core values via GPT-4o
- Generates a tailored interview intro and conducts a multi-turn behavioral interview using LangChain `ConversationBufferMemory`
- Transcribes candidate voice responses via Groq (Whisper)
- Evaluates each response against the job's required technologies and competencies
- Speaks responses aloud using OpenAI TTS API (voice: `fable`)
- Dark-themed Gradio UI

---

## Platform 2: Real-Time Technical Interview (Full-Stack)

A full-stack web app that conducts a live DSA coding interview over WebSockets with voice and code submission.

**Backend (FastAPI)**
- WebSocket endpoint handles the full interview loop in real time
- GPT-4-turbo drives the conversation: greeting → LeetCode-style coding question → approach discussion → code evaluation → structured feedback
- Coding questions are automatically detected and displayed as text-only (not spoken) while the follow-up is spoken aloud
- OpenAI Whisper (`whisper-1`) transcribes user voice input
- OpenAI TTS (`tts-1`) streams AI speech responses back to the client
- LangChain `ConversationBufferMemory` maintains full session context
- Structured end-of-interview feedback: confidence, problem-solving, communication, and coding skills rated 0–10

**Frontend (Next.js + TypeScript)**
- WebSocket client for real-time bidirectional communication
- Hold-to-record voice interface using the MediaRecorder API
- Monaco Editor for in-browser code writing and submission
- Split-panel layout: coding question panel + code editor + conversation transcript
- AI audio responses play automatically via a hidden `<audio>` element

---

## Setup

**Backend**
```bash
cd mock-interview-platform/backend
python -m venv venv && source venv/bin/activate
pip install fastapi uvicorn openai langchain python-dotenv
echo "OPENAI_API_KEY=your_key" > .env
uvicorn main:app --reload
```

**Frontend**
```bash
cd mock-interview-platform/frontend
npm install && npm run dev
```

**Behavioral Bot** — Open `Mock_interview_final_changed_to_whisperAI.ipynb` in Google Colab, set `OPENAI_API_KEY` and `GROQ_API` in Colab secrets, and run all cells.
