# Windows Setup Guide — MultiModel-TriageAssistant

## Prerequisites

- Windows 10 / 11
- Internet connection (models download ke liye ~8 GB)
- Minimum 8 GB RAM recommended

---

## Step 1: Python Install karo

1. [https://python.org/downloads](https://python.org/downloads) pe jao
2. **Python 3.11** download karo (3.12+ me easyocr issues ho sakte hain)
3. Installer chalao — **"Add Python to PATH"** checkbox zaroor tick karo
4. Verify karo:

```cmd
python --version
```

---

## Step 2: Ollama Install karo

1. [https://ollama.com/download](https://ollama.com/download) pe jao → Windows installer download karo
2. Install karo — background me automatically start hoga
3. Models download karo:

```cmd
ollama pull llama3
ollama pull llava
```

> Note: llama3 ~4.7 GB aur llava ~4.7 GB hai — fast internet pe 10-20 min lagenge

4. Verify karo (dono models dikhne chahiye):

```cmd
ollama list
```

---

## Step 3: Project Files Copy karo

Project folder ko Windows laptop pe copy karo — koi bhi ek tarika use karo:

- **Pendrive:** directly copy-paste karo
- **GitHub:** `git clone <your-repo-url>`
- **ZIP:** Google Drive / WhatsApp se bhejo, extract karo

---

## Step 4: Virtual Environment banao

```cmd
cd path\to\MultiModel-TriageAssistant
python -m venv venv
venv\Scripts\activate
```

Activate hone ke baad terminal me `(venv)` prefix dikhega.

---

## Step 5: Dependencies Install karo

```cmd
pip install -r requirements.txt
```

> Note: `easyocr` aur `torch` bade packages hain (~2 GB), time lagega

---

## Step 6: App Chalao

```cmd
streamlit run triage.py
```

Browser automatically open hoga — `http://localhost:8501`

---

## Har Baar App Open Karne Ke Liye

```cmd
cd path\to\MultiModel-TriageAssistant
venv\Scripts\activate
streamlit run triage.py
```

> Ollama Windows startup pe automatically background me run hota hai — alag se start karne ki zaroorat nahi.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `easyocr` install fail | `pip install easyocr --no-cache-dir` |
| `torch` error | `pip install torch --index-url https://download.pytorch.org/whl/cpu` |
| Ollama connection error | Task Manager me Ollama check karo, ya CMD me `ollama serve` run karo |
| Port already in use | `streamlit run triage.py --server.port 8502` |
| `venv\Scripts\activate` blocked | PowerShell me run karo: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
