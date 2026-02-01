#!/usr/bin/env python3
"""
Script to publish RELEASE-STRATEGY-GUIDE.md to Confluence.

Usage:
    1. Set environment variables in .env:
       CONFLUENCE_URL=https://yourcompany.atlassian.net/wiki
       CONFLUENCE_USERNAME=your-email@company.com
       CONFLUENCE_API_TOKEN=your-api-token
       CONFLUENCE_SPACE_KEY=YOUR_SPACE
       
    2. Run: python scripts/publish_to_confluence.py
"""

import os
import requests
from pathlib import Path
from dotenv import load_dotenv
import markdown
import re

load_dotenv()

# Configuration from environment
CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")
CONFLUENCE_USERNAME = os.getenv("CONFLUENCE_USERNAME")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
CONFLUENCE_SPACE_KEY = os.getenv("CONFLUENCE_SPACE_KEY")
PAGE_TITLE = "Release Strategy & CI/CD Best Practices Guide"


def convert_markdown_to_confluence(md_content: str) -> str:
    """Convert Markdown to Confluence storage format."""
    # Convert markdown to HTML
    html = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'toc']
    )
    
    # Wrap code blocks for Confluence
    html = re.sub(
        r'<pre><code class="language-(\w+)">(.*?)</code></pre>',
        r'<ac:structured-macro ac:name="code"><ac:parameter ac:name="language">\1</ac:parameter><ac:plain-text-body><![CDATA[\2]]></ac:plain-text-body></ac:structured-macro>',
        html,
        flags=re.DOTALL
    )
    
    # Handle mermaid diagrams - wrap in info panel with note
    html = re.sub(
        r'<pre><code class="language-mermaid">(.*?)</code></pre>',
        r'<ac:structured-macro ac:name="info"><ac:rich-text-body><p><strong>Mermaid Diagram:</strong> Install Mermaid plugin to render</p><ac:structured-macro ac:name="code"><ac:plain-text-body><![CDATA[\1]]></ac:plain-text-body></ac:structured-macro></ac:rich-text-body></ac:structured-macro>',
        html,
        flags=re.DOTALL
    )
    
    return html


def get_existing_page(title: str) -> dict | None:
    """Check if a page with this title already exists."""
    url = f"{CONFLUENCE_URL}/rest/api/content"
    params = {
        "title": title,
        "spaceKey": CONFLUENCE_SPACE_KEY,
        "expand": "version"
    }
    
    response = requests.get(
        url,
        params=params,
        auth=(CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN)
    )
    
    if response.status_code == 200:
        results = response.json().get("results", [])
        if results:
            return results[0]
    return None


def create_page(title: str, content: str) -> dict:
    """Create a new Confluence page."""
    url = f"{CONFLUENCE_URL}/rest/api/content"
    
    data = {
        "type": "page",
        "title": title,
        "space": {"key": CONFLUENCE_SPACE_KEY},
        "body": {
            "storage": {
                "value": content,
                "representation": "storage"
            }
        }
    }
    
    response = requests.post(
        url,
        json=data,
        auth=(CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN),
        headers={"Content-Type": "application/json"}
    )
    
    response.raise_for_status()
    return response.json()


def update_page(page_id: str, title: str, content: str, version: int) -> dict:
    """Update an existing Confluence page."""
    url = f"{CONFLUENCE_URL}/rest/api/content/{page_id}"
    
    data = {
        "type": "page",
        "title": title,
        "space": {"key": CONFLUENCE_SPACE_KEY},
        "body": {
            "storage": {
                "value": content,
                "representation": "storage"
            }
        },
        "version": {"number": version + 1}
    }
    
    response = requests.put(
        url,
        json=data,
        auth=(CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN),
        headers={"Content-Type": "application/json"}
    )
    
    response.raise_for_status()
    return response.json()


def main():
    # Validate configuration
    missing = []
    for var in ["CONFLUENCE_URL", "CONFLUENCE_USERNAME", "CONFLUENCE_API_TOKEN", "CONFLUENCE_SPACE_KEY"]:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print("❌ Missing environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\nAdd them to your .env file and try again.")
        return
    
    # Read the markdown file
    md_path = Path(__file__).parent.parent / "docs" / "RELEASE-STRATEGY-GUIDE.md"
    
    if not md_path.exists():
        print(f"❌ File not found: {md_path}")
        return
    
    print(f"📄 Reading: {md_path}")
    md_content = md_path.read_text()
    
    # Convert to Confluence format
    print("🔄 Converting Markdown to Confluence format...")
    confluence_content = convert_markdown_to_confluence(md_content)
    
    # Check if page exists
    print(f"🔍 Checking for existing page: '{PAGE_TITLE}'...")
    existing_page = get_existing_page(PAGE_TITLE)
    
    try:
        if existing_page:
            page_id = existing_page["id"]
            version = existing_page["version"]["number"]
            print(f"📝 Updating existing page (version {version})...")
            result = update_page(page_id, PAGE_TITLE, confluence_content, version)
            action = "updated"
        else:
            print("✨ Creating new page...")
            result = create_page(PAGE_TITLE, confluence_content)
            action = "created"
        
        page_url = f"{CONFLUENCE_URL}/spaces/{CONFLUENCE_SPACE_KEY}/pages/{result['id']}"
        print(f"\n✅ Page {action} successfully!")
        print(f"🔗 URL: {page_url}")
        
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ Error: {e}")
        print(f"Response: {e.response.text}")


if __name__ == "__main__":
    main()
