from striprtf.striprtf import rtf_to_text

with open("criminal_law.rtf", "r", encoding="utf-8") as f:
    rtf_content = f.read()

text = rtf_to_text(rtf_content)

# 只印出前500個字確認格式
print(text[:500])