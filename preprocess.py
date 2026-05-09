import re
import json
from striprtf.striprtf import rtf_to_text

# 讀取RTF
with open("criminal_law.rtf", "r", encoding="utf-8") as f:
    rtf_content = f.read()

text = rtf_to_text(rtf_content)

# 用「第 X 條」作為切分點
pattern = r"(第\s*\d+\s*條(?:-\d+)?)"
parts = re.split(pattern, text)

articles = []
for i in range(1, len(parts) - 1, 2):
    title = parts[i].strip()
    content = parts[i + 1].strip()

    if content:
        # 標準化條號格式
        article_num = re.sub(r"\s+", "", title)

        # 清理項次編號（如「1   」「2   」）
        content = re.sub(r"^\d+\s{2,}", "", content, flags=re.MULTILINE)

        full_text = f"{article_num}\n{content}"
        articles.append({
            "article": article_num,
            "content": content,
            "full_text": full_text
        })

# 存成JSON
with open("criminal_law.json", "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print(f"共切出 {len(articles)} 條法條，已存為 criminal_law.json")
print("---範例---")
for a in articles[:3]:
    print(a)
    print()