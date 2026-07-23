/**
 * XAU Quant · News & Signal Center
 * 加载 GitHub Actions 每 5 分钟更新的 JSON 数据,渲染到页面
 * 所有数据文件位于 /data/ 目录,由 .github/workflows/update.yml 自动更新
 */
(function () {
  'use strict';

  const DATA_BASE = '/data';
  const REFRESH_INTERVAL = 5 * 60 * 1000; // 5 分钟
  const COUNTDOWN_INTERVAL = 1000;

  // 沃什立场分析器(本地 fallback,无服务器依赖)
  const WARSH_KEYWORDS = {
    hawk: {
      'persistent': 2, 'elevated': 1, 'sticky': 2, 'above target': 2,
      'uncomfortable': 2, 'higher for longer': 3, 'vigilant': 1,
      'restrictive': 2, 'premature easing': 2, 'unwavering': 1,
      'credibility': 2, 'resolve': 1, 'commitment': 1,
      'price stability': 2, 'trimmed mean': 2, 'inflation remains': 2
    },
    dove: {
      'gradual': 1, 'patient': 1, 'data dependent': 1, 'flexible': 1,
      'moderating': 2, 'easing': 2, 'cuts': 2, 'accommodative': 1,
      'dovish': 2, 'transitory': 2, 'cooling': 1, 'softening': 1
    }
  };

  const FOMC_DATES = [
    { date: '2026-07-29T14:00:00-04:00', label: '2026-07-29' },
    { date: '2026-09-16T14:00:00-04:00', label: '2026-09-16' },
    { date: '2026-10-28T14:00:00-04:00', label: '2026-10-28' },
    { date: '2026-12-09T14:00:00-05:00', label: '2026-12-09' },
    { date: '2027-01-27T14:00:00-05:00', label: '2027-01-27' },
    { date: '2027-03-17T14:00:00-04:00', label: '2027-03-17' },
    { date: '2027-04-28T14:00:00-04:00', label: '2027-04-28' },
    { date: '2027-06-09T14:00:00-04:00', label: '2027-06-09' },
    { date: '2027-07-28T14:00:00-04:00', label: '2027-07-28' },
    { date: '2027-09-15T14:00:00-04:00', label: '2027-09-15' },
    { date: '2027-10-27T14:00:00-04:00', label: '2027-10-27' },
    { date: '2027-12-08T14:00:00-05:00', label: '2027-12-08' }
  ];

  function $(id) { return document.getElementById(id); }

  function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, character => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    })[character]);
  }

  function safeExternalUrl(value) {
    try {
      const url = new URL(String(value), window.location.origin);
      return ['http:', 'https:'].includes(url.protocol) ? url.href : '#';
    } catch {
      return '#';
    }
  }

  function formatTime(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    if (isNaN(d.getTime())) return '—';
    return d.toLocaleString('zh-CN', { hour12: false });
  }

  function relativeTime(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    if (isNaN(d.getTime())) return '—';
    const diff = Date.now() - d.getTime();
    const m = Math.floor(diff / 60000);
    if (m < 1) return '刚刚';
    if (m < 60) return `${m} 分钟前`;
    const h = Math.floor(m / 60);
    if (h < 24) return `${h} 小时前`;
    const day = Math.floor(h / 24);
    return `${day} 天前`;
  }

  function countdownTo(target) {
    const d = new Date(target);
    if (isNaN(d.getTime())) return { text: '—', date: '—' };
    const diff = d.getTime() - Date.now();
    if (diff <= 0) return { text: '00天 00:00:00', date: target };
    const days = Math.floor(diff / 86400000);
    const hours = Math.floor((diff % 86400000) / 3600000);
    const mins = Math.floor((diff % 3600000) / 60000);
    const seconds = Math.floor((diff % 60000) / 1000);
    return {
      text: `${days}天 ${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`,
      date: target
    };
  }

  function nextFomc() {
    const now = Date.now();
    return FOMC_DATES.find(f => new Date(f.date).getTime() > now) || null;
  }

  function renderPrice(d) {
    if (!d) return;
    if (d.price) $('xau-price').textContent = Number(d.price).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (d.change_pct != null) {
      const el = $('xau-delta');
      const v = Number(d.change_pct);
      el.textContent = `${v >= 0 ? '+' : ''}${v.toFixed(2)}%`;
      el.className = `delta ${v >= 0 ? 'up' : 'down'}`;
    }
  }

  function renderDxy(d) {
    if (!d) return;
    if (d.value) $('dxy-value').textContent = Number(d.value).toFixed(2);
    if (d.change_pct != null) {
      const el = $('dxy-delta');
      const v = Number(d.change_pct);
      el.textContent = `${v >= 0 ? '+' : ''}${v.toFixed(2)}%`;
      el.className = `delta ${v >= 0 ? 'up' : 'down'}`;
    }
  }

  function renderCountdown() {
    const next = nextFomc();
    if (!next) {
      $('fomc-countdown').textContent = '待公布';
      $('fomc-date').textContent = '等待美联储更新会议日程';
      return;
    }
    const c = countdownTo(next.date);
    $('fomc-countdown').textContent = c.text;
    $('fomc-date').textContent = `下次 FOMC 决议 · ${next.label} 14:00 ET`;
  }

  function analyzeWarshStance(text) {
    if (!text) return { hawk: 0, dove: 0, label: 'NEUTRAL', keywords: [] };
    const lower = text.toLowerCase();
    let hawk = 0, dove = 0;
    const keywords = [];

    for (const [kw, score] of Object.entries(WARSH_KEYWORDS.hawk)) {
      const re = new RegExp(kw.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
      const matches = lower.match(re);
      if (matches) {
        hawk += matches.length * score;
        keywords.push({ word: kw, type: 'hawk', count: matches.length });
      }
    }
    for (const [kw, score] of Object.entries(WARSH_KEYWORDS.dove)) {
      const re = new RegExp(kw.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
      const matches = lower.match(re);
      if (matches) {
        dove += matches.length * score;
        keywords.push({ word: kw, type: 'dove', count: matches.length });
      }
    }

    const diff = hawk - dove;
    let label = 'NEUTRAL';
    if (diff > 6) label = 'STRONG_HAWK';
    else if (diff > 2) label = 'HAWK';
    else if (diff < -6) label = 'STRONG_DOVE';
    else if (diff < -2) label = 'DOVE';

    return { hawk: hawk.toFixed(1), dove: dove.toFixed(1), label, keywords };
  }

  function renderWarsh(d) {
    if (!d) {
      $('stance-badge').textContent = '暂无数据';
      $('stance-badge').className = 'stance-badge neutral';
      $('stance-summary').textContent = '等待沃什最新公开发言...';
      return;
    }
    const a = d.stance || analyzeWarshStance(d.text || '');
    const badge = $('stance-badge');
    const labelMap = {
      'STRONG_HAWK': ['强鹰派', 'strong-hawk'],
      'HAWK': ['鹰派', 'hawk'],
      'NEUTRAL': ['中立', 'neutral'],
      'DOVE': ['鸽派', 'dove'],
      'STRONG_DOVE': ['强鸽派', 'strong-dove']
    };
    const [text, cls] = labelMap[a.label] || ['中立', 'neutral'];
    badge.textContent = text;
    badge.className = `stance-badge ${cls}`;

    $('hawk-score').textContent = a.hawk;
    $('dove-score').textContent = a.dove;
    const maxScore = Math.max(parseFloat(a.hawk), parseFloat(a.dove), 10);
    $('hawk-bar').style.width = `${Math.min(100, parseFloat(a.hawk) / maxScore * 100)}%`;
    $('dove-bar').style.width = `${Math.min(100, parseFloat(a.dove) / maxScore * 100)}%`;

    if (d.text) {
      $('stance-quote').style.display = 'block';
      $('stance-quote-text').textContent = `“${d.text.slice(0, 280)}${d.text.length > 280 ? '…' : ''}”`;
      $('stance-quote-source').textContent = `— ${d.source || '美联储'} · ${relativeTime(d.published_at)}`;
    }

    if (a.keywords && a.keywords.length) {
      const sorted = a.keywords.sort((x, y) => y.count - x.count).slice(0, 10);
      $('stance-keywords').innerHTML = sorted.map(k =>
        `<span class="kw ${k.type === 'dove' ? 'dove' : 'hawk'}">${escapeHtml(k.word)} ×${Number(k.count) || 0}</span>`
      ).join('');
    }

    $('stance-summary').textContent = d.summary || `基于最近一次发言的关键词权重分析`;
  }

  function renderFedwatch(d) {
    const panel = $('fedwatch-panel');
    if (!d || !d.meetings || d.meetings.length === 0) {
      panel.innerHTML = `<div class="empty-state"><strong>暂无 FedWatch 数据</strong>等待下次更新...</div>`;
      return;
    }
    panel.innerHTML = d.meetings.map(m => {
      const total = m.hold + m.hike + m.cut || 1;
      const holdPct = (m.hold / total * 100).toFixed(1);
      const hikePct = (m.hike / total * 100).toFixed(1);
      const cutPct = (m.cut / total * 100).toFixed(1);
      return `
        <div class="fedwatch-row">
          <div class="date">${escapeHtml(m.date || m.label || '—')}</div>
          <div class="fedwatch-bars">
            <div class="fedwatch-bar">
              <span class="label">维持</span>
              <div class="fedwatch-track hold"><span style="width: ${holdPct}%"></span></div>
              <span class="pct">${holdPct}%</span>
            </div>
            <div class="fedwatch-bar">
              <span class="label">加息 25bp</span>
              <div class="fedwatch-track hike"><span style="width: ${hikePct}%"></span></div>
              <span class="pct">${hikePct}%</span>
            </div>
            <div class="fedwatch-bar">
              <span class="label">降息 25bp</span>
              <div class="fedwatch-track cut"><span style="width: ${cutPct}%"></span></div>
              <span class="pct">${cutPct}%</span>
            </div>
          </div>
        </div>
      `;
    }).join('');
  }

  function renderNews(d) {
    const list = $('news-list');
    if (!d || !d.items || d.items.length === 0) {
      list.innerHTML = `<div class="empty-state"><strong>暂无新闻</strong>等待数据更新...</div>`;
      return;
    }
    list.innerHTML = d.items.slice(0, 30).map(item => {
      const source = String(item.source || 'unknown').toLowerCase();
      const sourceKey = ['fed', 'bls', 'treasury', 'cnbc', 'reuters', 'kitco'].find(s => source.includes(s)) || 'fed';
      const sourceLabels = { fed: 'FED', bls: 'BLS', treasury: 'TREASURY', cnbc: 'CNBC', reuters: 'REUTERS', kitco: 'KITCO' };
      return `
        <article class="news-item">
          <div class="meta">
            <span class="source-badge ${sourceKey}">${sourceLabels[sourceKey] || source.toUpperCase()}</span>
            <span>${escapeHtml(relativeTime(item.published_at))}</span>
          </div>
          <h3><a href="${safeExternalUrl(item.link)}" target="_blank" rel="noopener noreferrer">${escapeHtml(item.title || '—')}</a></h3>
          <p>${escapeHtml(item.summary || '')}</p>
        </article>
      `;
    }).join('');
  }

  function renderSignal(s) {
    $('signal-text').textContent = s ? s.signal : '震荡偏空 · 关注 4,000 支撑';
    $('signal-reason').textContent = s ? s.reason : '基于沃什鹰派立场 + 利率上行预期 + 美元走强,黄金短期承压。建议策略 A 做空端,1% 风险。';
  }

  async function fetchJson(path) {
    try {
      const r = await fetch(`${DATA_BASE}/${path}`, { cache: 'no-store' });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return await r.json();
    } catch (e) {
      console.warn(`[news] failed to load ${path}:`, e.message);
      return null;
    }
  }

  async function refresh() {
    $('last-updated').innerHTML = '刷新中<span class="loading-dot"></span><span class="loading-dot"></span><span class="loading-dot"></span>';

    const [price, dxy, warsh, fedwatch, news, signal] = await Promise.all([
      fetchJson('xauusd.json'),
      fetchJson('dxy.json'),
      fetchJson('warsh.json'),
      fetchJson('fedwatch.json'),
      fetchJson('news.json'),
      fetchJson('signal.json')
    ]);

    renderPrice(price);
    renderDxy(dxy);
    renderCountdown();
    renderWarsh(warsh);
    renderFedwatch(fedwatch);
    renderNews(news);
    renderSignal(signal);

    const now = new Date();
    $('last-updated').textContent = `最后更新: ${now.toLocaleString('zh-CN', { hour12: false })}`;
  }

  // 暴露给手动按钮
  window.newsApp = { refresh };

  document.addEventListener('DOMContentLoaded', () => {
    refresh();
    renderCountdown();
    setInterval(renderCountdown, COUNTDOWN_INTERVAL);
    setInterval(refresh, REFRESH_INTERVAL);
  });
})();
