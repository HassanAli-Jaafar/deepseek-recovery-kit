#!/usr/bin/env python3
"""
DeepSeek Recovery Kit
Recover, search, and export your DeepSeek chat history
MIT License - Free for everyone
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime
from html import escape

def extract_from_json(json_file, start_date=None, end_date=None):
    """Extract messages, code snippets, and callbacks from DeepSeek export"""
    
    print(f"📂 Loading: {json_file}")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    messages = []
    code_snippets = []
    callbacks = set()
    decisions = []
    
    for conv in data:
        mapping = conv.get('mapping', {})
        for node in mapping.values():
            msg = node.get('message')
            if not msg:
                continue
            
            # Parse timestamp
            ts_str = msg.get('inserted_at', '')
            if ts_str:
                try:
                    msg_date = datetime.strptime(ts_str[:19], '%Y-%m-%dT%H:%M:%S')
                except:
                    continue
                
                # Filter by date if specified
                if start_date and msg_date.date() < start_date:
                    continue
                if end_date and msg_date.date() > end_date:
                    continue
            else:
                msg_date = datetime.now()
            
            for frag in msg.get('fragments', []):
                if frag['type'] not in ['REQUEST', 'RESPONSE']:
                    continue
                
                content = frag.get('content', '')
                if not content:
                    continue
                
                messages.append({
                    'type': frag['type'],
                    'content': content,
                    'timestamp': ts_str[:19] if ts_str else '',
                    'date': msg_date.strftime('%Y-%m-%d')
                })
                
                # Extract code blocks
                code_matches = re.findall(r'```(\w+)?\n(.*?)```', content, re.DOTALL)
                for lang, code in code_matches:
                    code_snippets.append({
                        'language': lang or 'text',
                        'code': code.strip(),
                        'date': msg_date.strftime('%Y-%m-%d')
                    })
                
                # Extract callbacks (Telegram bot pattern)
                found_cbs = re.findall(r'case\s+\"([a-zA-Z_][a-zA-Z0-9_]*)\"', content)
                callbacks.update(found_cbs)
                
                # Extract decisions
                decision_patterns = [
                    r'(?:we\'ll|we will|let\'s|agreed|decided)\s+([^.!]+)',
                ]
                for pattern in decision_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        decisions.append(match[:200])
    
    return messages, code_snippets, list(callbacks), decisions

def generate_html(messages, code_snippets, callbacks, decisions, output_file):
    """Generate beautiful HTML report"""
    
    # Group messages by date
    messages_by_date = {}
    for msg in messages:
        date = msg['date']
        if date not in messages_by_date:
            messages_by_date[date] = []
        messages_by_date[date].append(msg)
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>DeepSeek Recovery Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background: #f0f2f5; }}
        .container {{ max-width: 1200px; margin: auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; }}
        .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px; }}
        .stat-card {{ background: white; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .tabs {{ display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }}
        .tab-btn {{ background: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; }}
        .tab-btn.active {{ background: #667eea; color: white; }}
        .tab-content {{ display: none; background: white; padding: 20px; border-radius: 15px; }}
        .tab-content.active {{ display: block; }}
        .message {{ margin-bottom: 15px; padding: 15px; border-radius: 10px; }}
        .REQUEST {{ background: #e3f2fd; border-left: 4px solid #2196f3; }}
        .RESPONSE {{ background: #e8f5e9; border-left: 4px solid #4caf50; }}
        .date-group {{ margin-bottom: 25px; }}
        .date-title {{ background: #667eea; color: white; padding: 8px 12px; border-radius: 8px; margin-bottom: 10px; }}
        pre {{ background: #2d2d2d; color: #f8f8f2; padding: 12px; border-radius: 8px; overflow-x: auto; }}
        .callback-badge {{ display: inline-block; background: #667eea; color: white; padding: 5px 12px; margin: 5px; border-radius: 20px; font-size: 12px; }}
        .search-box {{ width: 100%; padding: 10px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 8px; }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🤖 DeepSeek Recovery Kit</h1>
        <p>Recovered {len(messages)} messages, {len(code_snippets)} code snippets, {len(callbacks)} callbacks</p>
    </div>
    
    <div class="stats">
        <div class="stat-card"><div class="stat-number">{len(messages)}</div><div>💬 Messages</div></div>
        <div class="stat-card"><div class="stat-number">{len(code_snippets)}</div><div>📝 Code Blocks</div></div>
        <div class="stat-card"><div class="stat-number">{len(callbacks)}</div><div>🔘 Callbacks</div></div>
        <div class="stat-card"><div class="stat-number">{len(decisions)}</div><div>✅ Decisions</div></div>
    </div>
    
    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('messages')">💬 Messages</button>
        <button class="tab-btn" onclick="switchTab('code')">📝 Code ({len(code_snippets)})</button>
        <button class="tab-btn" onclick="switchTab('callbacks')">🔘 Callbacks ({len(callbacks)})</button>
    </div>
    
    <div id="messages-tab" class="tab-content active">
        <input type="text" class="search-box" id="searchInput" placeholder="🔍 Search messages..." onkeyup="filterMessages()">
        <div id="messages-container">
'''
    
    for date in sorted(messages_by_date.keys(), reverse=True):
        html += f'<div class="date-group"><div class="date-title">📅 {date}</div>'
        for msg in messages_by_date[date]:
            content = escape(msg['content']).replace('\n', '<br>')
            html += f'''
            <div class="message {msg['type']}">
                <small style="color:#888">{msg['timestamp']}</small><br>
                {content}
            </div>
            '''
        html += '</div>'
    
    html += f'''
        </div>
    </div>
    
    <div id="code-tab" class="tab-content">
        {''.join(f'<strong>{s["language"].upper()}</strong><pre><code>{escape(s["code"][:2000])}</code></pre><hr>' for s in code_snippets[:100])}
        {f'<p>... and {len(code_snippets) - 100} more snippets</p>' if len(code_snippets) > 100 else ''}
    </div>
    
    <div id="callbacks-tab" class="tab-content">
        {''.join(f'<span class="callback-badge">{cb}</span>' for cb in sorted(callbacks))}
    </div>
</div>

<script>
    function switchTab(tabName) {{
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.getElementById(tabName + '-tab').classList.add('active');
        event.target.classList.add('active');
    }}
    
    function filterMessages() {{
        let search = document.getElementById('searchInput').value.toLowerCase();
        let messages = document.querySelectorAll('#messages-container .message');
        messages.forEach(msg => {{
            msg.style.display = msg.innerText.toLowerCase().includes(search) ? 'block' : 'none';
        }});
    }}
</script>
</body>
</html>'''
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ HTML saved: {output_file}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='DeepSeek Recovery Kit')
    parser.add_argument('json_file', help='Path to DeepSeek export JSON')
    parser.add_argument('-o', '--output', default='recovery_report.html', help='Output HTML file')
    parser.add_argument('-s', '--start-date', help='Start date (YYYY-MM-DD)')
    parser.add_argument('-e', '--end-date', help='End date (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    start = datetime.strptime(args.start_date, '%Y-%m-%d').date() if args.start_date else None
    end = datetime.strptime(args.end_date, '%Y-%m-%d').date() if args.end_date else None
    
    messages, codes, callbacks, decisions = extract_from_json(args.json_file, start, end)
    generate_html(messages, codes, callbacks, decisions, args.output)
    print(f"\n📊 Summary:")
    print(f"   Messages: {len(messages)}")
    print(f"   Code snippets: {len(codes)}")
    print(f"   Callbacks: {len(callbacks)}")
    print(f"   Decisions: {len(decisions)}")

if __name__ == '__main__':
    main()
