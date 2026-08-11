#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查 data.js 中所有空数据项"""
import json
import re
from pathlib import Path

# 重新解析 markdown
exec(open("F:/Automation/国内遥感数据网站合集/parse_md.py", encoding="utf-8").read())

print("=" * 80)
print("空数据 / 无网址 / 无数据集 项审计")
print("=" * 80)

issues = []
for sec in sections:
    for it in sec["items"]:
        problems = []
        if not it.get("url"):
            problems.append("无网址")
        if not it.get("datasets") or len(it["datasets"]) == 0:
            problems.append("无数据集")
        else:
            # 检查数据集是否都是"空"（没有 name 也没有 url 也没 desc）
            empty_ds = 0
            for d in it["datasets"]:
                if not d.get("name") and not d.get("url") and (not d.get("desc") or len(d.get("desc", "")) < 5):
                    empty_ds += 1
            if empty_ds > 0:
                problems.append(f"{empty_ds}/{len(it['datasets'])} 数据集为空")
        if problems:
            issues.append((sec["key"], it["num"], it["title"], it.get("operator", ""), it.get("url", ""), len(it.get("datasets", [])), problems))

# 输出
print(f"\n总问题数: {len(issues)}\n")
for key, num, title, op, url, ds_count, probs in issues:
    print(f"[{key} #{num}] {title}")
    if op:
        print(f"  运营方: {op}")
    print(f"  网址: {url or '(空)'}")
    print(f"  数据集数: {ds_count}")
    print(f"  问题: {', '.join(probs)}")
    print()

# 按问题类型统计
no_url = sum(1 for i in issues if "无网址" in i[6])
no_ds = sum(1 for i in issues if "无数据集" in i[6])
empty_ds = sum(1 for i in issues if any("数据集为空" in p for p in i[6]))
print(f"\n无网址: {no_url} 项")
print(f"无数据集: {no_ds} 项")
print(f"数据集全空: {empty_ds} 项")

# 把有问题的项的"代表数据集"也打印出来
print("\n" + "=" * 80)
print("问题项的详细 datasets 内容")
print("=" * 80)
for sec in sections:
    for it in sec["items"]:
        if not it.get("datasets") or len(it["datasets"]) == 0:
            continue
        # 检查是否有空数据集
        has_empty = False
        for d in it["datasets"]:
            if not d.get("name") and not d.get("url") and (not d.get("desc") or len(d.get("desc", "")) < 5):
                has_empty = True
                break
        if has_empty:
            print(f"\n[{sec['key']} #{it['num']}] {it['title']}")
            print(f"  url: {it.get('url', '(空)')}")
            for d in it["datasets"]:
                print(f"  {d['idx']}. name={repr(d.get('name', ''))} desc={repr(d.get('desc', '')[:50])} url={d.get('url', '')}")
