# MacBook Setup Guide — MultiModel-TriageAssistant

## Prerequisites

- macOS 12 (Monterey) ya newer
- Internet connection (models download ke liye ~8 GB)
- Minimum 8 GB RAM recommended (Apple Silicon M1/M2/M3 best chalega)

---

## Step 1: Homebrew Install karo

Homebrew macOS ka package manager hai — isse Python aur baaki tools easily install honge.

1. Terminal kholo (Spotlight me "Terminal" search karo)
2. Yeh command chalao:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

3. Install ke baad jo "Next steps" instructions aaye (PATH wali `eval` line), unhe chalao — Apple Silicon pe aam taur pe:

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

4. Verify karo:

```bash
brew --version
```

---

## Step 2: Python Install karo

```bash
brew install python@3.11
```

> Note: Python 3.11 use karo — 3.12+ me easyocr issues ho sakte hain.

Verify karo:

```bash
python3.11 --version
```

---

## Step 3: Ollama Install karo

1. [https://ollama.com/download](https://ollama.com/download) pe jao → macOS app download karo
   - Ya Homebrew se: `brew install ollama`
2. App kholo — menu bar me Ollama icon dikhega (background me chal raha hoga)
3. Models download karo:

```bash
ollama pull llama3
ollama pull llava
```

> Note: llama3 ~4.7 GB aur llava ~4.7 GB hai — fast internet pe 10-20 min lagenge

4. Verify karo (dono models dikhne chahiye):

```bash
ollama list
```

---

## Step 4: Project Files Copy karo

Project folder ko MacBook pe copy karo — koi bhi ek tarika use karo:

- **Pendrive / AirDrop:** directly copy-paste karo
- **GitHub:** `git clone <your-repo-url>`
- **ZIP:** Google Drive / WhatsApp se bhejo, extract karo

---

## Step 5: Virtual Environment banao

```bash
cd path/to/MultiModel-TriageAssistant
python3.11 -m venv venv
source venv/bin/activate
```

Activate hone ke baad terminal me `(venv)` prefix dikhega.

---

## Step 6: Dependencies Install karo

```bash
pip install -r requirements.txt
```

> Note: `easyocr` aur `torch` bade packages hain (~2 GB), time lagega

---

## Step 7: App Chalao

```bash
streamlit run triage.py
```

Browser automatically open hoga — `http://localhost:8501`

---

## Har Baar App Open Karne Ke Liye

```bash
cd path/to/MultiModel-TriageAssistant
source venv/bin/activate
streamlit run triage.py
```

> Ollama app login pe automatically background me run hota hai — agar band ho to Applications se kholo, ya Terminal me `ollama serve` chalao.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `easyocr` install fail | `pip install easyocr --no-cache-dir` |
| `torch` error | `pip install torch` (macOS pe CPU/MPS build default aata hai) |
| `command not found: brew` | `eval "$(/opt/homebrew/bin/brew shellenv)"` chalao, phir Terminal restart karo |
| Ollama connection error | Menu bar me Ollama check karo, ya Terminal me `ollama serve` run karo |
| Port already in use | `streamlit run triage.py --server.port 8502` |
| `python3.11: command not found` | `brew install python@3.11` dobara chalao |
