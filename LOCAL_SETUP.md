# IPO-AI Local Development & Hackathon Demo Setup Guide

This guide provides instructions to launch the entire IPO-AI stack locally for testing and video recording.

---

## Prerequisites
- **Python**: Python 3.10+ (Tested on Python 3.13.9)
- **Node.js**: Node 18+ (Tested on Node 20+)
- **Package Manager**: `npm` (v10+)
- **Operating System**: Windows / macOS / Linux

---

## Quick Start (One-Command Launcher for Windows)

Double-click or run:
```cmd
start-local.bat
```
*(Or in PowerShell: `.\start-local.ps1`)*

This script automatically launches both the FastAPI backend and Next.js frontend in separate terminal windows.

---

## Manual Step-by-Step Setup

### 1. Backend Setup (Terminal 1)
```bash
# Navigate to project root
cd C:\Users\Kashish Gandhi\Desktop\IPO-AI

# Install backend dependencies if needed
pip install fastapi uvicorn pydantic pytest

# Start FastAPI Server
python -m uvicorn backend.src.main:app --reload --port 8000
```
- **Backend Base URL**: `http://localhost:8000`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`

### 2. Frontend Setup (Terminal 2)
```bash
# Navigate to frontend folder
cd frontend

# Copy environment template if .env.local does not exist
cp .env.example .env.local

# Start Next.js Development Server
npm run dev
```
- **Frontend App URL**: `http://localhost:3000`

---

## Verifying Local Installation

### 1. Run Automated Backend Tests
```bash
python -m pytest backend/tests/test_allotment_engine.py
```
*(Expected: 14/14 tests PASSED)*

### 2. Run Demo Data Validator Script
```bash
python backend/scripts/validate_demo_ipos.py
```
*(Expected: `DEMO STATUS: READY`)*

### 3. Verify Frontend Production Build
```bash
cd frontend
npm run build
```
*(Expected: `✓ Compiled successfully` with 6 static routes generated)*

---

## Key Demo URLs

| Page / Feature | Local URL | Description |
| :--- | :--- | :--- |
| **Landing Page** | `http://localhost:3000` | Search & Browse Live/Historical IPOs |
| **Live Mainboard IPO** | `http://localhost:3000/analyse/juniper-green-energy` | Incomplete-Data Safe Calculator State |
| **Live SME IPO** | `http://localhost:3000/analyse/g-v-electricals` | SME 2025 Market Lot Rules |
| **Historical BoA IPO** | `http://localhost:3000/analyse/zaggle-prepaid-ocean-services` | Official Basis of Allotment Post-Allotment State |
| **Interactive API Docs** | `http://localhost:8000/docs` | FastAPI Swagger OpenAPI Specification |

---

## Stopping Local Servers
- Close the backend and frontend terminal windows, or press `Ctrl + C` in each terminal.
