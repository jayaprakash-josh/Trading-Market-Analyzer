# Antigravity Chat History & Session Migration Guide

This directory and the [`brain_backup/`](../../brain_backup) folder contain the complete session state, agent reasoning transcripts, and artifacts for the **NSE Trading Market Analyzer** project (Conversation ID: `2b1a2a10-3c26-4acb-b23c-67acce8c2e6c`).

---

## 🚀 Quick Setup on a New Machine

When cloning this repository on a new laptop or desktop, follow these 3 simple steps to restore the full conversation history and IDE agent state:

### Step 1: Clone the Repo & Pull Git LFS (for the SQLite DB)
```bash
git clone https://github.com/jayaprakash-josh/Trading-Market-Analyzer.git
cd Trading-Market-Analyzer
git lfs pull
```

### Step 2: Run the One-Click Chat History Restorer
Run the included python script from the repository root:
```bash
python restore_chat_history.py
```

### What this script does automatically:
1. Detects your user home directory on Windows, macOS, or Linux.
2. Extracts [`brain_backup/2b1a2a10-3c26-4acb-b23c-67acce8c2e6c.zip`](../../brain_backup/2b1a2a10-3c26-4acb-b23c-67acce8c2e6c.zip) directly into:
   * **Windows:** `C:\Users\<username>\.gemini\antigravity\brain\2b1a2a10-3c26-4acb-b23c-67acce8c2e6c`
   * **Linux/Mac:** `~/.gemini/antigravity/brain/2b1a2a10-3c26-4acb-b23c-67acce8c2e6c`
3. Restores all agent memories, subagent transcripts, execution tasks, and design documents.

### Step 3: Open Antigravity / Gemini Agent
Open the repository folder in the IDE. The assistant will detect the existing conversation ID and seamlessly continue where you left off!

---

## 📖 Manual Import (Alternative)
If you prefer not to run the python script, you can manually extract the backup:
1. Open [`brain_backup/2b1a2a10-3c26-4acb-b23c-67acce8c2e6c.zip`](../../brain_backup/2b1a2a10-3c26-4acb-b23c-67acce8c2e6c.zip).
2. Extract all contents into:
   ```text
   ~/.gemini/antigravity/brain/2b1a2a10-3c26-4acb-b23c-67acce8c2e6c/
   ```

---

## 🧠 What is Restored?
* **Full Multi-Day Chat & Task Logs:** `transcript.jsonl` and `transcript_full.jsonl`.
* **Subagents & Transcripts:** `fno_builder`, `Short Engine Integrator`, etc.
* **Architecture & Flow Documents:** `current_business_flow.md`, `fno_implementation_plan.md`, `implementation_flow.md`.
* **Execution Logs:** Background task logs from live market execution runs.
