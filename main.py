"""
IncuBrix AI Background Music Engine - Simple Prototype
Backend implementation with FastAPI.
"""

import os
import uuid
import json
import math
import struct
import wave
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException, BackgroundTasks, status
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_validator


# --- Configuration ---
APP_TITLE = "IncuBrix AI Background Music Engine - Prototype"
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "outputs"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

MUSIC_PROVIDER = os.getenv("MUSIC_PROVIDER", "mock").lower()
MUSIC_API_KEY = os.getenv("MUSIC_API_KEY", "")
SAMPLE_RATE = int(os.getenv("DEFAULT_SAMPLE_RATE", "48000"))

app = FastAPI(
    title=APP_TITLE,
    description="A basic demonstration prototype of the IncuBrix AI Background Music Engine",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job storage for prototype
jobs_db: Dict[str, Dict[str, Any]] = {}


# --- Request & Response Models ---
class MusicJobCreate(BaseModel):
    prompt: str = Field(
        ...,
        description="Text description of the desired background music",
        min_length=3,
        max_length=1000,
        examples=["warm, optimistic acoustic pop for a product launch"],
    )
    duration_s: Optional[float] = Field(
        default=None,
        description="Music duration in seconds (must be between 5.0 and 300.0)",
        examples=[30.0],
    )
    duration: Optional[float] = Field(
        default=None,
        description="Alias for duration_s",
        examples=[30.0],
    )

    @model_validator(mode="after")
    def validate_duration_and_prompt(self):
        cleaned_prompt = self.prompt.strip()
        if not cleaned_prompt:
            raise ValueError("Prompt cannot be empty or only whitespace")
        self.prompt = cleaned_prompt

        # Resolve duration between duration_s and duration
        target_duration = self.duration_s if self.duration_s is not None else self.duration
        if target_duration is None:
            raise ValueError("Duration in seconds is required (between 5 and 300 seconds)")
        
        if not (5.0 <= float(target_duration) <= 300.0):
            raise ValueError(f"Duration must be between 5 and 300 seconds. Provided: {target_duration}")
        
        self.duration_s = float(target_duration)
        return self


class MusicJobResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    prompt: str
    duration_s: float
    created_at: str
    message: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# --- Audio Generation Engine ---
def generate_mock_audio(job_id: str, prompt: str, duration_s: float) -> Dict[str, Any]:
    """
    Generates a deterministic, pleasant harmonic audio WAV file using standard math & wave.
    Clearly labelled as a mock generator for prototype demonstration.
    """
    job_dir = OUTPUT_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    wav_path = job_dir / "mix.wav"
    manifest_path = job_dir / "music_manifest.json"

    # Audio synthesis parameters
    sample_rate = SAMPLE_RATE
    num_frames = int(sample_rate * duration_s)

    # Base harmonic frequencies (C Major 7 chord progression: C4, E4, G4, B4)
    chords = [
        [261.63, 329.63, 392.00, 493.88],  # Cmaj7
        [220.00, 261.63, 329.63, 392.00],  # Am7
        [174.61, 220.00, 261.63, 329.63],  # Fmaj7
        [196.00, 246.94, 293.66, 392.00],  # G7
    ]
    chord_duration = 3.0  # seconds per chord

    with wave.open(str(wav_path), "wb") as wav_file:
        wav_file.setnchannels(2)  # Stereo
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)

        # Buffer generation in chunks for performance
        chunk_size = 48000
        frames_written = 0

        fade_in_len = int(sample_rate * 0.5)
        fade_out_len = int(sample_rate * 1.0)

        while frames_written < num_frames:
            current_chunk = min(chunk_size, num_frames - frames_written)
            frame_bytes = bytearray()

            for i in range(current_chunk):
                frame_idx = frames_written + i
                t = frame_idx / sample_rate

                # Envelope: smooth fade-in and musical fade-out
                envelope = 1.0
                if frame_idx < fade_in_len:
                    envelope = frame_idx / fade_in_len
                elif frame_idx > (num_frames - fade_out_len):
                    envelope = (num_frames - frame_idx) / fade_out_len

                # Select active chord
                chord_idx = int(t / chord_duration) % len(chords)
                active_notes = chords[chord_idx]

                # Synthesize gentle harmonic tone
                sample_l = 0.25 * (
                    math.sin(2 * math.pi * active_notes[0] * t) +
                    0.5 * math.sin(2 * math.pi * active_notes[1] * t) +
                    0.25 * math.sin(2 * math.pi * active_notes[2] * t)
                ) * envelope

                sample_r = 0.25 * (
                    math.sin(2 * math.pi * active_notes[1] * t) +
                    0.5 * math.sin(2 * math.pi * active_notes[2] * t) +
                    0.25 * math.sin(2 * math.pi * active_notes[3] * t)
                ) * envelope

                # Clamp & convert to 16-bit integer (-32768 to 32767)
                int_l = max(-32767, min(32767, int(sample_l * 32767)))
                int_r = max(-32767, min(32767, int(sample_r * 32767)))

                frame_bytes.extend(struct.pack("<hh", int_l, int_r))

            wav_file.writeframes(frame_bytes)
            frames_written += current_chunk

    # Build manifest
    manifest_data = {
        "job_id": job_id,
        "prompt": prompt,
        "requested_duration_s": duration_s,
        "actual_duration_s": round(num_frames / sample_rate, 4),
        "sample_rate": sample_rate,
        "channels": 2,
        "format": "wav",
        "output_filename": "mix.wav",
        "generation_method": "Mock Synthetic Audio Synthesizer (Harmonic Waveform Engine)",
        "is_ai_generated": False,
        "audio_disclaimer": "This audio was generated using a mock harmonic synthesizer for prototype testing. It is NOT AI-generated music.",
        "stems_status": "Not implemented. Genuine stem generation requires multi-track separation or multi-instrument generative models, which are omitted in this basic prototype.",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    return {
        "mix_url": f"/api/v1/jobs/{job_id}/download/mix.wav",
        "manifest_url": f"/api/v1/jobs/{job_id}/download/music_manifest.json",
        "manifest": manifest_data,
    }


async def run_music_job(job_id: str, prompt: str, duration_s: float):
    """Background task to run audio generation and update job status."""
    try:
        jobs_db[job_id]["status"] = "running"
        jobs_db[job_id]["progress"] = 30
        jobs_db[job_id]["message"] = "Generating music track..."

        # Small async pause to simulate processing and verify async status polling
        await asyncio.sleep(0.5)

        jobs_db[job_id]["progress"] = 70

        if MUSIC_PROVIDER == "external_api" and MUSIC_API_KEY:
            # If an external provider is configured, call it here
            # Placeholder for configured external service
            raise NotImplementedError("External music generation API configured but not implemented")
        else:
            # Local mock provider
            result = generate_mock_audio(job_id, prompt, duration_s)

        jobs_db[job_id]["status"] = "succeeded"
        jobs_db[job_id]["progress"] = 100
        jobs_db[job_id]["message"] = "Music generation succeeded"
        jobs_db[job_id]["result"] = result
        jobs_db[job_id]["updated_at"] = datetime.now(timezone.utc).isoformat()

    except Exception as e:
        jobs_db[job_id]["status"] = "failed"
        jobs_db[job_id]["progress"] = 100
        jobs_db[job_id]["message"] = f"Generation failed: {str(e)}"
        jobs_db[job_id]["error"] = str(e)
        jobs_db[job_id]["updated_at"] = datetime.now(timezone.utc).isoformat()


# --- API Routes ---
@app.get("/health", summary="Health Check")
async def health_check():
    """Health check endpoint to verify that the application is running."""
    return {
        "status": "ok",
        "service": "incubrix-ai-music-engine-prototype",
        "version": "0.1.0",
        "provider": MUSIC_PROVIDER,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post(
    "/api/v1/music/jobs",
    response_model=MusicJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Create Music Generation Job",
)
async def create_music_job(payload: MusicJobCreate, background_tasks: BackgroundTasks):
    """
    Accepts a music prompt and duration (5 to 300 seconds),
    creates an asynchronous generation job, and queues it for processing.
    """
    job_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    job_data = {
        "job_id": job_id,
        "status": "queued",
        "progress": 0,
        "prompt": payload.prompt,
        "duration_s": payload.duration_s,
        "message": "Job queued for processing",
        "created_at": now,
        "updated_at": now,
        "result": None,
        "error": None,
    }
    jobs_db[job_id] = job_data

    # Schedule generation in background
    background_tasks.add_task(run_music_job, job_id, payload.prompt, payload.duration_s)

    return MusicJobResponse(**job_data)


@app.get(
    "/api/v1/jobs/{job_id}",
    response_model=MusicJobResponse,
    summary="Get Job Status and Results",
)
async def get_job_status(job_id: str):
    """Retrieves current job status, progress, and results or error details."""
    if job_id not in jobs_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found",
        )
    return MusicJobResponse(**jobs_db[job_id])


@app.get("/api/v1/jobs/{job_id}/download/{filename}", summary="Download Job Artifact")
async def download_job_file(job_id: str, filename: str):
    """Download the generated audio file (mix.wav) or manifest (music_manifest.json)."""
    if job_id not in jobs_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found",
        )

    file_path = OUTPUT_DIR / job_id / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{filename}' for job '{job_id}' not found",
        )

    media_type = "audio/wav" if filename.endswith(".wav") else "application/json"
    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=filename,
    )


# Mount static directory for frontend
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=HTMLResponse, summary="Web Interface")
async def serve_index():
    """Serves the simple web frontend."""
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        return HTMLResponse("<h1>IncuBrix AI Music Engine Prototype</h1><p>Frontend loading...</p>")
    with open(index_file, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("APP_HOST", "127.0.0.1")
    port = int(os.getenv("APP_PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=True)
