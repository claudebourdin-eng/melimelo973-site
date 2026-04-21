import requests
import os
import re
import json
from datetime import datetime
from html import unescape
import html2text

API_KEY    = "AIzaSyAlZcoFvzlr7KaMzyfL4L6vYEvMj2QQLyE"
BLOG_URL   = "https://melimelo973.blogspot.com"
OUTPUT_DIR = "hugo-site/content/poemes"
STATE_FILE = "scripts/imported_ids.json"

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
    print(f"OK Blog : {data['name']} (ID: {data['id']})")
    return data["id"]

def get_all_posts(blog_id):
    posts, page = [], 1
    url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts"
    params = {"key": API_KEY, "maxResults": 500, "status": "live"}
    while True:
        print(f"  -> Page {page}...")
        r = requests.get(url, params=params)
        r.raise_for_status()
        data = r.json()
        posts.extend(data.get("items", []))
        token = data.get("nextPageToken")
        if not token:
            break
        params["pageToken"] = token
        page += 1
    print(f"OK {len(posts)} articles trouves au total")
    return posts

def clean_title(title):
    title = unescape(title)
    title = title.replace("'", "'").replace('"', '"').replace('"', '"')
    title = title.strip("'\" ")
    return title

def normalize_title(title):
    title = clean_title(title).lower().strip()
    title = re.sub(r"['\"\u2018\u2019\u201c\u201d]", "", title)
    title = re.sub(r'\s+', ' ', title)
    return title

def slugify(text):
    text = clean_title(text).lower()
    for src, dst in [('aàáâãäå','a'),('eèéêë','e'),('iìíîï','i'),('oòóôõö','o'),('uùúûü','u'),('ç','c'),('ñ','n')]:
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
    title = clean_title(post.get("title", "Sans titre"))
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
    safe_title = title.replace('"', "'")
    front = f"""---
title: "{safe_title}"
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
    print("  Synchronisation Blogger -> Hugo")
    print("=" * 55)
    imported_ids = load_imported_ids()
    print(f"\nArticles deja importes : {len(imported_ids)}")
    blog_id = get_blog_id()
    posts   = get_all_posts(blog_id)
    seen_titles = set()
    new_posts = []
    for p in posts:
        if p["id"] not in imported_ids:
            norm = normalize_title(p.get("title", ""))
            if norm not in seen_titles:
                seen_titles.add(norm)
                new_posts.append(p)
    print(f"\nNouveaux articles a importer : {len(new_posts)}")
    if not new_posts:
        print("\nOK Rien de nouveau. Le site est deja a jour !")
        return
    saved, errors = 0, 0
    for post in new_posts:
        try:
            slug, date_pfx, content = post_to_markdown(post)
            name = save_post(slug, date_pfx, content)
            imported_ids.add(post["id"])
            print(f"  OK {name}")
            saved += 1
        except Exception as e:
            print(f"  ERREUR '{post.get('title','?')}' : {e}")
            errors += 1
    save_imported_ids(imported_ids)
    print(f"\n{'=' * 55}")
    print(f"  OK {saved} nouveaux poemes importes")
    if errors:
        print(f"  ERREURS : {errors}")
    print(f"{'=' * 55}")

if __name__ == "__main__":
    main()
