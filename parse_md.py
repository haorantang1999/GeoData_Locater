#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 国内外地理遥感数据网站合集.md 解析为 JSON 数据，供网页使用。
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
MD_PATH = BASE / "国内外地理遥感数据网站合集.md"
OUT_PATH = BASE / "data.js"

# 读取 markdown
text = MD_PATH.read_text(encoding="utf-8")
lines = text.splitlines()


def slugify(s: str) -> str:
    """生成 anchor id 友好的 slug。"""
    s = s.strip()
    s = re.sub(r"[^\w\u4e00-\u9fff\-]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


# 收集所有二级标题（## 第N部分：...）和三级标题（### N. 标题）
sections = []  # {title, anchor, items: [{num, title, anchor, content}]}
current_section = None

# 提取范围：从第一个 ### N. 开始到附录 G 之前
start = False
data_lines = []

for i, line in enumerate(lines):
    # 跳过附录 G（最新动态）和收尾
    if "## 附录 G：2025-2026 最新动态" in line:
        break
    if "## 附录 F" in line:
        data_lines = lines[:i]
        break

lines = data_lines

# 章节标题映射
SECTION_TITLES = {
    "第一部分": "SCI 论文高频使用的国际数据存储库",
    "第二部分": "国际官方卫星 / 遥感数据中心",
    "第三部分": "国内国家级科学数据中心",
    "第四部分": "国内专门遥感 / 卫星数据平台",
    "第五部分": "国内高校 / 科研机构专题遥感数据集",
    "第六部分": "日本官方遥感数据",
    "第七部分": "其他国家官方遥感数据",
    "第八部分": "SCI 论文配套数据存储库（按出版商 / 期刊 / 平台）",
    "第九部分": "跨库检索 / 元数据聚合",
    "第十部分": "AI / ML 时代新平台",
    "第十一部分": "国内中科院各所 + 高校遥感团队专题",
    "第十二部分": "国内行业部门专题",
    "第十三部分": "商业卫星公司开放数据集",
}

# 解析
sections = []  # [{key, title, anchor, items: [...]}]
items = []  # 当前 section 的 items

current_section = None
current_item = None  # 正在解析的 website/平台

def flush_item():
    global current_item
    if current_item and current_item.get("title"):
        # 解析 urls (从 - **网址**：xxx 或 - 多个链接)
        items.append(current_item)
    current_item = None


i = 0
N = len(lines)
while i < N:
    line = lines[i]
    stripped = line.strip()

    # 匹配 ## 第N部分：...
    m = re.match(r"^##\s*(第[一二三四五六七八九十]+部分)[：:]\s*(.*)$", stripped)
    if m:
        flush_item()
        if current_section:
            current_section["items"] = items
            sections.append(current_section)
        key, title = m.group(1), m.group(2).strip()
        current_section = {
            "key": key,
            "title": f"{key}：{title}",
            "anchor": f"section-{key}",
            "items": []
        }
        items = []
        i += 1
        continue

    # 匹配 ### N. 标题 或 ### N.N. 标题 或 ### 数字.
    m = re.match(r"^###\s*(\d+(?:\.\d+)?)\.?\s+(.*)$", stripped)
    if m:
        flush_item()
        num = m.group(1)
        title = m.group(2).strip()
        current_item = {
            "num": num,
            "title": title,
            "anchor": f"item-{num}",
            "url": "",
            "operator": "",
            "intro": "",
            "features": "",
            "landmark": "",
            "datasets": [],
            "sub_links": []  # 多 URL 时的额外链接
        }
        i += 1
        continue

    # 匹配 ### 6.5 之类或带 . 的特殊编号（如 6.5）
    m = re.match(r"^###\s*(\d+\.\d+)\s+.*—\s*(.*)$", stripped)
    if m:
        flush_item()
        num = m.group(1)
        title = m.group(2).strip()
        current_item = {
            "num": num,
            "title": title,
            "anchor": f"item-{num.replace('.', '-')}",
            "url": "",
            "operator": "",
            "intro": "",
            "features": "",
            "landmark": "",
            "datasets": [],
            "sub_links": []
        }
        i += 1
        continue

    # 匹配 - **网址**：... 或 - **数据入口**：...
    if current_item and re.match(r"^-\s*\*\*网址\*\*[：:]", stripped):
        # 解析本行 + 接下来几行的子链接
        all_lines = [stripped]
        j = i + 1
        while j < N and re.match(r"^\s+-\s+", lines[j]):
            all_lines.append(lines[j].strip())
            j += 1
        full_text = " ".join(all_lines)
        # 提取主 URL（第一个）
        m = re.search(r"<(https?://[^>]+)>", full_text)
        if m:
            current_item["url"] = m.group(1)
        # 提取所有链接作为 sub_links（带标签）
        for sm in re.finditer(r"([^:：]+?)[：:]\s*<(https?://[^>]+)>", full_text):
            current_item["sub_links"].append({"url": sm.group(2), "label": sm.group(1).strip()})
        if not current_item["sub_links"]:
            for sm in re.finditer(r"<(https?://[^>]+)>", full_text):
                current_item["sub_links"].append({"url": sm.group(1), "label": ""})
        i = j  # 跳过已处理的子链接行
        continue

    # 匹配 - **运营方**：...
    if current_item and re.match(r"^-\s*\*\*运营方?\*\*[：:]", stripped):
        m = re.search(r"\*\*运营方?\*\*[：:]\s*(.+?)$", stripped)
        if m:
            current_item["operator"] = m.group(1).strip()

    # 匹配 - **特点**：...
    if current_item and re.match(r"^-\s*\*\*特点\*\*[：:]", stripped):
        m = re.search(r"\*\*特点\*\*[：:]\s*(.+?)$", stripped)
        if m:
            current_item["features"] = m.group(1).strip()

    # 匹配 - **标志性数据集**：...
    if current_item and re.match(r"^-\s*\*\*标志性数据集\*\*[：:]", stripped):
        m = re.search(r"\*\*标志性数据集\*\*[：:]\s*(.+?)$", stripped)
        if m:
            current_item["landmark"] = m.group(1).strip()
        i += 1
        continue

    # 匹配 - **DOI 注册入口**：... 等其他 - 键值对
    if current_item and re.match(r"^-\s*\*\*[^*]+\*\*[：:]", stripped) and not any(
        re.match(r"^-\s*\*\*(网址|运营方|特点|标志性数据集)\*\*", stripped)
        for _ in [0]
    ):
        m = re.match(r"^-\s*\*\*([^*]+)\*\*[：:]\s*(.+?)$", stripped)
        if m and current_item.get("intro") == "":
            current_item["intro"] = f"{m.group(1).strip()}：{m.group(2).strip()}"

    # 匹配 - **...**（无冒号，作为描述）
    if current_item and re.match(r"^-\s*\*\*[^*]+\*\*\s*$", stripped) is None and \
       current_item and re.match(r"^-\s*\*\*[^*]+\*\*\s*", stripped) and \
       "网址" not in stripped and "运营方" not in stripped and "特点" not in stripped:
        pass  # 不重复处理

    # 匹配 **10 个代表性数据集**：开始
    if re.match(r"^\*\*\d+\s*个代表性", stripped):
        i += 1
        # 跳过空行
        while i < N and lines[i].strip() == "":
            i += 1
        # 解析接下来的 1. xxx 2. xxx 列表
        while i < N:
            ln = lines[i].strip()
            if ln == "":
                i += 1
                continue
            m = re.match(r"^(\d+)\.\s+\*\*(.+?)\*\*\s*[——\-:]?\s*(.*)$", ln)
            if m:
                idx = m.group(1)
                name = m.group(2).strip()
                desc = m.group(3).strip()
                ds_url = ""
                mu = re.search(r"<(https?://[^>]+)>", desc)
                if mu:
                    ds_url = mu.group(1)
                current_item["datasets"].append({
                    "idx": int(idx),
                    "name": name,
                    "desc": desc,
                    "url": ds_url
                })
                i += 1
            elif re.match(r"^\d+\.\s+", ln):
                # 没有 **...** 加粗
                m2 = re.match(r"^(\d+)\.\s+(.+?)$", ln)
                if m2:
                    idx = m2.group(1)
                    desc = m2.group(2).strip()
                    ds_url = ""
                    mu = re.search(r"<(https?://[^>]+)>", desc)
                    if mu:
                        ds_url = mu.group(1)
                    current_item["datasets"].append({
                        "idx": int(idx),
                        "name": "",
                        "desc": desc,
                        "url": ds_url
                    })
                i += 1
            else:
                break
        continue

    i += 1

# 收尾
flush_item()
if current_section:
    current_section["items"] = items
    sections.append(current_section)

# 写出
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
js_content = "// 自动生成于 parse_md.py - 国内外遥感数据网站合集\n"
_sites = sum(len(s["items"]) for s in sections)
_ds = sum(len(it["datasets"]) for s in sections for it in s["items"])
js_content += "window.SITE_DATA = " + json.dumps({
    "title": "国内外地理遥感数据网站合集",
    "subtitle": f"{_sites} 个平台 · {_ds} 个数据集 · {len(sections)} 个主题部分",
    "sections": sections
}, ensure_ascii=False, indent=2) + ";\n"
OUT_PATH.write_text(js_content, encoding="utf-8")

# 统计
total_sites = sum(len(s["items"]) for s in sections)
total_datasets = sum(len(it["datasets"]) for s in sections for it in s["items"])
print(f"解析完成：{len(sections)} 个部分，{total_sites} 个网站，{total_datasets} 个数据集")
for s in sections:
    print(f"  {s['key']}：{s['title']} - {len(s['items'])} 个网站")
