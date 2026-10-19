# SOURCES & LICENSES DISCLOSURE

IncuBrix AI Background Music Engine — Prototype

This document lists all libraries, frameworks, tools, models, media sources, and datasets used in this prototype project, verifying that all default dependencies and outputs are safe and legally licensed for commercial use.

---

## 1. Core Frameworks & Dependencies

| Component | Version | License | Commercial Use | Purpose / Description |
| :--- | :--- | :--- | :--- | :--- |
| **Python** | 3.14+ | PSF License | Yes | Core programming language runtime. |
| **FastAPI** | >= 0.115.0 | MIT License | Yes | High-performance asynchronous web framework for REST API endpoints. |
| **Uvicorn** | >= 0.30.0 | BSD-3-Clause | Yes | Lightning-fast ASGI web server implementation. |
| **Starlette** | >= 0.46.0 | BSD-3-Clause | Yes | Lightweight ASGI framework/toolkit underpinning FastAPI. |
| **Pydantic** | >= 2.9.0 | MIT License | Yes | Data validation and settings management using Python type annotations. |
| **HTTPX** | >= 0.28.0 | BSD-3-Clause | Yes | Next-generation HTTP client for API communication and integration tests. |
| **Pytest** | >= 8.0.0 | MIT License | Yes | Automated testing framework for unit and integration testing. |

---

## 2. Audio Engine & Synthesis Sources

| Component | Source / Provider | License | Commercial Rights | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Mock Harmonic Audio Synthesizer** | Custom procedural engine (`main.py`) | MIT / Project Owned | Yes | Generates procedural stereo harmonic audio using standard Python mathematical synthesis (`math`, `wave`, `struct`). |
| **Audio Samples / Sound Libraries** | None | N/A | N/A | No third-party recorded audio samples, copyrighted loops, or proprietary sound packs were used. Output is generated procedurally from sine wave harmonics. |

---

## 3. Commercial Safety & Copyright Statement

- **No Copyrighted Music:** The prototype does not copy, interpolate, or train on any copyrighted songs, melodies, or artist recordings.
- **Instrumental Only:** Output audio is purely instrumental waveforms; no human vocals, speech recordings, or vocal samples are used.
- **No Non-Commercial Licenses:** No CC BY-NC (Creative Commons Non-Commercial) assets or restrictive AGPL code are used in the runtime path.
