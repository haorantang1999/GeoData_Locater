# GeoData Locater · 国内外遥感数据网站合集

> 📡 **166 个数据平台 · 1660 个代表数据集 · 13 个主题部分**

SCI 遥感论文常用的数据存储库、国内国家级数据中心、中科院各所与高校遥感团队、日本及其他国家官方数据、AI/ML 平台、商业卫星公司开放数据 —— 一站式覆盖遥感科研数据全谱系。

**🍎 苹果极简风网页** · GitHub Pages 静态部署 · 全静态、无后端

---

## 📂 文件结构

```
website/
├── index.html      # 主页面（单页应用）
├── style.css       # 苹果风样式（含暗色模式）
├── app.js          # 渲染 / 搜索 / 过滤 / 展开逻辑
├── data.js         # 166 平台 / 1650 数据集（从 markdown 自动生成）
├── .nojekyll       # 防止 GitHub Pages 用 Jekyll 编译
└── README.md       # 本文件
```

## 🚀 GitHub Pages 部署步骤

### 方式一：直接部署整个仓库（推荐）

1. **创建 GitHub 仓库**（如 `GeoData_Locater`）
2. **将 `website/` 目录内容 push 到仓库根目录**：
   ```bash
   cd website
   git init
   git add .
   git commit -m "Deploy GeoData Locater"
   git branch -M main
   git remote add origin https://github.com/haorantang1999/GeoData_Locater.git
   git push -u origin main
   ```
3. **GitHub 仓库 → Settings → Pages**：
   - Source: `Deploy from a branch`
   - Branch: `main` / `(root)`
4. 等待 1-2 分钟，访问 `https://haorantang1999.github.io/GeoData_Locater/`

### 方式二：主仓库是 markdown，单独部署 website/

如果主仓库保留 `国内外地理遥感数据网站合集.md`，但希望 GitHub Pages 部署 `website/`：

1. **push 主分支时**：
   ```bash
   git add 国内外地理遥感数据网站合集.md
   git commit -m "更新数据合集"
   git push
   ```
2. **Settings → Pages → Source**：
   - Branch: `main` / `website`  ← 选这个

这样 markdown 源文件在仓库根，`website/` 子目录部署为网页。

### 方式三：使用 GitHub Actions 自动部署

`.github/workflows/deploy.yml`：

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Pages
        uses: actions/configure-pages@v4
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: 'website'
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

---

## 🛠 维护与更新

### 1. 编辑 markdown 源文档

`../国内外地理遥感数据网站合集.md` 是源文件。

### 2. 重新生成 data.js

```bash
cd ..
python parse_md.py
```

会自动覆盖 `website/data.js`。

### 3. 重新部署

```bash
cd website
git add .
git commit -m "更新数据 $(date +%Y-%m-%d)"
git push
```

1-2 分钟后 GitHub Pages 自动更新。

---

## 🎨 网页功能

- **🔍 搜索**：支持按平台名 / 运营方 / 数据集 / 网址 全文搜索
- **🎯 过滤**：13 个主题部分可单独筛选
- **📂 展开**：每个平台默认折叠，点击 `+` 展开 10 个代表数据集
- **⌨️ 快捷键**：`⌘/Ctrl + K` 聚焦搜索框；`Esc` 重置
- **🌗 暗色模式**：跟随系统 `prefers-color-scheme`
- **📱 响应式**：桌面 / 平板 / 手机自适应

---

## 🛡 致谢与声明

- 整理人：**Mavis (Mavis Code Agent)**
- 数据更新：2026-08-08
- 引用建议：本文档为非正式整理版本，使用前请按"**网址 + DOI**"双重验证最新可用性

---

## 📊 数据规模一览

| 部分 | 平台 | 数据集 |
|---|---:|---:|
| 第一部分：SCI 论文高频使用的国际数据存储库 | 11 | 110 |
| 第二部分：国际官方卫星 / 遥感数据中心 | 10 | 100 |
| 第三部分：国内国家级科学数据中心 | 12 | 120 |
| 第四部分：国内专门遥感 / 卫星数据平台 | 10 | 100 |
| 第五部分：国内高校 / 科研机构专题遥感数据集 | 8 | 80 |
| 第六部分：日本官方遥感数据 | 8 | 80 |
| 第七部分：其他国家官方遥感数据 | 32 | 320 |
| 第八部分：SCI 论文配套数据存储库 | 14 | 140 |
| 第九部分：跨库检索 / 元数据聚合 | 8 | 80 |
| 第十部分：AI / ML 时代新平台 | 8 | 80 |
| 第十一部分：国内中科院各所 + 高校遥感团队专题 | 20 | 200 |
| 第十二部分：国内行业部门专题 | 10 | 100 |
| 第十三部分：商业卫星公司开放数据集 | 15 | 150 |
| **合计** | **166** | **1,660** |
