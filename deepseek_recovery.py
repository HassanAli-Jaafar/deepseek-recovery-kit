#!/usr/bin/env python3
"""
DeepSeek Recovery Kit - ULTRA FAST CLI Version
With timers, limited output for speed, and clean HTML
"""

import json
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime
from html import escape

def extract_from_json_ultrafast(json_file, start_date=None, end_date=None):
    """ULTRA FAST extraction - limits display for speed"""
    
    messages = []
    code_snippets = []
    callbacks = set()
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for conv in data:
        mapping = conv.get('mapping', {})
        for node in mapping.values():
            msg = node.get('message')
            if not msg:
                continue
            
            ts_str = msg.get('inserted_at', '')
            if ts_str:
                try:
                    msg_date = datetime.strptime(ts_str[:19], '%Y-%m-%dT%H:%M:%S')
                except:
                    continue
                
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
                
                # Limit messages for display (first 1500)
                if len(messages) < 1500:
                    msg_content = content[:1500] if len(content) > 1500 else content
                    messages.append({
                        'type': frag['type'],
                        'content': msg_content,
                        'timestamp': ts_str[:16] if ts_str else '',
                        'date': msg_date.strftime('%Y-%m-%d')
                    })
                
                # Limit code snippets (first 300)
                if len(code_snippets) < 300:
                    code_matches = re.findall(r'```(\w+)?\n(.*?)```', content, re.DOTALL)
                    for lang, code in code_matches:
                        code_snippets.append({
                            'language': lang or 'text',
                            'code': code.strip()[:1000],
                        })
                
                # Collect ALL callbacks (no limit)
                found_cbs = re.findall(r'case\s+\"([a-zA-Z_][a-zA-Z0-9_]*)\"', content)
                callbacks.update(found_cbs)
    
    return messages, code_snippets, list(callbacks)

