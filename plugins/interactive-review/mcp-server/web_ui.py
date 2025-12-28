"""
Web UI Generator for Interactive Review

Generates a self-contained HTML file with embedded CSS and JavaScript
for reviewing markdown content with checkboxes and comments.
"""

import re
import json
from typing import List, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class Block:
    """Represents a reviewable block in the markdown content."""
    id: str
    type: str  # heading, list-item, paragraph, code
    text: str
    level: int = 0  # for headings
    raw: str = ""  # original markdown


def parse_markdown(content: str) -> List[Block]:
    """
    Parse markdown content into reviewable blocks.
    Each heading, list item, and paragraph becomes a separate block.
    """
    blocks = []
    lines = content.split('\n')
    block_id = 0

    i = 0
    while i < len(lines):
        line = lines[i]

        # Skip empty lines
        if not line.strip():
            i += 1
            continue

        # Heading
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2).strip()
            blocks.append(Block(
                id=f"block-{block_id}",
                type="heading",
                text=text,
                level=level,
                raw=line
            ))
            block_id += 1
            i += 1
            continue

        # List item (- or * or numbered)
        list_match = re.match(r'^(\s*)[-*]\s+(.+)$', line) or re.match(r'^(\s*)\d+\.\s+(.+)$', line)
        if list_match:
            text = list_match.group(2).strip()
            blocks.append(Block(
                id=f"block-{block_id}",
                type="list-item",
                text=text,
                raw=line
            ))
            block_id += 1
            i += 1
            continue

        # Code block
        if line.strip().startswith('```'):
            code_lines = [line]
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            if i < len(lines):
                code_lines.append(lines[i])
                i += 1

            raw = '\n'.join(code_lines)
            # Extract language and code content
            lang_match = re.match(r'^```(\w*)$', code_lines[0].strip())
            lang = lang_match.group(1) if lang_match else ''
            code_content = '\n'.join(code_lines[1:-1]) if len(code_lines) > 2 else ''

            blocks.append(Block(
                id=f"block-{block_id}",
                type="code",
                text=f"[Code: {lang}]" if lang else "[Code block]",
                raw=raw
            ))
            block_id += 1
            continue

        # Regular paragraph
        para_lines = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith('#') and not re.match(r'^[-*]\s', lines[i]) and not re.match(r'^\d+\.\s', lines[i]) and not lines[i].strip().startswith('```'):
            para_lines.append(lines[i])
            i += 1

        text = ' '.join(para_lines).strip()
        if text:
            blocks.append(Block(
                id=f"block-{block_id}",
                type="paragraph",
                text=text,
                raw='\n'.join(para_lines)
            ))
            block_id += 1

    return blocks


