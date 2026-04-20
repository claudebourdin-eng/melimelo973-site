#!/usr/bin/env python3
"""
import_blogger.py
Récupère tous les poèmes de melimelo973.blogspot.com
et génère les fichiers Markdown pour Hugo.
Détecte automatiquement les nouveaux articles pour n'importer que les nouveautés.
"""

import requests
import os
import re
import json
from datetime import datetime
from html import unescape
import html2text

# ─── CONFIGURATION ────────────────────────────────────────────────────────────
API_KEY    = "AIzaSyAlZcoFvzlr7KaMzyfL4L6vYEvMj2QQLyE"
BLOG_URL   = "https://melimelo973.blogspot.com"
OUTPUT_DIR = "hugo-site/content/poemes"
STATE_FILE = "scripts/imported_ids.json"   # Mémorise les articles déjà importés
# ──────────────────────────────────────────────────────────────────────────────

def load_imported_ids():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_imported_ids(ids):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(list(ids), f)

def get_blog_id():
    url = "https://www.googleapis.com/blogger/v3/blogs/byurl"
    r = requests.get(url, params={"url": BLOG_URL, "key": API_KEY})
    r.raise_for_status()
    data = r.json()
    print(f"✅ Blog : {data['name']} (ID: {data['id']})")
    return data["id"]

def get_all_posts(blog_id):
    posts, page = [], 1
    url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts"
    params = {"key": API_KEY, "maxResults": 500, "status": "live"}
    while True:
        print(f"  → Page {page}...")
        r = requests.get(url, params=params)
        r.raise_for_status()
        data = r.json()
        posts.extend(data.get("items", []))
        token = data.get("nextPageToken")
        if not token:
            break
        params["pageToken"] = token
        page += 1
    print(f"✅ {len(posts)} articles trouvés au total")
    return posts

def slugify(text):
    text = unescape(text).lower()
    for src, dst in [('àáâãäå','a'),('èéêë','e'),('ìíîï','i'),('òóôõö','o'),('ùúûü','u'),('ç','c'),('ñ','n')]:
        for c in src:
            text = text.replace(c, dst)
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-')

def html_to_markdown(html):
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.body_width = 0
    md = h.handle(html)
    return re.sub(r'\n{3,}', '\n\n', md).strip()

def post_to_markdown(post):
    title = unescape(post.get("title", "Sans titre"))
    slug  = slugify(title)
    published = post.get("published", "")
    try:
        dt       = datetime.fromisoformat(published.replace("Z", "+00:00"))
        date_str = dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        date_pfx = dt.strftime("%Y-%m-%d")
    except:
        date_str = published
        date_pfx = published[:10] if published else "0000-00-00"

    labels   = post.get("labels", [])
    tags_yml = "\n".join(f'  - "{l}"' for l in labels) or "  []"
    content  = html_to_markdown(post.get("content", ""))

    front = f"""---
title: "{title.replace('"', "'")}"
date: {date_str}
slug: "{slug}"
tags:
{tags_yml}
original_url: "{post.get('url', '')}"
draft: false
---

"""
    return slug, date_pfx, front + content

def save_post(slug, date_pfx, content):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    name = f"{date_pfx}-{slug}.md"
    path = os.path.join(OUTPUT_DIR, name)
    n = 1
    while os.path.exists(path):
        name = f"{date_pfx}-{slug}-{n}.md"
        path = os.path.join(OUTPUT_DIR, name)
        n += 1
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return name

def main():
    print("=" * 55)
    print("  Migration / Synchronisation Blogger → Hugo")
    print("=" * 55)

    imported_ids = load_imported_ids()
    print(f"\n📋 Articles déjà importés : {len(imported_ids)}")

    blog_id = get_blog_id()
    posts   = get_all_posts(blog_id)

    new_posts = [p for p in posts if p["id"] not in imported_ids]
    print(f"\n🆕 Nouveaux articles à importer : {len(new_posts)}")

    if not new_posts:
        print("\n✅ Rien de nouveau. Le site est déjà à jour !")
        return

    saved, errors = 0, 0
    for post in new_posts:
        try:
            slug, date_pfx, content = post_to_markdown(post)
            name = save_post(slug, date_pfx, content)
            imported_ids.add(post["id"])
            print(f"  ✅ {name}")
            saved += 1
        except Exception as e:
            print(f"  ❌ '{post.get('title','?')}' : {e}")
            errors += 1

    save_imported_ids(imported_ids)

    print(f"\n{'=' * 55}")
    print(f"  ✅ {saved} nouveaux poèmes importés")
    if errors:
        print(f"  ⚠️  {errors} erreurs")
    print(f"{'=' * 55}")

if __name__ == "__main__":
    main()
