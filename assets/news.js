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
  const REQUESTED_LANGUAGE = new URLSearchParams(window.location.search).get('newsLang');
  const PAGE_LANGUAGE = (REQUESTED_LANGUAGE || document.documentElement.lang).toLowerCase();
  const IS_ENGLISH = PAGE_LANGUAGE.startsWith('en');
  const TRANSLATION_LANGUAGE = {
    'zh-cn': 'zh-CN',
    'zh-tw': 'zh-TW',
    en: 'en',
    ja: 'ja',
    ko: 'ko',
    de: 'de',
    fr: 'fr'
  }[PAGE_LANGUAGE] || 'en';
  const TIME_LABELS = {
    'zh-CN': ['实时 UTC 时间', '实时北京时间 (UTC+8)', '参考汇率日期', '行情数据更新'],
    'zh-TW': ['即時 UTC 時間', '即時北京時間 (UTC+8)', '參考匯率日期', '行情資料更新'],
    en: ['Live UTC time', 'Live Beijing time (UTC+8)', 'Reference-rate date', 'Market data updated'],
    ja: ['リアルタイム UTC', 'リアルタイム北京時間 (UTC+8)', '参照レート日', '市場データ更新'],
    ko: ['실시간 UTC', '실시간 베이징 시간 (UTC+8)', '기준 환율 날짜', '시장 데이터 업데이트'],
    de: ['UTC-Echtzeit', 'Peking-Echtzeit (UTC+8)', 'Referenzkursdatum', 'Marktdaten aktualisiert'],
    fr: ['Heure UTC en direct', 'Heure de Pékin en direct (UTC+8)', 'Date du taux de référence', 'Données de marché actualisées']
  };
  const STANCE_UI = {
    'zh-CN': { empty: '暂无数据', waiting: '等待沃什最新公开发言…', summary: '基于最近一次发言的关键词权重分析', fed: '美联储', labels: ['强鹰派', '鹰派', '中立', '鸽派', '强鸽派'] },
    'zh-TW': { empty: '暫無資料', waiting: '等待沃什最新公開發言…', summary: '根據最近一次發言進行關鍵詞權重分析', fed: '聯準會', labels: ['強鷹派', '鷹派', '中立', '鴿派', '強鴿派'] },
    en: { empty: 'No data', waiting: 'Waiting for Warsh’s latest public remarks…', summary: 'Keyword-weight analysis of the latest remarks', fed: 'Federal Reserve', labels: ['Strong hawk', 'Hawkish', 'Neutral', 'Dovish', 'Strong dove'] },
    ja: { empty: 'データなし', waiting: 'ウォーシュ議長の最新発言を待っています…', summary: '最新発言のキーワード加重分析', fed: '連邦準備制度', labels: ['強いタカ派', 'タカ派', '中立', 'ハト派', '強いハト派'] },
    ko: { empty: '데이터 없음', waiting: '워시 의장의 최신 공개 발언을 기다리는 중…', summary: '최근 발언의 키워드 가중치 분석', fed: '연방준비제도', labels: ['강한 매파', '매파', '중립', '비둘기파', '강한 비둘기파'] },
    de: { empty: 'Keine Daten', waiting: 'Warte auf Warshs jüngste öffentliche Äußerung…', summary: 'Schlüsselwortanalyse der jüngsten Äußerung', fed: 'Federal Reserve', labels: ['Stark restriktiv', 'Restriktiv', 'Neutral', 'Expansiv', 'Stark expansiv'] },
    fr: { empty: 'Aucune donnée', waiting: 'En attente de la dernière déclaration publique de Warsh…', summary: 'Analyse pondérée des mots-clés de la dernière déclaration', fed: 'Réserve fédérale', labels: ['Très restrictif', 'Restrictif', 'Neutre', 'Accommodant', 'Très accommodant'] }
  };

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

  function formatZonedTime(date, timeZone) {
    return new Intl.DateTimeFormat('sv-SE', {
      timeZone,
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    }).format(date);
  }

  function renderDataTime(elementId, iso, referenceDate) {
    const element = $(elementId);
    if (!element) return;
    const fetchedAt = new Date(iso);
    const hasFetchedAt = iso && !Number.isNaN(fetchedAt.getTime());
    const labels = TIME_LABELS[TRANSLATION_LANGUAGE] || TIME_LABELS.en;
    const updated = hasFetchedAt
      ? formatZonedTime(fetchedAt, 'UTC')
      : (IS_ENGLISH ? 'Unavailable' : '暂不可用');
    const reference = referenceDate
      ? `<div class="data-time-row"><span>${labels[2]}</span><time>${escapeHtml(referenceDate)}</time></div>`
      : '';
    element.innerHTML = `
      <div class="data-time-row is-live"><span>${labels[0]}</span><time class="live-utc">—</time></div>
      <div class="data-time-row is-live"><span>${labels[1]}</span><time class="live-beijing">—</time></div>
      <div class="data-time-row"><span>${labels[3]} (UTC)</span><time>${escapeHtml(updated)}</time></div>
      ${reference}
    `;
    updateMarketClocks();
  }

  function updateMarketClocks() {
    const now = new Date();
    const utc = formatZonedTime(now, 'UTC');
    const beijing = formatZonedTime(now, 'Asia/Shanghai');
    document.querySelectorAll('.live-utc').forEach(element => {
      element.textContent = utc;
    });
    document.querySelectorAll('.live-beijing').forEach(element => {
      element.textContent = beijing;
    });
  }

  function relativeTime(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    if (isNaN(d.getTime())) return '—';
    const diff = Date.now() - d.getTime();
    const m = Math.floor(diff / 60000);
    const formatter = new Intl.RelativeTimeFormat(TRANSLATION_LANGUAGE, { numeric: 'auto' });
    if (m < 1) return formatter.format(0, 'minute');
    if (m < 60) return formatter.format(-m, 'minute');
    const h = Math.floor(m / 60);
    if (h < 24) return formatter.format(-h, 'hour');
    const day = Math.floor(h / 24);
    return formatter.format(-day, 'day');
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
    renderDataTime('xau-time', d.fetched_at);
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
    renderDataTime('dxy-time', d.fetched_at, d.source_date);
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
    const ui = STANCE_UI[TRANSLATION_LANGUAGE] || STANCE_UI.en;
    if (!d) {
      $('stance-badge').textContent = ui.empty;
      $('stance-badge').className = 'stance-badge neutral';
      $('stance-summary').textContent = ui.waiting;
      return;
    }
    const a = d.stance || analyzeWarshStance(d.text || '');
    const badge = $('stance-badge');
    const labelMap = {
      'STRONG_HAWK': [ui.labels[0], 'strong-hawk'],
      'HAWK': [ui.labels[1], 'hawk'],
      'NEUTRAL': [ui.labels[2], 'neutral'],
      'DOVE': [ui.labels[3], 'dove'],
      'STRONG_DOVE': [ui.labels[4], 'strong-dove']
    };
    const [text, cls] = labelMap[a.label] || [ui.labels[2], 'neutral'];
    badge.textContent = text;
    badge.className = `stance-badge ${cls}`;

    $('hawk-score').textContent = a.hawk;
    $('dove-score').textContent = a.dove;
    const maxScore = Math.max(parseFloat(a.hawk), parseFloat(a.dove), 10);
    $('hawk-bar').style.width = `${Math.min(100, parseFloat(a.hawk) / maxScore * 100)}%`;
    $('dove-bar').style.width = `${Math.min(100, parseFloat(a.dove) / maxScore * 100)}%`;

    if (d.text) {
      const source = String(d.source || '').includes('Federal Reserve') ? ui.fed : (d.source || ui.fed);
      const pretranslated = d.translations?.[TRANSLATION_LANGUAGE];
      const excerpt = TRANSLATION_LANGUAGE !== 'en' && typeof pretranslated?.excerpt === 'string'
        ? pretranslated.excerpt
        : d.text.slice(0, 280);
      $('stance-quote').style.display = 'block';
      $('stance-quote-text').textContent = `“${excerpt}${d.text.length > 280 ? '…' : ''}”`;
      $('stance-quote-source').textContent = `— ${source} · ${relativeTime(d.published_at)}`;
    }

    let sorted = [];
    if (a.keywords && a.keywords.length) {
      sorted = [...a.keywords].sort((x, y) => y.count - x.count).slice(0, 10);
      const translatedKeywords = d.translations?.[TRANSLATION_LANGUAGE]?.keywords;
      $('stance-keywords').innerHTML = sorted.map((keyword, index) =>
        `<span class="kw ${keyword.type === 'dove' ? 'dove' : 'hawk'}">${escapeHtml(translatedKeywords?.[index] || keyword.word)} ×${Number(keyword.count) || 0}</span>`
      ).join('');
    }

    $('stance-summary').textContent = d.summary || ui.summary;
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

  function newsMarkup(items) {
    return items.map((item, index) => {
      const source = String(item.source || 'unknown').toLowerCase();
      const sourceKey = ['treasury', 'census', 'white_house', 'ecb', 'fed', 'bls', 'bea']
        .find(s => source.includes(s)) || 'official';
      const sourceLabels = {
        treasury: 'TREASURY',
        census: 'CENSUS',
        white_house: 'WHITE HOUSE',
        ecb: 'ECB',
        fed: 'FED',
        bls: 'BLS',
        bea: 'BEA',
        official: 'OFFICIAL'
      };
      return `
        <article class="news-item" data-news-index="${index}">
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

  function localizedNewsItems(items) {
    if (TRANSLATION_LANGUAGE === 'en') return items;
    return items.map(item => {
      const translation = item.translations?.[TRANSLATION_LANGUAGE];
      if (!translation) return item;
      return {
        ...item,
        title: translation.title || item.title,
        summary: translation.summary || item.summary
      };
    });
  }

  function renderNews(d) {
    const list = $('news-list');
    if (!d || !d.items || d.items.length === 0) {
      list.innerHTML = `<div class="empty-state"><strong>暂无新闻</strong>等待数据更新...</div>`;
      return;
    }
    const items = localizedNewsItems(d.items);
    list.innerHTML = newsMarkup(items);
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
    const languageSelect = $('siteLanguage');
    const activeOption = languageSelect?.querySelector(`[data-lang="${TRANSLATION_LANGUAGE}"]`);
    if (activeOption instanceof HTMLOptionElement) {
      languageSelect.value = activeOption.value;
    }
    refresh();
    renderCountdown();
    setInterval(renderCountdown, COUNTDOWN_INTERVAL);
    setInterval(updateMarketClocks, COUNTDOWN_INTERVAL);
    setInterval(refresh, REFRESH_INTERVAL);
  });
})();
