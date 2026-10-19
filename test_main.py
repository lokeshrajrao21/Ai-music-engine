"""
Automated test suite for IncuBrix AI Background Music Engine Prototype.
Tests health endpoint, job creation, duration validation, status retrieval, and artifact downloads.
"""

import time
import wave
import pytest
from starlette.testclient import TestClient
from main import app, jobs_db, OUTPUT_DIR


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint(client):
    """Test GET /health returns running status and provider info."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "provider" in data
    assert "version" in data
    assert data["provider"] == "mock"


def test_index_frontend(client):
    """Test GET / serves HTML frontend."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "IncuBrix" in response.text


def test_create_job_valid(client):
    """Test POST /api/v1/music/jobs with valid prompt and duration."""
    payload = {
        "prompt": "calm, ambient lo-fi beat for product demonstration",
        "duration_s": 10.0
    }
    response = client.post("/api/v1/music/jobs", json=payload)
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] in ["queued", "running", "succeeded"]
    assert data["duration_s"] == 10.0
    assert data["prompt"] == payload["prompt"]


def test_job_status_and_completion(client):
    """Test creating a job and polling GET /api/v1/jobs/{job_id} until succeeded."""
    payload = {
        "prompt": "upbeat corporate acoustic theme",
        "duration_s": 5.0
    }
    create_res = client.post("/api/v1/music/jobs", json=payload)
    assert create_res.status_code == 202
    job_id = create_res.json()["job_id"]

    # Poll status until finished or timeout
    max_retries = 20
    succeeded = False
    for _ in range(max_retries):
        status_res = client.get(f"/api/v1/jobs/{job_id}")
        assert status_res.status_code == 200
        job_data = status_res.json()
        if job_data["status"] == "succeeded":
            succeeded = True
            assert job_data["progress"] == 100
            assert job_data["result"] is not None
            assert "mix_url" in job_data["result"]
            assert "manifest_url" in job_data["result"]
            break
        elif job_data["status"] == "failed":
            pytest.fail(f"Job failed with error: {job_data.get('error')}")
        time.sleep(0.1)

    assert succeeded, "Job did not complete within the timeout period"


def test_invalid_duration_too_low(client):
    """Test duration validation rejects values less than 5 seconds."""
    payload = {
        "prompt": "quick melody",
        "duration_s": 4.9
    }
    response = client.post("/api/v1/music/jobs", json=payload)
    assert response.status_code == 422


def test_invalid_duration_too_high(client):
    """Test duration validation rejects values greater than 300 seconds."""
    payload = {
        "prompt": "epic cinematic symphony",
        "duration_s": 305.0
    }
    response = client.post("/api/v1/music/jobs", json=payload)
    assert response.status_code == 422


def test_invalid_prompt_empty(client):
    """Test validation rejects empty prompt string."""
    payload = {
        "prompt": "   ",
        "duration_s": 15.0
    }
    response = client.post("/api/v1/music/jobs", json=payload)
    assert response.status_code == 422


def test_job_not_found(client):
    """Test GET /api/v1/jobs/{job_id} returns 404 for unknown job ID."""
    response = client.get("/api/v1/jobs/non-existent-uuid-12345")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_download_artifacts_and_validate_wav(client):
    """Test downloading the generated WAV file and manifest, validating content."""
    payload = {
        "prompt": "test acoustic track for verification",
        "duration_s": 6.0
    }
    create_res = client.post("/api/v1/music/jobs", json=payload)
    job_id = create_res.json()["job_id"]

    # Wait for completion
    for _ in range(20):
        res = client.get(f"/api/v1/jobs/{job_id}")
        if res.json()["status"] == "succeeded":
            break
        time.sleep(0.1)

    # 1. Download WAV
    wav_res = client.get(f"/api/v1/jobs/{job_id}/download/mix.wav")
    assert wav_res.status_code == 200
    assert wav_res.headers["content-type"] == "audio/wav"
    assert len(wav_res.content) > 0

    # Verify WAV file integrity
    wav_path = OUTPUT_DIR / job_id / "mix.wav"
    with wave.open(str(wav_path), "rb") as wav_file:
        assert wav_file.getnchannels() == 2
        assert wav_file.getsampwidth() == 2
        assert wav_file.getframerate() == 48000
        actual_duration = wav_file.getnframes() / 48000.0
        assert abs(actual_duration - 6.0) < 0.05

    # 2. Download manifest
    manifest_res = client.get(f"/api/v1/jobs/{job_id}/download/music_manifest.json")
    assert manifest_res.status_code == 200
    manifest = manifest_res.json()
    assert manifest["is_ai_generated"] is False
    assert "mock" in manifest["generation_method"].lower()
    assert "not implemented" in manifest["stems_status"].lower()
    assert manifest["requested_duration_s"] == 6.0
