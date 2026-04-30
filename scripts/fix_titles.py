import os
import re
from html import unescape

folder = "hugo-site/content/poemes"

for filename in os.listdir(folder):
    if not filename.endswith(".md"):
        continue
    filepath = os.path.join(folder, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    if "&#" in content or "&quot;" in content or "&amp;" in content:
        new_content = re.sub(
            r'title: "(.*?)"',
            lambda m: f'title: "{unescape(m.group(1)).replace(chr(34), chr(39))}"',
            content
        )
        if new_content != content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Corrige: {filename}")

print("Termine!")