def generate_html_ultrafast(messages, code_snippets, callbacks, output_file):
    """Generate small, fast-loading HTML"""
    
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
        .stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px; }}
        .stat-card {{ background: white; padding: 15px; border-radius: 10px; text-align: center; }}
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
        pre {{ background: #2d2d2d; color: #f8f8f2; padding: 12px; border-radius: 8px; overflow-x: auto; font-size: 12px; }}
        .callback-badge {{ display: inline-block; background: #667eea; color: white; padding: 5px 12px; margin: 5px; border-radius: 20px; font-size: 12px; }}
        .search-box {{ width: 100%; padding: 10px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 8px; }}
        .search-btn {{ background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; margin-left: 10px; }}
        .search-container {{ display: flex; margin-bottom: 15px; }}
        .highlight {{ background: #fff3cd !important; border-left: 4px solid #ff9800 !important; }}
        .timestamp {{ font-size: 11px; color: #888; }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🤖 DeepSeek Recovery Kit</h1>
        <p>{len(messages)} messages | {len(code_snippets)} code blocks | {len(callbacks)} callbacks</p>
    </div>
    
    <div class="stats">
        <div class="stat-card"><div class="stat-number">{len(messages)}</div><div>💬 Messages</div></div>
        <div class="stat-card"><div class="stat-number">{len(code_snippets)}</div><div>📝 Code</div></div>
        <div class="stat-card"><div class="stat-number">{len(callbacks)}</div><div>🔘 Callbacks</div></div>
    </div>
    
    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('messages')">💬 Messages</button>
        <button class="tab-btn" onclick="switchTab('code')">📝 Code ({len(code_snippets)})</button>
        <button class="tab-btn" onclick="switchTab('callbacks')">🔘 Callbacks ({len(callbacks)})</button>
    </div>
    
    <div id="messages-tab" class="tab-content active">
        <div class="search-container">
            <input type="text" class="search-box" id="searchInput" placeholder="🔍 Search messages..." onkeyup="filterMessages()">
            <button class="search-btn" onclick="searchNext()">⏩ Next Match</button>
        </div>
        <div id="messages-container">
'''
    
    for date in sorted(messages_by_date.keys(), reverse=True)[:30]:
        html += f'<div class="date-group"><div class="date-title">📅 {date}</div>'
        for msg in messages_by_date[date]:
            content = escape(msg['content']).replace('\n', '<br>')
            html += f'''
            <div class="message {msg['type']}" data-content="{escape(msg['content'][:300])}">
                <span class="timestamp">{msg['timestamp']}</span>
                <div>{content}</div>
            </div>
            '''
        html += '</div>'
    
    html += f'''
        </div>
    </div>
    
    <div id="code-tab" class="tab-content">
        {''.join(f'<strong>{s["language"].upper()}</strong><pre><code>{escape(s["code"])}</code></pre><hr>' for s in code_snippets[:100])}
        {f'<p>... and {len(code_snippets) - 100} more snippets</p>' if len(code_snippets) > 100 else ''}
    </div>
    
    <div id="callbacks-tab" class="tab-content">
        {''.join(f'<span class="callback-badge">{cb}</span>' for cb in sorted(callbacks))}
    </div>
</div>

<script>
    let searchResults = [];
    let currentIndex = 0;
    
    function switchTab(tabName) {{
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.getElementById(tabName + '-tab').classList.add('active');
        event.target.classList.add('active');
    }}
    
    function filterMessages() {{
        let search = document.getElementById('searchInput').value.toLowerCase();
        let messages = document.querySelectorAll('#messages-container .message');
        searchResults = [];
        
        messages.forEach((msg, idx) => {{
            let content = msg.getAttribute('data-content').toLowerCase();
            if (content.includes(search)) {{
                msg.style.display = 'block';
                searchResults.push(idx);
            }} else {{
                msg.style.display = 'none';
            }}
        }});
        
        currentIndex = 0;
        if (searchResults.length > 0) {{
            highlightMessage(searchResults[0]);
        }}
    }}
    
    function searchNext() {{
        if (searchResults.length === 0) {{
            alert('No matches found. Try a different search term.');
            return;
        }}
        currentIndex = (currentIndex + 1) % searchResults.length;
        highlightMessage(searchResults[currentIndex]);
    }}
    
    function highlightMessage(index) {{
        let messages = document.querySelectorAll('#messages-container .message');
        messages.forEach(m => m.classList.remove('highlight'));
        if (messages[index]) {{
            messages[index].classList.add('highlight');
            messages[index].scrollIntoView({{ behavior: 'smooth', block: 'center' }});
        }}
    }}
</script>
</body>
</html>'''
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    return len(messages), len(code_snippets), len(callbacks)

def main():
    parser = argparse.ArgumentParser(description='DeepSeek Recovery Kit - ULTRA FAST Version')
    parser.add_argument('json_file', help='Path to DeepSeek export JSON')
    parser.add_argument('-o', '--output', default='recovery_report.html', help='Output HTML file')
    parser.add_argument('-s', '--start-date', help='Start date (YYYY-MM-DD)')
    parser.add_argument('-e', '--end-date', help='End date (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    if not Path(args.json_file).exists():
        print(f"❌ File not found: {args.json_file}")
        sys.exit(1)
    
    # ⏱️ START TIMER
    start_time = datetime.now()
    print("=" * 50)
    print("🚀 DeepSeek Recovery Kit - ULTRA FAST CLI")
    print(f"⏱️ START TIME: {start_time.strftime('%H:%M:%S')}")
    print(f"📅 DATE: {start_time.strftime('%Y-%m-%d')}")
    print("=" * 50)
    
    start = datetime.strptime(args.start_date, '%Y-%m-%d').date() if args.start_date else None
    end = datetime.strptime(args.end_date, '%Y-%m-%d').date() if args.end_date else None
    
    print(f"\n📂 Loading: {args.json_file}")
    print("⚡ Processing (ULTRA FAST mode)...")
    
    # Extract data
    messages, codes, callbacks = extract_from_json_ultrafast(args.json_file, start, end)
    
    print(f"✅ Found: {len(messages)} messages, {len(codes)} code blocks, {len(callbacks)} callbacks")
    
    print("\n📝 Generating HTML...")
    msg_count, code_count, cb_count = generate_html_ultrafast(messages, codes, callbacks, args.output)
    
    # Check file size
    output_size = Path(args.output).stat().st_size / 1024
    
    # ⏱️ END TIMER
    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()
    
    print("\n" + "=" * 50)
    print("⏱️ TIMING SUMMARY")
    print("=" * 50)
    print(f"💬 Messages displayed: {msg_count}")
    print(f"📝 Code snippets: {code_count}")
    print(f"🔘 Callbacks found: {cb_count}")
    print(f"💾 Output size: {output_size:.1f} KB")
    print("-" * 50)
    print(f"⏱️ TOTAL TIME: {total_time:.2f} seconds")
    print(f"⏱️ START: {start_time.strftime('%H:%M:%S')}")
    print(f"⏱️ END:   {end_time.strftime('%H:%M:%S')}")
    print("=" * 50)
    print(f"\n✅ HTML saved: {args.output}")
    print("\n🎉 DONE! Open the HTML file in your browser.")
    print("UMPOUWAAH! 😎")

if __name__ == '__main__':
    main()
