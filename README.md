# MultiModel-TriageAssistant

> A privacy-first, locally-run **multi-modal AI health triage assistant** that provides preliminary risk assessment across symptom text, medical images, and clinical reports — powered entirely by local LLMs via [Ollama](https://ollama.com).

<p align="left">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white">
  <img alt="Streamlit" src="https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?logo=streamlit&logoColor=white">
  <img alt="Ollama" src="https://img.shields.io/badge/Ollama-llama3%20%7C%20llava-000000?logo=ollama&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/License-Educational-blue">
</p>

> [!WARNING]
> **Educational prototype only.** MultiModel-TriageAssistant does **not** provide medical diagnoses, prescribe treatment, or replace professional medical advice. Always consult a qualified healthcare provider. It is not a medical device.

---

## ✨ Features

- **🩺 Symptom Checker** — Analyzes free-text symptom descriptions and returns a structured severity assessment with urgency guidance.
- **🖼️ Image Analysis** — Interprets medical/skin images using a local vision model (LLaVA) with preprocessing.
- **📄 Report Analysis** — Extracts text from clinical PDF reports (PyMuPDF + EasyOCR fallback for scanned pages), cleans it, and produces a plain-language interpretation.
- **🚨 Emergency Detection** — A rule-based, score-driven engine flags red-flag symptoms (chest pain, stroke signs, difficulty breathing, etc.) and escalates urgency in real time.
- **🔒 100% Local & Private** — No data leaves your machine. All inference runs through Ollama on `localhost`.

---

## 🏗️ Architecture

```
                         triage.py  (Streamlit entry point)
                              │  page config · CSS · sidebar · router
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
        ui/pages/         ui/components/      ui/styles.py
        (5 pages)        cards · badges       global theme
                          · banners
            │
            ▼
        modules/                         core/
   ┌────────────────┐            ┌──────────────────────┐
   │ symptom_analysis│           │ ollama_client.py     │  ← llama3 / llava
   │ image_analysis  │ ────────► │ emergency_detector.py│
   │ report_analysis │           │ response_parser.py   │
   └────────────────┘            └──────────────────────┘
            │                              │
            ▼                              ▼
        config/  (settings · prompts)   utils/  (validators · logger)
```

| Layer | Responsibility |
|-------|----------------|
| [triage.py](triage.py) | Bootstraps page config, CSS, sidebar, and navigation router. |
| [ui/](ui/) | Streamlit pages (`home`, `symptom`, `image`, `report`, `about`) + reusable components (result cards, severity badges, emergency banner). |
| [modules/](modules/) | Business logic per modality — analyzers, preprocessors, extractors, and Pydantic schemas. |
| [core/](core/) | Ollama API client, rule-based emergency detector, and LLM response parser. |
| [config/](config/) | Application constants ([settings.py](config/settings.py)) and LLM prompt templates ([prompts.py](config/prompts.py)). |
| [utils/](utils/) | Input validators and logging setup. |

---

## 🚀 Quick Start

> Detailed, OS-specific guides live in [SETUP_Files/](SETUP_Files/):
> [Windows](SETUP_Files/WINDOWS_SETUP.md) · [macOS](SETUP_Files/MacBook_SETUP.md)

### 1. Prerequisites

- **Python 3.11** (3.12+ may cause `easyocr` issues)
- **[Ollama](https://ollama.com/download)** installed and running
- ~8 GB free disk space for models · 8 GB+ RAM recommended

### 2. Pull the models

```bash
ollama pull llama3    # text reasoning  (~4.7 GB)
ollama pull llava     # vision/images   (~4.7 GB)
```

### 3. Set up the environment

```bash
# from the project root
python3.11 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run triage.py
```

The app opens automatically at **http://localhost:8501**.

---

## ⚙️ Configuration

Key settings in [config/settings.py](config/settings.py):

| Setting | Default | Description |
|---------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_TEXT_MODEL` | `llama3` | Model for symptom/report analysis |
| `OLLAMA_VISION_MODEL` | `llava` | Model for image analysis |
| `OLLAMA_TIMEOUT` | `120` | Per-request timeout (seconds) |
| `MAX_SYMPTOM_TEXT_LENGTH` | `2000` | Max characters for symptom input |
| `MAX_REPORT_FILE_SIZE_MB` | `20` | Max PDF report upload size |
| `MAX_IMAGE_FILE_SIZE_MB` | `10` | Max image upload size |

Severity levels (**Low / Medium / High**) and urgency tiers (**Routine → Soon → Urgent → Emergency**) are also defined here.

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| UI | [Streamlit](https://streamlit.io) |
| LLM runtime | [Ollama](https://ollama.com) — `llama3` (text), `llava` (vision) |
| PDF / OCR | [PyMuPDF](https://pymupdf.readthedocs.io), [EasyOCR](https://github.com/JaidedAI/EasyOCR) |
| Validation | [Pydantic](https://docs.pydantic.dev) |
| Imaging | [Pillow](https://python-pillow.org) |

---

## 📁 Project Structure

```
MultiModel-TriageAssistant/
├── triage.py                  # Streamlit entry point
├── requirements.txt
├── config/                    # Settings & prompt templates
├── core/                      # Ollama client, emergency detector, parser
├── modules/
│   ├── symptom_analysis/      # Text symptom analyzer
│   ├── image_analysis/        # Vision analyzer + preprocessor
│   └── report_analysis/       # PDF extractor, cleaner, analyzer
├── ui/
│   ├── pages/                 # home · symptom · image · report · about
│   ├── components/            # result cards, badges, emergency banner
│   └── styles.py              # global CSS theme
├── utils/                     # validators, logger
├── docs/                      # project report & integration notes
└── SETUP_Files/               # Windows & macOS setup guides
```

---

## 📚 Documentation

- [Project Report](docs/PROJECT_REPORT.md) — full design, methodology, and evaluation
- [Report Analysis Integration Guide](docs/report_analysis_integration.md) — PDF → text → LLM pipeline

---

## 🧯 Troubleshooting

| Problem | Fix |
|---------|-----|
| `Ollama connection error` | Ensure Ollama is running (`ollama serve`) and models are pulled |
| `easyocr` install fails | `pip install easyocr --no-cache-dir` |
| Port already in use | `streamlit run triage.py --server.port 8502` |
| Slow first response | Models load into memory on first call — subsequent calls are faster |

---

## ⚖️ Disclaimer

This project is developed for **educational purposes only**. MultiModel-TriageAssistant does not provide medical diagnoses and should not be used as a substitute for professional medical advice, diagnosis, or treatment. In a medical emergency, contact your local emergency services immediately.
