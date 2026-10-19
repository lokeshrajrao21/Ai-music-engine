# IncuBrix AI Background Music Engine — Simple Prototype

A lightweight demonstration prototype of the **IncuBrix AI Background Music Engine for Video** assessment. Built with **Python**, **FastAPI**, and vanilla **HTML/CSS/JS**.

---

## 1. Overview

This prototype demonstrates the end-to-end background music generation workflow:
- Creators input a music description (prompt) and target duration (in seconds).
- The system validates the request (5 to 300 seconds) and queues a background generation job.
- The user can monitor job status in real time.
- Upon completion, the system outputs a 48 kHz stereo WAV audio file, a JSON metadata manifest, an in-browser audio player, and download links.

> **Important Disclosure on Provider & Stems:**  
> - **Provider:** Uses a clearly labelled **mock procedural harmonic synthesizer** running locally. It does not pretend to be AI-generated music.
> - **Stems:** Genuine stem generation requires multi-track generative models or separation pipelines (e.g. Demucs/HTDemucs). This basic prototype **does not fabricate fake stems**; the stems requirement is explicitly reported as **Not Implemented**.

---

## 2. Architecture & File Structure

```
Incubrix/
├── main.py                  # FastAPI server, endpoints, background worker, mock audio synthesizer
├── static/
│   └── index.html           # Simple web interface with form, polling, audio player, manifest viewer
├── test_main.py             # Automated test suite (pytest + Starlette TestClient)
├── requirements.txt         # Python dependencies
├── openapi.yaml             # OpenAPI 3.1 specification for all endpoints
├── .env.example             # Configuration environment variables template
├── README.md                # Project documentation and quickstart instructions
├── SOURCES.md               # Disclosures and commercial licensing verification
├── AI_USE.md                # AI coding assistance disclosure
├── REPORT.md                # Engineering assessment report, trade-offs, and metrics
└── outputs/                 # Directory where generated WAVs and manifests are saved per job
```

---

## 3. Quickstart & Installation (Under 5 Commands)

### Step 1: Clone or open project folder
```bash
cd Incubrix
```

### Step 2: Install dependencies
Using Python 3.10+ (or Windows `py` launcher):
```bash
py -m pip install -r requirements.txt
```
*(On Linux/macOS: `python3 -m pip install -r requirements.txt`)*

### Step 3: Run automated test suite
```bash
py -m pytest test_main.py -v
```

### Step 4: Start the application server
```bash
py -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### Step 5: Open the web application
Open your browser and navigate to:
```
http://127.0.0.1:8000
```
Interactive API docs are also available at `http://127.0.0.1:8000/docs`.

---

## 4. API Endpoints Reference

### 1. Health Check
- **Endpoint:** `GET /health`
- **Response:**
  ```json
  {
    "status": "ok",
    "service": "incubrix-ai-music-engine-prototype",
    "version": "0.1.0",
    "provider": "mock",
    "timestamp": "2026-10-19T15:15:00Z"
  }
  ```

### 2. Create Music Generation Job
- **Endpoint:** `POST /api/v1/music/jobs`
- **Status Code:** `202 Accepted`
- **Request Body:**
  ```json
  {
    "prompt": "warm, optimistic acoustic pop for a product launch",
    "duration_s": 45.0
  }
  ```
  *(Note: `duration` is also accepted as an alias for `duration_s`)*
- **Validation Rules:**
  - `prompt`: String, non-empty, minimum length 3 characters, maximum 1000 characters.
  - `duration_s`: Float/int, strictly between **5.0** and **300.0** seconds.
  - Invalid requests return `422 Unprocessable Entity`.
- **Response:**
  ```json
  {
    "job_id": "a98fdc57-60a3-4876-b516-ec8c75ddc67b",
    "status": "queued",
    "progress": 0,
    "prompt": "warm, optimistic acoustic pop for a product launch",
    "duration_s": 45.0,
    "created_at": "2026-10-19T15:15:00Z",
    "message": "Job queued for processing",
    "result": null,
    "error": null
  }
  ```

### 3. Get Job Status & Results
- **Endpoint:** `GET /api/v1/jobs/{job_id}`
- **Response (when succeeded):**
  ```json
  {
    "job_id": "a98fdc57-60a3-4876-b516-ec8c75ddc67b",
    "status": "succeeded",
    "progress": 100,
    "prompt": "warm, optimistic acoustic pop for a product launch",
    "duration_s": 45.0,
    "created_at": "2026-10-19T15:15:00Z",
    "message": "Music generation succeeded",
    "result": {
      "mix_url": "/api/v1/jobs/a98fdc57-60a3-4876-b516-ec8c75ddc67b/download/mix.wav",
      "manifest_url": "/api/v1/jobs/a98fdc57-60a3-4876-b516-ec8c75ddc67b/download/music_manifest.json",
      "manifest": {
        "job_id": "a98fdc57-60a3-4876-b516-ec8c75ddc67b",
        "prompt": "warm, optimistic acoustic pop for a product launch",
        "requested_duration_s": 45.0,
        "actual_duration_s": 45.0,
        "sample_rate": 48000,
        "channels": 2,
        "format": "wav",
        "output_filename": "mix.wav",
        "generation_method": "Mock Synthetic Audio Synthesizer (Harmonic Waveform Engine)",
        "is_ai_generated": false,
        "audio_disclaimer": "This audio was generated using a mock harmonic synthesizer for prototype testing. It is NOT AI-generated music.",
        "stems_status": "Not implemented. Genuine stem generation requires multi-track separation or multi-instrument generative models, which are omitted in this basic prototype.",
        "created_at": "2026-10-19T15:15:01Z"
      }
    },
    "error": null
  }
  ```

### 4. Download Generated Audio & Manifest
- **Endpoint:** `GET /api/v1/jobs/{job_id}/download/{filename}`
- Serves `mix.wav` (`audio/wav`) or `music_manifest.json` (`application/json`).

---

## 5. Honest Status Assessment

In accordance with the IncuBrix Assessment standards, here is the honest evaluation of features:

### Implemented & Working:
- [x] Simple web frontend (text box for prompt, duration input, generate button, live status message, audio player, download link, manifest viewer).
- [x] FastAPI REST API matching IncuBrix endpoints (`POST /api/v1/music/jobs`, `GET /api/v1/jobs/{job_id}`, `GET /health`).
- [x] Prompt & duration validation (enforces 5 to 300 seconds; rejects empty or invalid prompts).
- [x] Asynchronous background job processing and progress tracking.
- [x] 48 kHz stereo WAV generation with exact length matching and smooth fade envelope.
- [x] JSON manifest generation with prompt, duration, method, disclaimer, and stems status.
- [x] Full automated test suite (8 test cases passing).
- [x] OpenAPI 3.1 specification (`openapi.yaml`).
- [x] Disclosures (`SOURCES.md`, `AI_USE.md`, `REPORT.md`).

### Not Implemented in this Prototype:
- [ ] **Real AI Music Model:** Real open-weights or hosted AI generation (e.g. MusicGen, Stable Audio) is swapped for a mock procedural audio synthesizer.
- [ ] **Instrument Stems:** Separate stems (drums, bass, pads, lead) are not produced. The system does not fake stems via EQ bands.
- [ ] **Voiceover Ducking:** Ducking under speech input (`narration_url`) is not implemented.
- [ ] **Persistent S3/MinIO & Database:** Uses local filesystem (`outputs/`) and in-memory job store.
- [ ] **Docker Compose:** Containerization not included in this minimal prototype.
