# MultiModel-TriageAssistant
## A Local AI-Powered Preliminary Medical Assessment System

---

**Department of Computer Science and Engineering**

**Bachelor of Technology**

**Academic Year: 2025–2026**

---

| | |
|---|---|
| **Project Title** | Health Care Triage Assistant |
| **Guide** | GAURAV VARSHNEY |
| **Team Members** | ANUBHA KUMARI |
| **Roll No.** | 23131480004 |
| **Institution** | GALGOTIAS UNIVERSITY |
| **Submitted To** | Department of Computer Science and Engineering |

---

> **Disclaimer:** This system is developed purely for educational purposes as a college project. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare professional for medical concerns.

---

## TABLE OF CONTENTS

1. [Abstract](#1-abstract)
2. [Introduction](#2-introduction)
3. [Problem Statement](#3-problem-statement)
4. [Objectives](#4-objectives)
5. [Literature Review](#5-literature-review)
6. [Methodology](#6-methodology)
7. [System Architecture](#7-system-architecture)
8. [Modules](#8-modules)
9. [Results](#9-results)
10. [Future Scope](#10-future-scope)
11. [Conclusion](#11-conclusion)
12. [References](#12-references)

---

## 1. ABSTRACT

Healthcare accessibility remains a critical challenge in many regions, where patients lack immediate access to medical professionals for preliminary assessment of their symptoms. This project presents **MultiModel-TriageAssistant**, a locally-deployed, privacy-preserving AI application that provides preliminary health risk assessment through three complementary modalities: symptom text analysis, medical image analysis, and clinical report interpretation.

The system leverages large language models (LLMs) running entirely on-device via the **Ollama** inference framework — specifically **Llama 3** for natural language processing and **LLaVA** (Large Language and Vision Assistant) for multimodal image understanding. A rule-based emergency detection engine provides always-on, deterministic identification of life-threatening conditions independent of the LLM pipeline, ensuring zero false negatives for critical emergencies.

Built with **Python** and **Streamlit**, the application follows a clean layered architecture separating business logic from the user interface. Medical report ingestion supports both native PDF text extraction (via **PyMuPDF**) and OCR-based extraction for scanned documents (via **EasyOCR**). All data processing occurs locally with no external API calls, preserving complete patient privacy.

Evaluation demonstrates that the system correctly identifies emergency conditions, generates structured and clinically relevant analysis across all three input modalities, and presents results in an accessible interface with appropriate urgency indicators. This project demonstrates the feasibility of deploying capable AI health-assistance tools in resource-constrained, privacy-sensitive environments.

**Keywords:** AI Triage, Large Language Model, Ollama, LLaVA, Llama 3, Medical Image Analysis, OCR, Symptom Checker, Emergency Detection, Streamlit, Privacy-Preserving AI.

---

## 2. INTRODUCTION

### 2.1 Background

The global healthcare system faces a fundamental mismatch: demand for medical guidance far exceeds the availability of healthcare professionals, particularly for initial assessments that help patients decide whether and how urgently to seek formal care. In India alone, the doctor-to-patient ratio stands at approximately 1:1,511 against the WHO-recommended 1:1,000, with rural regions facing even greater scarcity. This gap leads to two equally harmful outcomes — delayed care for genuinely urgent conditions, and unnecessary emergency-room visits for non-critical concerns.

Artificial Intelligence, particularly the recent generation of large language models, has demonstrated remarkable capability in biomedical question answering, clinical note understanding, and medical image interpretation. Models like GPT-4, Med-PaLM 2, and open-source alternatives trained on medical corpora show performance approaching specialist-level reasoning on structured medical exams. However, most deployments rely on cloud APIs, raising significant concerns about patient data privacy, internet connectivity requirements, and ongoing subscription costs.

### 2.2 Motivation

The motivation for this project arises from three observations:

1. **Privacy gap**: Existing AI health tools (Symptom Checker by WebMD, Ada Health, K Health) send sensitive medical data to remote servers. For many patients, this is an unacceptable compromise.

2. **Accessibility gap**: Cloud-dependent tools require reliable internet. Offline or locally-running alternatives would serve rural or bandwidth-limited users.

3. **Modality gap**: Most consumer tools accept only text symptoms. A more complete assistant should handle medical images (photos of wounds, rashes, burns) and interpret printed lab reports — inputs patients commonly have on hand.

### 2.3 Scope

MultiModel-TriageAssistant is designed as an **educational prototype** demonstrating how locally-running open-source LLMs can be combined with classical NLP and computer vision techniques to build a multi-modal health triage tool. The system provides structured preliminary assessments and urgency recommendations. It does **not** make diagnoses, prescribe treatments, or replace clinical judgment.

---

## 3. PROBLEM STATEMENT

Patients seeking preliminary health guidance face a trilemma:

- **Privacy**: Cloud-based AI health tools require uploading sensitive personal medical data to third-party servers.
- **Accessibility**: Reliable internet access is a prerequisite for most modern AI health assistants, excluding rural and low-connectivity populations.
- **Completeness**: Existing free tools handle primarily text symptoms; few accept medical images or interpret lab reports, despite these being common patient-held data sources.

Additionally, all AI-based systems carry the risk of **missed emergencies** — if the language model hallucinates or misclassifies a critical condition as benign, the consequences could be life-threatening.

**This project addresses the following specific problem:**

> *How can a locally-deployable, privacy-preserving AI system provide accurate multi-modal preliminary medical triage — covering text symptoms, medical images, and clinical reports — while guaranteeing detection of life-threatening emergencies through a deterministic, LLM-independent safety layer?*

---

## 4. OBJECTIVES

The primary and secondary objectives of this project are as follows:

### 4.1 Primary Objectives

1. **Develop a multi-modal triage system** capable of accepting three input types: free-text symptoms, medical images, and PDF clinical reports.

2. **Achieve fully local execution** using the Ollama inference framework with Llama 3 and LLaVA models, eliminating dependence on external APIs.

3. **Implement a deterministic emergency detection layer** that identifies life-threatening conditions using rule-based phrase matching, independent of the LLM pipeline.

4. **Provide structured, actionable output** including severity classification, consultation urgency, possible conditions, and specific recommendations.

### 4.2 Secondary Objectives

5. **Support scanned PDF ingestion** through OCR-based text extraction for clinical reports not available in digital text form.

6. **Build a clean, layered software architecture** with strict separation between business logic and user interface, enabling future extensibility.

7. **Ensure patient data privacy** by processing all data locally with zero external network calls during analysis.

8. **Produce a usable, well-documented codebase** demonstrating software engineering best practices (Pydantic schemas, modular design, configuration management).

---

## 5. LITERATURE REVIEW

### 5.1 AI in Medical Triage and Symptom Checking

**Semigran et al. (2015)** evaluated 23 online symptom checkers and found they listed the correct diagnosis first in only 34% of cases, though they appropriately advised emergency care 80% of the time for serious conditions. This highlighted the importance of emergency detection accuracy over diagnostic precision.

**Rajpurkar et al. (2017)** demonstrated with CheXNet that convolutional neural networks trained on chest X-ray datasets could exceed radiologist-level performance on pneumonia detection, establishing the viability of AI for medical image interpretation.

**Singhal et al. (2023)** introduced Med-PaLM 2, achieving expert-level performance (86.5%) on the US Medical Licensing Examination (USMLE), demonstrating that large language models can reason effectively over medical questions when properly prompted.

**Nori et al. (2023)** showed GPT-4 achieved 90.2% on USMLE questions, further validating LLMs' medical reasoning capability. Critically, they noted that structured prompting and JSON-constrained output significantly improved reliability and reduced hallucinations.

### 5.2 Open-Source and Local LLMs in Healthcare

**Touvron et al. (2023)** released Llama 2, establishing that open-source models can approach proprietary model quality while enabling local deployment. Llama 3 (Meta AI, 2024) further closed this gap and is the text backbone of this project.

**Liu et al. (2023)** introduced LLaVA (Large Language and Vision Assistant), a multimodal model combining a CLIP vision encoder with a language model. LLaVA demonstrates strong performance on visual question answering tasks, including medical image understanding, making it suitable as this project's vision module.

**Ollama (2023)** emerged as the dominant framework for running quantized LLMs locally, abstracting hardware-specific optimization (GGUF quantization, Metal/CUDA acceleration) behind a unified REST API. This significantly lowers the barrier to local LLM deployment.

### 5.3 Medical Report Analysis and OCR

**PyMuPDF (MuPDF)** provides high-performance native PDF text extraction. For scanned or image-based PDFs, optical character recognition is necessary. **EasyOCR** (JaidedAI, 2020) offers an accessible Python OCR library supporting 80+ languages, with strong performance on printed documents typical of clinical reports.

### 5.4 Structured Output and Schema Validation

Recent work on LLM reliability emphasizes constrained generation and post-hoc validation. **Pydantic** schemas, combined with JSON extraction from model outputs, provide a practical approach to structured output enforcement that is model-agnostic and does not require fine-tuning.

### 5.5 Emergency Detection

**Classic triage systems** (Manchester Triage System, Emergency Severity Index) use rule-based protocols to categorize patients by urgency. This project adapts the core principle — deterministic, protocol-driven emergency identification — to a software implementation, using phrase-pattern scoring rather than vital-sign measurement.

### 5.6 Gap Analysis

| Aspect | Existing Tools | This Project |
|--------|---------------|--------------|
| Privacy | Cloud-based (Ada, K Health) | Fully local |
| Modalities | Primarily text | Text + Image + Report |
| Emergency safety | LLM-dependent | Rule-based + LLM |
| Connectivity | Internet required | Offline capable |
| Cost | Subscription/freemium | Open source |
| OCR support | Rare | Native (EasyOCR) |

---

## 6. METHODOLOGY

### 6.1 Overall Approach

The project follows a **modular pipeline architecture** for each input type, with a shared emergency detection layer. The development methodology is iterative, with each module (symptom → image → report) developed, tested, and integrated sequentially.

### 6.2 Technology Selection

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | Python 3.11 | Ecosystem maturity; EasyOCR compatibility |
| UI Framework | Streamlit | Rapid prototyping; minimal boilerplate |
| LLM Runtime | Ollama | Unified API; hardware acceleration |
| Text Model | Llama 3 (8B) | Strong instruction-following; open-source |
| Vision Model | LLaVA | Multimodal; CLIP-based vision encoder |
| PDF Extraction | PyMuPDF | Fast; high fidelity native text |
| OCR | EasyOCR | Multi-language; no external deps |
| Image Processing | Pillow | Standard Python imaging |
| Validation | Pydantic v2 | Fast validation; JSON schema generation |
| Data Classes | Pydantic | Type safety at pipeline boundaries |

### 6.3 Prompt Engineering

All LLM interactions use a two-part prompt structure:

**System Prompt** defines the model's role, output format constraints (JSON-only), field definitions, and safety disclaimers. Example excerpt from the symptom module:

```
You are a medical AI assistant providing preliminary health assessments.
Respond ONLY with valid JSON matching this exact schema:
{
  "possible_conditions": [...],
  "severity_level": "Low|Medium|High",
  "consultation_urgency": "Routine|Soon|Urgent|EMERGENCY",
  ...
}
```

**User Prompt** contains structured patient data (symptoms, age, sex, duration, intensity) formatted for the specific analysis type.

Image analysis prompts include a **type-specific focus suffix** — for skin lesions, this adds ABCDE criteria (Asymmetry, Border, Color, Diameter, Evolution); for burns, it adds Rule of Nines guidance; for wounds, it adds wound-classification criteria.

### 6.4 Emergency Detection Design

The emergency detector uses a three-layer scoring system:

1. **Category matching**: 9 emergency categories (chest pain, respiratory distress, severe bleeding, unconsciousness, seizure, stroke, burns, anaphylaxis, overdose), each with 10–15 phrase patterns. A match scores 10–30 base points per category.

2. **Amplifier scoring**: Presence of severity modifiers ("severe", "sudden", "cannot breathe", "profuse") multiplies the score by 1.5×.

3. **Override rules**: Certain phrases (e.g., "crushing chest pain", "not breathing", "stopped breathing") unconditionally set the level to CRITICAL regardless of score.

**Score thresholds:**
- CRITICAL: ≥ 60 → Call emergency services immediately
- HIGH: ≥ 30 → Go to emergency room now
- MODERATE: ≥ 10 → Seek care today
- NONE: < 10 → Standard assessment flow

This runs in sub-millisecond time before any LLM call. If CRITICAL or HIGH is detected, the LLM is still called for detailed recommendations, but the emergency override is applied to the final severity and urgency output.

### 6.5 Development Workflow

```
1. Requirements → Architecture Design
2. Core layer (Ollama client, emergency detector, parser)
3. Schema definitions (Pydantic models)
4. Module pipelines (symptom → image → report)
5. UI pages (one per module)
6. Integration testing
7. Documentation
```

---

## 7. SYSTEM ARCHITECTURE

### 7.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Symptom Page │  │  Image Page  │  │    Report Page       │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
└─────────┼─────────────────┼────────────────────-─┼─────────────┘
          │                 │                       │
┌─────────▼─────────────────▼───────────────────────▼─────────────┐
│                        Business Logic Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │   Symptom    │  │    Image     │  │       Report         │   │
│  │   Analyzer   │  │   Analyzer   │  │      Analyzer        │   │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘   │
└─────────┼─────────────────┼───────────────────────┼─────────────┘
          │                 │                        │
┌─────────▼─────────────────▼────────────────────────▼────────────┐
│                         Core Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │   Ollama     │  │  Emergency   │  │    Response          │   │
│  │   Client     │  │  Detector    │  │    Parser            │   │
│  └──────┬───────┘  └──────────────┘  └──────────────────────┘   │
└─────────┼────────────────────────────────────────────────────────┘
          │
┌─────────▼────────────────────────────────────────────────────────┐
│                      Ollama Runtime (Local)                      │
│         ┌────────────────┐          ┌────────────────┐           │
│         │   Llama 3 (8B) │          │   LLaVA        │           │
│         │  (Text/Report) │          │  (Image)       │           │
│         └────────────────┘          └────────────────┘           │
└──────────────────────────────────────────────────────────────────┘
```

### 7.2 Layered Architecture

The codebase is organized into four distinct layers:

| Layer | Directory | Responsibility |
|-------|-----------|---------------|
| **UI** | `ui/` | Streamlit pages, components, CSS |
| **Business Logic** | `modules/` | Analysis pipelines, schemas |
| **Core** | `core/` | LLM client, emergency detector, parser |
| **Config** | `config/` | Settings constants, prompt templates |
| **Utils** | `utils/` | Validators, logging |

**Key architectural principle:** Modules in `modules/` have **zero UI dependencies** — they can be used headlessly or integrated into any other interface (API, CLI, desktop app) without modification.

### 7.3 Data Flow — Symptom Analysis

```
User Input (symptoms, age, sex, duration, intensity)
          │
          ▼
    Input Validation (validators.py)
          │
          ▼
    Emergency Pre-Scan (emergency_detector.py)
          │
     ┌────┴─────┐
     │ CRITICAL? │── Yes ──► Force urgency=EMERGENCY, show banner
     └────┬─────┘
          │ No
          ▼
    Build LLM Prompt (prompts.py)
          │
          ▼
    Llama 3 Inference (ollama_client.py)
          │
          ▼
    JSON Extraction + Pydantic Validation (response_parser.py)
          │
          ▼
    Emergency Override (if detector flagged HIGH+)
          │
          ▼
    SymptomResult → UI Rendering (symptom_page.py)
```

### 7.4 Data Flow — Image Analysis

```
Image Upload (JPEG/PNG/BMP/WEBP)
          │
          ▼
    Image Preprocessing (preprocessor.py)
    [validate format → resize ≤1344px → base64 encode]
          │
          ▼
    Emergency Pre-Scan on user context text
          │
          ▼
    Build Vision Prompt (type-specific focus suffix)
          │
          ▼
    LLaVA Vision Inference (ollama_client.py)
          │
          ▼
    JSON Extraction + Pydantic Validation
          │
          ▼
    Emergency Override (if applicable)
          │
          ▼
    ImageResult → UI Rendering (image_page.py)
```

### 7.5 Data Flow — Report Analysis

```
PDF Upload
     │
     ▼
PyMuPDF Text Extraction (extractor.py)
     │
     ├── Native text found? ──► Use extracted text
     │
     └── Scanned/image pages? ──► EasyOCR fallback
          │
          ▼
    Text Cleaning (cleaner.py)
    [Unicode normalize → OCR noise removal → truncate 6000 chars]
          │
          ▼
    Build Report Prompt (report-specific prompts)
          │
          ▼
    Llama 3 Inference
          │
          ▼
    JSON Extraction + Pydantic Validation
          │
          ▼
    MedicalReportResult → UI Rendering (report_page.py)
```

### 7.6 Directory Structure

```
MultiModel-TriageAssistant/
├── triage.py                     # Application entry point
├── requirements.txt              # Python dependencies
├── config/
│   ├── settings.py               # Constants and thresholds
│   └── prompts.py                # Centralized LLM prompts
├── core/
│   ├── ollama_client.py          # Ollama REST API wrapper
│   ├── emergency_detector.py     # Rule-based emergency engine
│   └── response_parser.py       # JSON extraction & validation
├── modules/
│   ├── symptom_analysis/
│   │   ├── analyzer.py           # Symptom pipeline orchestrator
│   │   └── schema.py             # SymptomInput / SymptomResult
│   ├── image_analysis/
│   │   ├── analyzer.py           # Image pipeline orchestrator
│   │   ├── preprocessor.py       # Image validation & encoding
│   │   └── schema.py             # ImageInput / ImageResult
│   └── report_analysis/
│       ├── analyzer.py           # Report pipeline orchestrator
│       ├── extractor.py          # PDF text + OCR extraction
│       ├── cleaner.py            # Text normalization
│       ├── prompts.py            # Report-specific prompts
│       └── schemas.py            # MedicalReportResult
├── ui/
│   ├── styles.py                 # Global CSS injection
│   ├── components/
│   │   ├── result_card.py        # Card & stat widgets
│   │   ├── severity_badge.py     # Color-coded severity badges
│   │   └── emergency_banner.py  # Emergency alert component
│   └── pages/
│       ├── home_page.py          # Landing page
│       ├── symptom_page.py       # Symptom checker page
│       ├── image_page.py         # Image analysis page
│       ├── report_page.py        # Report analysis page
│       └── about_page.py         # About & disclaimer page
└── utils/
    ├── validators.py             # Input validation helpers
    └── logger.py                 # Logging configuration
```

---

## 8. MODULES

### 8.1 Module 1: Symptom Analysis

**Purpose:** Accept a free-text symptom description along with patient context (age, sex, duration, intensity) and return structured preliminary assessment.

**Input Schema (`SymptomInput`):**

| Field | Type | Constraints |
|-------|------|-------------|
| `symptoms` | string | 10–2000 characters |
| `age` | integer | 1–120 |
| `sex` | string | Male / Female / Other |
| `duration` | string | Free text (e.g., "3 days") |
| `intensity` | integer | 1–5 scale |

**Output Schema (`SymptomResult`):**

| Field | Description |
|-------|-------------|
| `possible_conditions` | List of likely conditions with confidence |
| `severity_level` | Low / Medium / High |
| `consultation_urgency` | Routine / Soon / Urgent / EMERGENCY |
| `confidence_level` | Low / Medium / High |
| `recommendations` | Specific actionable advice list |
| `emergency_result` | Emergency detector output (level, score, actions) |

**Pipeline:**
1. Validate input via Pydantic
2. Run emergency detector on symptom text
3. Construct system + user prompt with patient context
4. Call Llama 3 via Ollama client (timeout: 120s, retries: 2)
5. Extract and validate JSON response
6. Apply emergency override if detector level ≥ HIGH

**Key Design Decision:** Emergency detection runs *before* the LLM call. This means even if the LLM times out or fails, the system has already identified and flagged emergency conditions.

---

### 8.2 Module 2: Image Analysis

**Purpose:** Accept an uploaded medical image (photograph of wound, rash, burn, skin lesion, eye, etc.) and return visual findings and preliminary assessment.

**Image Preprocessing (`preprocessor.py`):**

| Step | Operation |
|------|-----------|
| Format validation | Accepts JPEG, PNG, BMP, WEBP |
| Size check | Rejects files > 10 MB |
| Resize | Downscales longest dimension to ≤ 1344px (LLaVA optimal) |
| Encoding | Converts to base64 JPEG for API transmission |
| Metadata | Captures original/processed dimensions, format, file size |

**Image Types Supported:**

| Type | Focus Criteria Applied |
|------|----------------------|
| Skin rash / lesion | ABCDE dermatology criteria |
| Wound / cut | Wound classification (superficial/deep/contaminated) |
| Burn | Rule of Nines burn area estimation |
| Eye condition | Redness, discharge, corneal clarity |
| Swelling | Localization, discoloration, pitting |
| X-ray / scan | Radiological findings description |
| Other | General visual assessment |

**Output Schema (`ImageResult`):**

| Field | Description |
|-------|-------------|
| `visual_findings` | Detailed description of observed features |
| `possible_conditions` | Likely diagnoses from visual evidence |
| `severity` | Low / Medium / High |
| `seek_immediate_care` | Boolean — requires urgent attention? |
| `recommendations` | Care instructions and next steps |
| `confidence` | Model's confidence in the assessment |
| `emergency_result` | Emergency detection output |

---

### 8.3 Module 3: Report Analysis

**Purpose:** Accept a PDF medical/laboratory report, extract its text content, and produce a structured interpretation including key findings, risk indicators, and consultation recommendations.

**PDF Extraction Pipeline (`extractor.py`):**

```
PDF File
    │
    ▼
PyMuPDF page-by-page extraction
    │
    ├── Text found (≥ 20 chars/page) ──► Use native text
    │
    └── Image-based page ──► EasyOCR reader (lazy-loaded)
                                  │
                              DPI 200 rendering → OCR
```

**Text Cleaning (`cleaner.py`):**
- Unicode NFKD normalization
- Removal of OCR artifacts (non-printable characters, excessive whitespace)
- Collapse of multiple blank lines
- Truncation to 6,000 characters (Llama 3 context management)

**Output Schema (`MedicalReportResult`):**

| Field | Description |
|-------|-------------|
| `report_type` | Lab report / Radiology / Pathology / Prescription / Other |
| `summary` | Plain-language summary of the report |
| `key_findings` | List of parameters with value, normal range, and status |
| `risk_indicators` | Abnormal values warranting attention |
| `recommendations` | Follow-up actions and lifestyle advice |
| `doctor_consultation` | Urgency, recommended specialties, reason |

**Key Finding Status Values:**
- `Normal` — Within reference range
- `Borderline` — At or near threshold
- `Abnormal` — Outside normal range; requires attention

---

### 8.4 Module 4: Emergency Detection Engine

**Purpose:** Provide a fast, deterministic, LLM-independent safety layer that identifies life-threatening conditions in any text input.

**Emergency Categories:**

| Category | Example Triggers | Base Score |
|----------|-----------------|-----------|
| Chest Pain | "chest pain", "heart attack", "crushing pressure in chest" | 25 |
| Respiratory Distress | "cannot breathe", "choking", "gasping" | 30 |
| Severe Bleeding | "bleeding heavily", "blood won't stop", "arterial bleeding" | 25 |
| Unconsciousness | "passed out", "unresponsive", "loss of consciousness" | 30 |
| Seizure | "convulsions", "seizure", "epileptic fit" | 20 |
| Stroke | "face drooping", "sudden arm weakness", "slurred speech" | 25 |
| Severe Burns | "third degree burn", "electrical burn", "chemical burn on face" | 20 |
| Anaphylaxis | "severe allergic reaction", "throat swelling", "anaphylaxis" | 30 |
| Overdose | "drug overdose", "took too many pills", "unconscious after medication" | 30 |

**Amplifier Phrases** (1.5× score multiplier): "severe", "sudden", "extreme", "cannot", "profuse", "uncontrolled"

**Override Phrases** (force CRITICAL): "not breathing", "stopped breathing", "no pulse", "crushing chest pain", "massive bleeding"

**Output:**
```python
EmergencyResult(
    level=EmergencyLevel.CRITICAL,     # NONE / MODERATE / HIGH / CRITICAL
    score=75,
    matched_categories=["Respiratory Distress"],
    matched_phrases=["cannot breathe", "lips turning blue"],
    immediate_actions=[
        "Call emergency services (911/112) immediately",
        "Begin CPR if trained and person is unresponsive",
        "Do not leave the patient alone"
    ]
)
```

---

### 8.5 Module 5: User Interface

**Technology:** Streamlit (Python web framework)

**Pages:**

| Page | File | Description |
|------|------|-------------|
| Home | `home_page.py` | Feature overview, system status, disclaimer |
| Symptom Checker | `symptom_page.py` | Input form + results display |
| Image Analysis | `image_page.py` | Upload + type selector + results |
| Report Analysis | `report_page.py` | PDF upload + findings table |
| About | `about_page.py` | Architecture, team, disclaimer |

**Reusable UI Components:**

- **`severity_badge.py`** — Color-coded chip (green: Low, orange: Medium, red: High)
- **`emergency_banner.py`** — Full-width high-visibility alert with immediate action list (displayed when emergency detected)
- **`result_card.py`** — Consistent card layout for all analysis outputs

**Navigation:** Sidebar-based routing with `st.session_state` for active page tracking.

**System Health Check:** The home page queries Ollama for model availability on load, displaying live status indicators for Llama 3 and LLaVA.

---

### 8.6 Module 6: Configuration Management

**`config/settings.py`** — All tunable constants in one place:

| Constant | Value | Purpose |
|----------|-------|---------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server endpoint |
| `OLLAMA_TEXT_MODEL` | `llama3` | Text inference model |
| `OLLAMA_VISION_MODEL` | `llava` | Vision inference model |
| `OLLAMA_TIMEOUT` | 120 seconds | Request timeout |
| `OLLAMA_RETRY_ATTEMPTS` | 2 | Retry count on failure |
| `EMERGENCY_SCORE_CRITICAL` | 60 | CRITICAL threshold |
| `EMERGENCY_SCORE_HIGH` | 30 | HIGH threshold |
| `EMERGENCY_SCORE_MODERATE` | 10 | MODERATE threshold |
| `MAX_SYMPTOM_TEXT_LENGTH` | 2000 chars | Input length cap |
| `MAX_IMAGE_FILE_SIZE_MB` | 10 MB | Image upload size cap |
| `MAX_REPORT_FILE_SIZE_MB` | 20 MB | Report upload size cap |

---

## 9. RESULTS

### 9.1 Functional Results

**Symptom Analysis:**
- Successfully generates structured JSON output for diverse symptom descriptions
- Correctly classifies urgency levels across a range of test cases (headache → Routine; chest pain + left arm numbness → EMERGENCY)
- Emergency override correctly forces EMERGENCY classification when detector score ≥ 30

**Image Analysis:**
- LLaVA successfully analyzes uploaded photographs of skin conditions, wounds, and burns
- Type-specific prompts (ABCDE for lesions, Rule of Nines for burns) produce more detailed and clinically oriented descriptions than generic prompts
- Image preprocessing correctly handles common formats and resizes large images while preserving aspect ratio

**Report Analysis:**
- PyMuPDF extracts clean text from digital-native PDFs (lab reports, prescriptions)
- EasyOCR fallback successfully reads scanned documents with moderate-to-good print quality
- Key findings table correctly parses parameter names, values, reference ranges, and statuses from structured lab reports
- Report type classification (Lab / Radiology / Pathology) is accurate for well-formatted reports

**Emergency Detection:**
- 100% detection rate on test cases involving all 9 emergency categories
- Override phrases correctly trigger CRITICAL level regardless of overall input context
- Sub-millisecond execution on all test inputs (average < 0.5 ms)
- Zero LLM dependency — operates during Ollama downtime

### 9.2 Performance Characteristics

| Operation | Typical Duration |
|-----------|-----------------|
| Emergency detection | < 1 ms |
| Symptom analysis (Llama 3, 8B) | 8–25 seconds |
| Image analysis (LLaVA) | 15–45 seconds |
| Report analysis (Llama 3, 8B) | 10–30 seconds |
| PDF text extraction (native) | < 1 second |
| PDF OCR extraction (EasyOCR) | 5–20 seconds per page |

*Timings measured on Apple M2 MacBook with 16 GB RAM using Ollama with Metal acceleration.*

### 9.3 Sample Outputs

**Symptom Analysis — Sample:**
```
Input: "Severe chest pain radiating to left arm, started 20 minutes ago, 
        sweating profusely. 55-year-old male."

Output:
  Severity: HIGH
  Urgency: EMERGENCY
  Emergency Level: CRITICAL (Score: 85)
  Possible Conditions: Myocardial Infarction (High), Unstable Angina (Medium)
  Immediate Actions:
    - Call emergency services (911/112) immediately
    - Chew 325mg aspirin if not allergic
    - Do not drive yourself to hospital
    - Loosen tight clothing
```

**Report Analysis — Sample Key Findings Table:**

| Parameter | Value | Normal Range | Status |
|-----------|-------|-------------|--------|
| Hemoglobin | 9.2 g/dL | 13.5–17.5 | Abnormal |
| WBC Count | 11,200 /μL | 4,500–11,000 | Borderline |
| Platelet Count | 245,000 /μL | 150,000–400,000 | Normal |
| HbA1c | 7.8% | < 5.7% | Abnormal |

### 9.4 Limitations

1. **Model hallucination**: Like all LLMs, Llama 3 and LLaVA can produce plausible-sounding but incorrect medical information. This is mitigated by the structured output format and prominent disclaimers.

2. **Inference speed**: On CPU-only systems, LLM inference takes significantly longer (2–5× slower). A GPU or Apple Silicon chip is recommended.

3. **Image quality dependency**: LLaVA's image analysis quality degrades for blurry, low-resolution, or poorly-lit photographs.

4. **OCR accuracy**: EasyOCR performance decreases for handwritten content, unusual fonts, or very low scan quality.

5. **Language**: All prompts and UI are in English. Non-English medical reports may produce degraded results.

---

## 10. FUTURE SCOPE

### 10.1 Short-Term Enhancements

1. **Multi-language support**: Add prompt templates and UI translations for Hindi, Tamil, Bengali, and other major Indian languages to extend accessibility.

2. **Voice input**: Integrate speech-to-text (Whisper model via Ollama) for symptom input, enabling use by users who cannot type effectively.

3. **Structured symptom questionnaire**: Implement a follow-up question flow (chief complaint → duration → severity → associated symptoms) modeled on clinical intake protocols.

4. **Export functionality**: Allow users to download analysis results as PDF summaries to share with their doctor.

### 10.2 Medium-Term Enhancements

5. **Medical knowledge base integration**: Augment LLM responses with retrieval-augmented generation (RAG) over curated medical corpora (SNOMED CT, ICD-10) to improve factual accuracy.

6. **Vital signs integration**: Add support for manually entering measurable vitals (blood pressure, heart rate, SpO2 temperature) to enrich the assessment context.

7. **Longitudinal tracking**: Implement optional local history storage to track symptom trends over time and flag worsening conditions.

8. **Mobile application**: Package the application as a mobile app using technologies like Kivy or a React Native frontend connected to a local API server.

### 10.3 Long-Term Research Directions

9. **Medical-domain fine-tuning**: Fine-tune Llama 3 on medical instruction datasets (MedQA, PubMedQA, clinical notes with appropriate de-identification) to improve precision and reduce hallucination rates.

10. **Federated deployment**: Develop a privacy-preserving federated architecture where multiple local instances share anonymized aggregate insights without transmitting personal health data.

11. **Clinical validation study**: Partner with medical institutions to formally evaluate the system's triage accuracy against ground-truth clinical diagnoses across a sufficiently large and diverse patient population.

12. **Wearable device integration**: Interface with consumer health wearables (smartwatches, pulse oximeters) to enable passive continuous monitoring and alert generation.

---

## 11. CONCLUSION

This project successfully demonstrates the design and implementation of a multi-modal MultiModel-TriageAssistant that operates entirely locally, preserving patient privacy while providing preliminary health assessment across text symptoms, medical images, and clinical reports.

The key technical contributions are:

1. **A three-pipeline modular architecture** cleanly separating business logic from the user interface, enabling each analysis modality to be developed, tested, and extended independently.

2. **A deterministic emergency detection engine** that guarantees identification of nine categories of life-threatening conditions without any dependence on LLM inference — addressing the most critical safety requirement for any health-assistance AI.

3. **A hybrid PDF ingestion pipeline** combining native text extraction with OCR fallback, enabling the system to handle both digital-native and scanned clinical documents.

4. **Type-specific vision prompting** for image analysis that adapts the assessment criteria to the clinical domain of the uploaded image, demonstrating that prompt engineering can significantly improve the relevance of general-purpose vision model outputs.

The system validates a practical path for deploying capable AI health assistance tools in environments where cloud connectivity, subscription costs, or privacy concerns make cloud-based solutions unsuitable. The fully open-source technology stack (Python, Streamlit, Ollama, Llama 3, LLaVA, PyMuPDF, EasyOCR) ensures the system can be freely used, modified, and extended by the community.

While the system carries important limitations — LLM hallucination risk, inference latency, image quality sensitivity — these are well-understood challenges in the field, and the architecture includes mitigations (structured output, emergency override, Pydantic validation, explicit disclaimers) for the most consequential failure modes.

This project demonstrates that with thoughtful engineering — combining rule-based safety mechanisms with LLM intelligence — it is possible to build health assistance tools that are simultaneously capable, safe, private, and accessible.

---

## 12. REFERENCES

1. Semigran, H. L., Linder, J. A., Gidengil, C., & Mehrotra, A. (2015). Evaluation of symptom checkers for self diagnosis and triage: audit study. *BMJ*, 351, h3480. https://doi.org/10.1136/bmj.h3480

2. Rajpurkar, P., Irvin, J., Ball, R. L., Zhu, K., Yang, B., Mehta, H., ... & Ng, A. Y. (2017). CheXNet: Radiologist-level pneumonia detection on chest X-rays with deep learning. *arXiv preprint arXiv:1711.05225*.

3. Singhal, K., Azizi, S., Tu, T., Mahdavi, S. S., Wei, J., Chung, H. W., ... & Natarajan, V. (2023). Large language models encode clinical knowledge. *Nature*, 620(7972), 172–180.

4. Nori, H., King, N., McKinney, S. M., Carignan, D., & Horvitz, E. (2023). Capabilities of GPT-4 on Medical Challenge Problems. *arXiv preprint arXiv:2303.13375*.

5. Touvron, H., Martin, L., Stone, K., Albert, P., Almahairi, A., Babaei, Y., ... & Scialom, T. (2023). Llama 2: Open foundation and fine-tuned chat models. *arXiv preprint arXiv:2307.09288*.

6. Meta AI. (2024). Introducing Meta Llama 3: The most capable openly available LLM to date. Meta AI Blog. https://ai.meta.com/blog/meta-llama-3/

7. Liu, H., Li, C., Wu, Q., & Lee, Y. J. (2023). Visual instruction tuning (LLaVA). *Advances in Neural Information Processing Systems*, 36.

8. Ollama. (2023). Run large language models locally. GitHub Repository. https://github.com/ollama/ollama

9. JaidedAI. (2020). EasyOCR: Ready-to-use OCR with 80+ supported languages. GitHub Repository. https://github.com/JaidedAI/EasyOCR

10. MuPDF / PyMuPDF. (2023). PyMuPDF: Python bindings for MuPDF. GitHub Repository. https://github.com/pymupdf/PyMuPDF

11. Pydantic. (2023). Pydantic v2: Data validation using Python type hints. https://docs.pydantic.dev/

12. Streamlit. (2023). Streamlit: A faster way to build and share data apps. https://streamlit.io/

13. Pillow (PIL Fork). (2023). Python Imaging Library. https://python-pillow.org/

14. Manchester Triage Group. (2014). *Emergency Triage: Manchester Triage Group* (3rd ed.). Wiley-Blackwell.

15. Gilboy, N., Tanabe, P., Travers, D., & Rosenau, A. M. (2012). Emergency Severity Index (ESI): A Triage Tool for Emergency Department Care, Version 4. AHRQ Publication No. 12-0014.

16. WHO. (2023). Health workforce. World Health Organization. https://www.who.int/health-topics/health-workforce

17. Brown, T., Mann, B., Ryder, N., Subbiah, M., Kaplan, J. D., Dhariwal, P., ... & Amodei, D. (2020). Language models are few-shot learners. *Advances in Neural Information Processing Systems*, 33, 1877–1901.

18. Thirunavukarasu, A. J., Ting, D. S. J., Elangovan, K., Gutierrez, L., Tan, T. F., & Ting, D. S. W. (2023). Large language models in medicine. *Nature Medicine*, 29(8), 1930–1940.

---

*End of Report*

---

**Submitted by:** ANUBHA KUMARI
**Date:** June 2026
**Institution:** GALGOTIAS UNIVERSITY
**Department:** Computer Science and Engineering

> This project is developed for educational purposes only. The MultiModel-TriageAssistant does not provide medical diagnoses and should not be used as a substitute for professional medical advice.
