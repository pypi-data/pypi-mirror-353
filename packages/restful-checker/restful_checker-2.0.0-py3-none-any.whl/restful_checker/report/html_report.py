from datetime import datetime
from pathlib import Path
import importlib.resources

def render_ordered_section(messages):
    html = ""
    errors = [m for m in messages if m.startswith("❌")]
    warnings = [m for m in messages if m.startswith("⚠️")]
    others = [m for m in messages if not m.startswith(("❌", "⚠️"))]
    for m in errors + warnings + others:
        html += f"<li>{m}</li>"
    html += "</ul>"
    return html

def generate_html(report, score, output=None):
    if output is None:
        output = Path(__file__).parent.parent / "html" / "rest_report.html"

    if score < 30:
        level = "Very Low"
        color = "#c0392b"
    elif score < 50:
        level = "Low"
        color = "#e74c3c"
    elif score < 70:
        level = "Medium"
        color = "#f39c12"
    elif score < 80:
        level = "Good"
        color = "#f1c40f"
    elif score < 95:
        level = "Very Good"
        color = "#2ecc71"
    else:
        level = "Excellent"
        color = "#27ae60"

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        inline_css = importlib.resources.read_text("restful_checker.data", "style.css")
    except (FileNotFoundError, ModuleNotFoundError):
        inline_css = "/* Failed to load CSS */"

    html = f"""<html><head>
    <meta charset='utf-8'>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RESTful API Report</title>
    <style>{inline_css}</style>
</head><body>
    <div class="container">
        <h1>RESTful API Report</h1>
        <p><strong>Generated:</strong> {now}</p>
        <div class='section'><div class='score' style='background:{color}'>{score}% - {level}</div></div>
"""

    for block in report:
        block_items = block['items']
        block_score = block.get("score", 1.0)
        emoji = "🟢"
        level_class = "section-ok"

        block_score = block.get("score", 1.0)

        if block_score < 0.5:
            level_class = "section-error"
            emoji = "🔴"
        elif block_score < 0.7:
            level_class = "section-warn"
            emoji = "🟡"
        else:
            level_class = "section-ok"
            emoji = "🟢"

        score_tag = f" <span class='score-inline'>({round(block_score * 100)}%)</span>"

        html += f"<div class='section {level_class}'><h2>{emoji}&nbsp;{block['title']}{score_tag}</h2>"

        section_messages = []

        for item in block_items:
            if item.startswith("### "):
                if section_messages:
                    html += render_ordered_section(section_messages)
                    section_messages = []
                current_section = item[4:]
                html += f"<h3>{current_section}</h3><ul>"
            else:
                section_messages.append(item)

        if section_messages:
            html += render_ordered_section(section_messages)

        html += "</div>"

    html += "</div></body></html>"
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(html, encoding='utf-8')
    return str(output)