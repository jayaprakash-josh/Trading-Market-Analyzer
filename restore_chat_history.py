"""
Restore Chat History & Brain Artifacts for Antigravity / Gemini Agent.

Usage on any new machine:
    python restore_chat_history.py
"""

import os
import sys
import zipfile
import pathlib

CONVERSATION_ID = "2b1a2a10-3c26-4acb-b23c-67acce8c2e6c"

def main():
    print("=" * 60)
    print(" Antigravity Chat History & Brain Restorer")
    print("=" * 60)
    
    # 1. Locate the backup archive
    repo_root = pathlib.Path(__file__).parent.resolve()
    zip_path = repo_root / "brain_backup" / f"{CONVERSATION_ID}.zip"
    
    if not zip_path.exists():
        print(f"[ERROR] Backup zip not found at: {zip_path}")
        sys.exit(1)
        
    print(f"[*] Found backup archive: {zip_path.name} ({zip_path.stat().st_size / (1024*1024):.2f} MB)")
    
    # 2. Determine target Antigravity brain path
    user_home = pathlib.Path.home()
    target_dir = user_home / ".gemini" / "antigravity" / "brain" / CONVERSATION_ID
    
    print(f"[*] Target directory on this machine:")
    print(f"    {target_dir}")
    
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # 3. Extract all brain files
    print("[*] Extracting conversation history, transcripts, and artifacts...")
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(target_dir)
        
    print("[+] SUCCESS! Chat history and brain state successfully restored.")
    print("=" * 60)
    print(f"Conversation ID: {CONVERSATION_ID}")
    print(f"Location:        {target_dir}")
    print("=" * 60)
    print("You can now open Antigravity / Gemini IDE and resume your conversation!")

if __name__ == "__main__":
    main()
