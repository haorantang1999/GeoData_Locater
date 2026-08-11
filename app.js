// ===== GeoData Locater 前端逻辑 =====

(function () {
  "use strict";

  // 状态
  const state = {
    data: window.SITE_DATA || { sections: [] },
    query: "",
    activeSection: null, // null = all
    expanded: new Set(),
  };

  // DOM
  const el = {
    sectionGrid: document.getElementById("section-grid"),
    siteList: document.getElementById("site-list"),
    empty: document.getElementById("empty"),
    searchInput: document.getElementById("search-input"),
    searchClear: document.getElementById("search-clear"),
    filterPills: document.getElementById("filter-pills"),
    resetBtn: document.getElementById("reset-btn"),
  };

  // ===== 工具函数 =====
  function escapeHtml(s) {
    if (s == null) return "";
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // 极简 markdown 内联渲染：先转义，再还原 **加粗** / *斜体* 与 <链接>
  function mdInline(s) {
    if (s == null) return "";
    return escapeHtml(s)
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/(^|[^*])\*([^*\n]+?)\*(?!\*)/g, "$1<em>$2</em>")
      .replace(
        /&lt;(https?:\/\/[^\s&]+)&gt;/g,
        '<a href="$1" target="_blank" rel="noopener">$1</a>'
      )
      .replace(/\n/g, "<br>");
  }

  function totalDatasets() {
    return state.data.sections.reduce(
      (sum, s) => sum + s.items.reduce((n, it) => n + it.datasets.length, 0),
      0
    );
  }

  function filterItems(items) {
    const q = state.query.trim().toLowerCase();
    if (!q) return items;
    return items.filter((it) => {
      const haystack = [
        it.title,
        it.url,
        it.operator,
        it.features,
        it.intro,
        it.landmark,
        ...(it.datasets || []).map((d) => `${d.name} ${d.desc}`),
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      return haystack.includes(q);
    });
  }

  // ===== 渲染分类网格 =====
  function renderSectionGrid() {
    const html = state.data.sections
      .map((s) => {
        const dsCount = s.items.reduce((n, it) => n + it.datasets.length, 0);
        return `
          <a class="sec-card" href="#${s.anchor}" data-section="${escapeHtml(s.key)}">
            <div class="sec-num">${escapeHtml(s.key)}</div>
            <div class="sec-title">${escapeHtml(s.title.replace(/^第[一二三四五六七八九十]+部分[：:]\s*/, ""))}</div>
            <div class="sec-meta">
              <span class="sec-count">${s.items.length} 平台</span>
              <span>· ${dsCount} 数据集</span>
            </div>
          </a>
        `;
      })
      .join("");
    el.sectionGrid.innerHTML = html;

    el.sectionGrid.addEventListener("click", (e) => {
      const card = e.target.closest(".sec-card");
      if (!card) return;
      e.preventDefault();
      const key = card.getAttribute("data-section");
      const sec = state.data.sections.find((s) => s.key === key);
      if (!sec) return;
      state.activeSection = key;
      renderFilterPills();
      renderSiteList();
      // 滚动到浏览区
      document.getElementById("explore").scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }

  // ===== 渲染过滤 pill =====
  function renderFilterPills() {
    const pills = [
      `<button class="pill${state.activeSection == null ? " active" : ""}" data-section="">全部 13 部分</button>`,
    ];
    state.data.sections.forEach((s) => {
      pills.push(
        `<button class="pill${state.activeSection === s.key ? " active" : ""}" data-section="${escapeHtml(s.key)}">${escapeHtml(s.key)} · ${s.items.length}</button>`
      );
    });
    el.filterPills.innerHTML = pills.join("");

    el.filterPills.addEventListener("click", (e) => {
      const btn = e.target.closest(".pill");
      if (!btn) return;
      const key = btn.getAttribute("data-section");
      state.activeSection = key || null;
      renderFilterPills();
      renderSiteList();
    });
  }

  // ===== 渲染平台列表 =====
  function renderSiteList() {
    let html = "";
    let totalMatches = 0;
    state.data.sections.forEach((sec) => {
      // 如果有 activeSection 过滤
      if (state.activeSection && state.activeSection !== sec.key) return;
      const items = filterItems(sec.items);
      if (items.length === 0 && state.query.trim()) return; // 有搜索时，无结果不展示
      if (items.length === 0 && !state.query.trim()) return;

      totalMatches += items.length;
      const dsCount = items.reduce((n, it) => n + it.datasets.length, 0);
      // 去掉 "第一部分：" 重复前缀
      const cleanTitle = sec.title.replace(/^第[一二三四五六七八九十]+部分[：:]\s*/, "");

      html += `<div class="sec-block" id="${sec.anchor}">`;
      html += `<h2 class="sec-block-title"><span class="sec-block-num">${escapeHtml(sec.key)}</span>${escapeHtml(cleanTitle)}</h2>`;
      html += `<p class="sec-block-meta">${items.length} 平台 · ${dsCount} 数据集</p>`;

      items.forEach((it) => {
        const expanded = state.expanded.has(it.anchor);
        html += renderSite(it, sec.key, expanded);
      });

      html += `</div>`;
    });

    if (totalMatches === 0) {
      el.siteList.innerHTML = "";
      el.empty.hidden = false;
    } else {
      el.siteList.innerHTML = html;
      el.empty.hidden = true;
      bindSiteEvents();
    }
  }

  function renderSite(it, secKey, expanded) {
    const block = (label, text, cls) =>
      text
        ? `<div class="site-features${cls ? " " + cls : ""}"><div class="site-features-label">${label}</div>${mdInline(text)}</div>`
        : "";

    const featuresHtml =
      block("简介", it.intro) +
      block("特点", it.features) +
      block("标志性数据集", it.landmark, "site-landmark");

    let dsHtml = "";
    if (it.datasets && it.datasets.length) {
      dsHtml = `<div class="site-ds-label">代表数据集 · ${it.datasets.length} 个</div>`;
      dsHtml += `<div class="ds-list">`;
      it.datasets.forEach((d) => {
        const name = d.name
          ? `<span class="ds-name">${escapeHtml(d.name)}</span>`
          : "";
        const desc = d.desc ? `<div class="ds-desc">${mdInline(d.desc)}</div>` : "";
        const link = d.url
          ? `<a class="ds-link" href="${escapeHtml(d.url)}" target="_blank" rel="noopener">${escapeHtml(d.url)}</a>`
          : "";
        dsHtml += `<div class="ds">
          <div class="ds-idx">${d.idx}</div>
          <div class="ds-content">${name}${desc}${link}</div>
        </div>`;
      });
      dsHtml += `</div>`;
    }

    let subHtml = "";
    if (it.sub_links && it.sub_links.length > 1) {
      subHtml = `<div class="sub-links"><div class="sub-links-label">相关链接</div>`;
      it.sub_links.forEach((sl) => {
        subHtml += `<div><span class="sub-link-label">${escapeHtml(sl.label || "↗")}</span><a class="sub-link" href="${escapeHtml(sl.url)}" target="_blank" rel="noopener">${escapeHtml(sl.url)}</a></div>`;
      });
      subHtml += `</div>`;
    }

    return `<div class="site${expanded ? " open" : ""}" data-anchor="${escapeHtml(it.anchor)}">
      <div class="site-head">
        <div class="site-num">${escapeHtml(it.num)}</div>
        <div class="site-meta">
          <div class="site-title">${escapeHtml(it.title)}</div>
          ${it.url ? `<a class="site-url" href="${escapeHtml(it.url)}" target="_blank" rel="noopener">${escapeHtml(it.url)}</a>` : ""}
          ${it.operator ? `<div class="site-operator">运营方：${escapeHtml(it.operator)}</div>` : ""}
          ${it.datasets && it.datasets.length ? `<div class="site-tags"><span class="site-tag">${it.datasets.length} 数据集</span></div>` : ""}
        </div>
        <button class="site-toggle" type="button" aria-label="展开">+</button>
      </div>
      <div class="site-body">
        ${featuresHtml}
        ${dsHtml}
        ${subHtml}
      </div>
    </div>`;
  }

  function bindSiteEvents() {
    el.siteList.querySelectorAll(".site-head").forEach((head) => {
      head.addEventListener("click", (e) => {
        if (e.target.tagName === "A") return; // 链接不触发
        const site = head.closest(".site");
        const anchor = site.getAttribute("data-anchor");
        if (state.expanded.has(anchor)) {
          state.expanded.delete(anchor);
          site.classList.remove("open");
        } else {
          state.expanded.add(anchor);
          site.classList.add("open");
        }
      });
    });
  }

  // ===== 搜索 =====
  function onSearchInput() {
    state.query = el.searchInput.value;
    el.searchClear.classList.toggle("visible", state.query.length > 0);
    renderSiteList();
  }

  function resetSearch() {
    state.query = "";
    state.activeSection = null;
    el.searchInput.value = "";
    el.searchClear.classList.remove("visible");
    renderFilterPills();
    renderSiteList();
  }

  // ===== 启动 =====
  function init() {
    if (!state.data.sections || state.data.sections.length === 0) {
      el.siteList.innerHTML = '<div class="loading">数据加载失败，请检查 data.js 是否正确加载。</div>';
      return;
    }

    renderSectionGrid();
    renderFilterPills();
    renderSiteList();

    el.searchInput.addEventListener("input", onSearchInput);
    el.searchClear.addEventListener("click", () => {
      el.searchInput.value = "";
      onSearchInput();
      el.searchInput.focus();
    });
    el.resetBtn.addEventListener("click", resetSearch);

    // 键盘 ⌘/Ctrl+K 聚焦搜索
    document.addEventListener("keydown", (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        el.searchInput.focus();
        el.searchInput.select();
      }
      if (e.key === "Escape" && document.activeElement === el.searchInput) {
        resetSearch();
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
