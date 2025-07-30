import re
from markdown_it import MarkdownIt

def render_markdown_to_html(md_text: str) -> str:
    """
    Render Markdown text to prompt_toolkit-compatible HTML,
    mapping strong->b, em->i, li->bullet.
    """
    md = MarkdownIt()
    html = md.render(md_text)
    # Convert links to underlined text with URL in parentheses
    html = re.sub(r'<a href="([^"]+)">([^<]+)</a>', r'<u>\2</u> (\1)', html)
    # Map tags to prompt_toolkit HTML
    html = html.replace('<strong>', '<b>').replace('</strong>', '</b>')
    html = html.replace('<em>', '<i>').replace('</em>', '</i>')
    html = html.replace('<ul>', '').replace('</ul>', '')
    html = html.replace('<li>', '• ').replace('</li>', '\n')
    html = html.replace('<p>', '').replace('</p>', '\n\n')
    return html.strip() 