def generate_html(title: str, content: str, blocks: List[Block], server_port: int) -> str:
    """Generate the complete HTML for the review UI."""

    blocks_json = json.dumps([asdict(b) for b in blocks])

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Interactive Review</title>
    <style>
        :root {{
            --bg-primary: #1a1a2e;
            --bg-secondary: #16213e;
            --bg-card: #1f2847;
            --text-primary: #eaeaea;
            --text-secondary: #a0a0a0;
            --accent: #4f9cf9;
            --accent-hover: #3b8bef;
            --success: #4ade80;
            --danger: #f87171;
            --border: #2d3a5a;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
        }}

        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border);
        }}

        h1 {{
            font-size: 1.5rem;
            font-weight: 600;
        }}

        .summary {{
            font-size: 0.875rem;
            color: var(--text-secondary);
        }}

        .summary .approved {{
            color: var(--success);
        }}

        .summary .rejected {{
            color: var(--danger);
        }}

        .block {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            margin-bottom: 1rem;
            overflow: hidden;
            transition: border-color 0.2s;
        }}

        .block:hover {{
            border-color: var(--accent);
        }}

        .block.rejected {{
            border-left: 3px solid var(--danger);
        }}

        .block.approved {{
            border-left: 3px solid var(--success);
        }}

        .block-header {{
            display: flex;
            align-items: flex-start;
            gap: 1rem;
            padding: 1rem;
            cursor: pointer;
        }}

        .checkbox-wrapper {{
            flex-shrink: 0;
            padding-top: 2px;
        }}

        input[type="checkbox"] {{
            width: 20px;
            height: 20px;
            cursor: pointer;
            accent-color: var(--success);
        }}

        .block-content {{
            flex: 1;
        }}

        .block-type {{
            font-size: 0.7rem;
            text-transform: uppercase;
            color: var(--text-secondary);
            margin-bottom: 0.25rem;
        }}

        .block-text {{
            font-size: 0.95rem;
        }}

        .block-text.heading {{
            font-weight: 600;
            font-size: 1.1rem;
        }}

        .block-text.code {{
            font-family: 'SF Mono', Monaco, monospace;
            font-size: 0.85rem;
            color: var(--accent);
        }}

        .comment-section {{
            padding: 0 1rem 1rem 3.25rem;
        }}

        .comment-input {{
            width: 100%;
            padding: 0.75rem;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text-primary);
            font-size: 0.875rem;
            resize: vertical;
            min-height: 60px;
        }}

        .comment-input:focus {{
            outline: none;
            border-color: var(--accent);
        }}

        .comment-input::placeholder {{
            color: var(--text-secondary);
        }}

        .actions {{
            display: flex;
            gap: 1rem;
            justify-content: space-between;
            align-items: center;
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border);
        }}

        .action-group {{
            display: flex;
            gap: 0.5rem;
        }}

        button {{
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 6px;
            font-size: 0.875rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .btn-secondary {{
            background: var(--bg-secondary);
            color: var(--text-primary);
            border: 1px solid var(--border);
        }}

        .btn-secondary:hover {{
            background: var(--border);
        }}

        .btn-success {{
            background: var(--success);
            color: #000;
        }}

        .btn-success:hover {{
            opacity: 0.9;
        }}

        .btn-danger {{
            background: transparent;
            color: var(--danger);
            border: 1px solid var(--danger);
        }}

        .btn-danger:hover {{
            background: var(--danger);
            color: #000;
        }}

        .btn-primary {{
            background: var(--accent);
            color: #fff;
        }}

        .btn-primary:hover {{
            background: var(--accent-hover);
        }}

        .keyboard-hint {{
            font-size: 0.75rem;
            color: var(--text-secondary);
        }}

        kbd {{
            background: var(--bg-secondary);
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-family: inherit;
            border: 1px solid var(--border);
        }}

        .raw-content {{
            display: none;
            background: var(--bg-secondary);
            padding: 0.75rem;
            margin: 0.5rem 1rem 1rem 3.25rem;
            border-radius: 6px;
            font-family: 'SF Mono', Monaco, monospace;
            font-size: 0.8rem;
            white-space: pre-wrap;
            color: var(--text-secondary);
        }}

        .block:hover .raw-content {{
            display: block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{title}</h1>
            <div class="summary">
                <span class="approved" id="approved-count">0</span> approved |
                <span class="rejected" id="rejected-count">0</span> needs revision
            </div>
        </header>

        <main id="blocks-container">
            <!-- Blocks will be rendered here -->
        </main>

        <div class="actions">
            <div class="action-group">
                <button class="btn-success" onclick="approveAll()">Approve All</button>
                <button class="btn-danger" onclick="rejectAll()">Reject All</button>
            </div>
            <div class="keyboard-hint">
                <kbd>Cmd</kbd>+<kbd>Enter</kbd> to submit | <kbd>Esc</kbd> to cancel
            </div>
            <div class="action-group">
                <button class="btn-secondary" onclick="cancelReview()">Cancel</button>
                <button class="btn-primary" onclick="submitReview()">Submit Review</button>
            </div>
        </div>
    </div>

    <script>
        const blocks = {blocks_json};
        const serverPort = {server_port};

        // Initialize blocks with checked=true by default
        const reviewState = blocks.map(block => ({{
            ...block,
            checked: true,
            comment: ''
        }}));

        function renderBlocks() {{
            const container = document.getElementById('blocks-container');
            container.innerHTML = reviewState.map((block, index) => `
                <div class="block ${{block.checked ? 'approved' : 'rejected'}}" data-index="${{index}}">
                    <div class="block-header" onclick="toggleCheck(${{index}})">
                        <div class="checkbox-wrapper">
                            <input type="checkbox"
                                   ${{block.checked ? 'checked' : ''}}
                                   onclick="event.stopPropagation(); toggleCheck(${{index}})"
                                   id="check-${{index}}">
                        </div>
                        <div class="block-content">
                            <div class="block-type">${{block.type}}${{block.level ? ' h' + block.level : ''}}</div>
                            <div class="block-text ${{block.type}}">${{escapeHtml(block.text)}}</div>
                        </div>
                    </div>
                    ${{block.raw !== block.text ? `<div class="raw-content">${{escapeHtml(block.raw)}}</div>` : ''}}
                    <div class="comment-section">
                        <textarea class="comment-input"
                                  placeholder="Add a comment (optional)..."
                                  data-index="${{index}}"
                                  oninput="updateComment(${{index}}, this.value)">${{block.comment}}</textarea>
                    </div>
                </div>
            `).join('');

            updateSummary();
        }}

        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}

        function toggleCheck(index) {{
            reviewState[index].checked = !reviewState[index].checked;
            renderBlocks();
        }}

        function updateComment(index, value) {{
            reviewState[index].comment = value;
        }}

        function updateSummary() {{
            const approved = reviewState.filter(b => b.checked).length;
            const rejected = reviewState.length - approved;
            document.getElementById('approved-count').textContent = approved;
            document.getElementById('rejected-count').textContent = rejected;
        }}

        function approveAll() {{
            reviewState.forEach(block => block.checked = true);
            renderBlocks();
        }}

        function rejectAll() {{
            reviewState.forEach(block => block.checked = false);
            renderBlocks();
        }}

        async function submitReview() {{
            const result = {{
                status: 'submitted',
                timestamp: new Date().toISOString(),
                items: reviewState.map(block => ({{
                    id: block.id,
                    text: block.text,
                    checked: block.checked,
                    comment: block.comment
                }}))
            }};

            try {{
                await fetch(`http://localhost:${{serverPort}}/submit`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(result)
                }});
                window.close();
            }} catch (e) {{
                alert('Failed to submit review. Please try again.');
                console.error(e);
            }}
        }}

        async function cancelReview() {{
            try {{
                await fetch(`http://localhost:${{serverPort}}/submit`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ status: 'cancelled', items: [] }})
                }});
                window.close();
            }} catch (e) {{
                window.close();
            }}
        }}

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {{
            if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {{
                e.preventDefault();
                submitReview();
            }}
            if (e.key === 'Escape') {{
                cancelReview();
            }}
        }});

        // Initial render
        renderBlocks();
    </script>
</body>
</html>'''
