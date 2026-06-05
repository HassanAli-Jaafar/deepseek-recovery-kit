#!/usr/bin/env python3
"""
DeepSeek Recovery Kit - GUI Version
With date picker, progress bar, and beautiful interface
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime
from html import escape
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import threading

class DeepSeekRecoveryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🌟 DeepSeek Recovery Kit")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        self.root.configure(bg='#1a1a2e')
        
        self.json_file = None
        
        # Colors
        self.bg_color = "#1a1a2e"
        self.accent_color = "#e94560"
        self.secondary = "#0f3460"
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(main_frame, text="🌟 DeepSeek Recovery Kit", 
                        font=("Arial", 20, "bold"), bg=self.bg_color, fg='white')
        title.pack(pady=10)
        
        subtitle = tk.Label(main_frame, text="Recover, Search, and Export Your Chat History", 
                           font=("Arial", 10), bg=self.bg_color, fg='#888')
        subtitle.pack()
        
        # File selection
        file_frame = tk.Frame(main_frame, bg=self.bg_color)
        file_frame.pack(pady=20, fill=tk.X)
        
        self.file_label = tk.Label(file_frame, text="📂 No file selected", 
                                   bg=self.secondary, fg='white', padx=10, pady=5)
        self.file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.file_btn = tk.Button(file_frame, text="Browse", command=self.select_file,
                                  bg=self.accent_color, fg='white', padx=15, pady=5)
        self.file_btn.pack(side=tk.RIGHT, padx=5)
        
        # Date range
        date_frame = tk.Frame(main_frame, bg=self.bg_color)
        date_frame.pack(pady=15)
        
        tk.Label(date_frame, text="📅 START DATE:", font=("Arial", 10, "bold"),
                bg=self.bg_color, fg=self.accent_color).pack(side=tk.LEFT, padx=10)
        
        self.start_date = DateEntry(date_frame, width=12, date_pattern='yyyy-mm-dd')
        self.start_date.pack(side=tk.LEFT, padx=5)
        self.start_date.set_date(datetime(2025, 3, 25))
        
        tk.Label(date_frame, text="📅 END DATE:", font=("Arial", 10, "bold"),
                bg=self.bg_color, fg=self.accent_color).pack(side=tk.LEFT, padx=10)
        
        self.end_date = DateEntry(date_frame, width=12, date_pattern='yyyy-mm-dd')
        self.end_date.pack(side=tk.LEFT, padx=5)
        self.end_date.set_date(datetime.now())
        
        # Options
        options_frame = tk.Frame(main_frame, bg=self.bg_color)
        options_frame.pack(pady=15)
        
        self.full_content = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="Include FULL message content (may be large)",
                      variable=self.full_content, bg=self.bg_color, fg='white',
                      selectcolor=self.bg_color).pack(anchor=tk.W, padx=30)
        
        # Progress
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', length=500)
        self.progress.pack(pady=15)
        
        # Status
        self.status = tk.Label(main_frame, text="✅ Ready", bg=self.bg_color, fg='#4CAF50')
        self.status.pack()
        
        # Extract button
        self.extract_btn = tk.Button(main_frame, text="🚀 START EXTRACTION", 
                                     font=("Arial", 12, "bold"),
                                     bg=self.accent_color, fg='white',
                                     command=self.start_extraction,
                                     padx=30, pady=10)
        self.extract_btn.pack(pady=20)
    
    def select_file(self):
        filename = filedialog.askopenfilename(
            title="Select DeepSeek Export JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.json_file = filename
            self.file_label.config(text=f"📂 {Path(filename).name}")
    
    def start_extraction(self):
        if not self.json_file:
            messagebox.showerror("Error", "Please select a JSON file first!")
            return
        
        self.extract_btn.config(state=tk.DISABLED, text="⏳ PROCESSING...")
        self.progress.start()
        self.status.config(text="📂 Loading JSON...", fg='#FFA500')
        
        thread = threading.Thread(target=self.extract_data)
        thread.daemon = True
        thread.start()
    
    def extract_data(self):
        start_date = self.start_date.get_date()
        end_date = self.end_date.get_date()
        full_content = self.full_content.get()
        
        self.status.config(text="📖 Reading file...")
        
        with open(self.json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.status.config(text=f"🔍 Filtering {start_date} → {end_date}...")
        
        messages = []
        code_snippets = []
        callbacks = set()
        
        for conv in data:
            mapping = conv.get('mapping', {})
            for node in mapping.values():
                msg = node.get('message')
                if not msg:
                    continue
                
                ts_str = msg.get('inserted_at', '')
                if ts_str:
                    try:
                        msg_date = datetime.strptime(ts_str[:19], '%Y-%m-%dT%H:%M:%S').date()
                    except:
                        continue
                    
                    if not (start_date <= msg_date <= end_date):
                        continue
                
                for frag in msg.get('fragments', []):
                    if frag['type'] not in ['REQUEST', 'RESPONSE']:
                        continue
                    
                    content = frag.get('content', '')
                    if not content:
                        continue
                    
                    if not full_content and len(content) > 2000:
                        content = content[:2000] + "\n... (trimmed)"
                    
                    messages.append({
                        'type': frag['type'],
                        'content': content,
                        'timestamp': ts_str[:19] if ts_str else '',
                        'date': msg_date.strftime('%Y-%m-%d')
                    })
                    
                    code_matches = re.findall(r'```(\w+)?\n(.*?)```', content, re.DOTALL)
                    for lang, code in code_matches:
                        code_snippets.append({
                            'language': lang or 'text',
                            'code': code.strip()[:1000]
                        })
                    
                    callbacks.update(re.findall(r'case\s+\"([a-zA-Z_][a-zA-Z0-9_]*)\"', content))
        
        self.status.config(text="📝 Generating HTML...")
        
        output_file = f"DeepSeek_Recovery_{start_date}_to_{end_date}.html"
        self.generate_html(messages, code_snippets, list(callbacks), output_file)
        
        self.progress.stop()
        
        messagebox.showinfo("Complete!", 
                           f"✅ Extraction complete!\n\n"
                           f"📊 {len(messages)} messages\n"
                           f"📝 {len(code_snippets)} code snippets\n"
                           f"🔘 {len(callbacks)} callbacks\n\n"
                           f"💾 Saved as: {output_file}")
        
        self.status.config(text="✅ Complete!", fg='#4CAF50')
        self.extract_btn.config(state=tk.NORMAL, text="🚀 START EXTRACTION")
    
    def generate_html(self, messages, code_snippets, callbacks, output_file):
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>DeepSeek Recovery Report</title>
    <style>
        body {{ font-family: Arial; margin: 20px; background: #f0f2f5; }}
        .container {{ max-width: 1000px; margin: auto; }}
        .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; border-radius: 15px; }}
        .stats {{ display: flex; gap: 15px; margin: 20px 0; }}
        .stat {{ background: white; padding: 15px; border-radius: 10px; text-align: center; flex: 1; }}
        .stat-num {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .tabs {{ display: flex; gap: 10px; margin-bottom: 20px; }}
        .tab {{ background: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; }}
        .tab.active {{ background: #667eea; color: white; }}
        .content {{ display: none; background: white; padding: 20px; border-radius: 15px; }}
        .content.active {{ display: block; }}
        .message {{ padding: 10px; margin: 10px 0; border-radius: 8px; }}
        .REQUEST {{ background: #e3f2fd; }}
        .RESPONSE {{ background: #e8f5e9; }}
        pre {{ background: #2d2d2d; color: #f8f8f2; padding: 10px; overflow-x: auto; }}
        .badge {{ display: inline-block; background: #667eea; color: white; padding: 5px 10px; margin: 5px; border-radius: 15px; }}
        .search {{ width: 100%; padding: 10px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 8px; }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🤖 DeepSeek Recovery Kit</h1>
        <p>{len(messages)} messages | {len(code_snippets)} code blocks | {len(callbacks)} callbacks</p>
    </div>
    <div class="stats">
        <div class="stat"><div class="stat-num">{len(messages)}</div><div>💬 Messages</div></div>
        <div class="stat"><div class="stat-num">{len(code_snippets)}</div><div>📝 Code</div></div>
        <div class="stat"><div class="stat-num">{len(callbacks)}</div><div>🔘 Callbacks</div></div>
    </div>
    <div class="tabs">
        <button class="tab active" onclick="switchTab('messages')">Messages</button>
        <button class="tab" onclick="switchTab('code')">Code</button>
        <button class="tab" onclick="switchTab('callbacks')">Callbacks</button>
    </div>
    <div id="messages" class="content active">
        <input type="text" class="search" id="searchMsg" placeholder="Search..." onkeyup="filterMessages()">
        <div id="msgList">
            {''.join(f'<div class="message {m["type"]}"><small>{m["timestamp"]}</small><br>{escape(m["content"])}</div>' for m in messages[:500])}
        </div>
    </div>
    <div id="code" class="content">
        {''.join(f'<strong>{s["language"]}</strong><pre><code>{escape(s["code"])}</code></pre><hr>' for s in code_snippets[:100])}
    </div>
    <div id="callbacks" class="content">
        {''.join(f'<span class="badge">{cb}</span>' for cb in sorted(callbacks))}
    </div>
</div>
<script>
    function switchTab(tab) {{
        document.querySelectorAll('.content').forEach(c => c.classList.remove('active'));
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.getElementById(tab).classList.add('active');
        event.target.classList.add('active');
    }}
    function filterMessages() {{
        let search = document.getElementById('searchMsg').value.toLowerCase();
        let msgs = document.querySelectorAll('#msgList .message');
        msgs.forEach(m => m.style.display = m.innerText.toLowerCase().includes(search) ? 'block' : 'none');
    }}
</script>
</body>
</html>'''
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ Saved: {output_file}")

def main():
    root = tk.Tk()
    app = DeepSeekRecoveryGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
