(function () {
  'use strict';

  const language = document.documentElement.lang.toLowerCase();
  const locale = {
    'zh-cn': {
      title: '黄金市场智能简报', confidence: '置信度', score: '综合评分',
      events: '经济事件雷达', support: '主要驱动', counter: '反向因素',
      open: '查看完整新闻与信号中心', empty: '暂无未来事件',
      signals: ['强势偏多', '震荡偏多', '多空均衡', '震荡偏空', '强势偏空'],
      factors: ['沃什立场', '利率路径', '黄金动量', '美元指数'],
      eventNames: ['FOMC 利率决议', '美国消费者物价指数 CPI', '美国非农就业报告', '美国生产者物价指数 PPI', '美国 JOLTS 职位空缺', '美国就业成本指数']
    },
    'zh-tw': {
      title: '黃金市場智能簡報', confidence: '信心度', score: '綜合評分',
      events: '經濟事件雷達', support: '主要驅動', counter: '反向因素',
      open: '查看完整新聞與訊號中心', empty: '暫無未來事件',
      signals: ['強勢偏多', '震盪偏多', '多空均衡', '震盪偏空', '強勢偏空'],
      factors: ['沃什立場', '利率路徑', '黃金動量', '美元指數'],
      eventNames: ['FOMC 利率決議', '美國消費者物價指數 CPI', '美國非農就業報告', '美國生產者物價指數 PPI', '美國 JOLTS 職位空缺', '美國就業成本指數']
    },
    en: {
      title: 'Gold Market Intelligence Brief', confidence: 'Confidence', score: 'Composite score',
      events: 'Economic Event Radar', support: 'Key drivers', counter: 'Counter factors',
      open: 'Open full News & Signal Center', empty: 'No upcoming events',
      signals: ['Strong bullish', 'Mild bullish', 'Balanced', 'Mild bearish', 'Strong bearish'],
      factors: ['Warsh stance', 'Rate path', 'Gold momentum', 'Dollar index'],
      eventNames: ['FOMC Rate Decision', 'U.S. Consumer Price Index', 'U.S. Employment Report', 'U.S. Producer Price Index', 'U.S. JOLTS Job Openings', 'U.S. Employment Cost Index']
    },
    ja: {
      title: '金市場インテリジェンス', confidence: '信頼度', score: '総合スコア',
      events: '経済イベントレーダー', support: '主な要因', counter: '反対要因',
      open: 'ニュース・シグナルセンターを開く', empty: '予定なし',
      signals: ['強い強気', 'やや強気', '均衡', 'やや弱気', '強い弱気'],
      factors: ['ウォーシュ姿勢', '金利経路', '金モメンタム', 'ドル指数'],
      eventNames: ['FOMC 金利決定', '米国 CPI', '米国雇用統計', '米国 PPI', '米国 JOLTS 求人', '米国雇用コスト指数']
    },
    ko: {
      title: '금 시장 인텔리전스 브리핑', confidence: '신뢰도', score: '종합 점수',
      events: '경제 이벤트 레이더', support: '주요 동인', counter: '반대 요인',
      open: '뉴스 및 신호 센터 열기', empty: '예정된 이벤트 없음',
      signals: ['강한 강세', '완만한 강세', '균형', '완만한 약세', '강한 약세'],
      factors: ['워시 입장', '금리 경로', '금 모멘텀', '달러 지수'],
      eventNames: ['FOMC 금리 결정', '미국 CPI', '미국 고용보고서', '미국 PPI', '미국 JOLTS 구인', '미국 고용비용지수']
    },
    de: {
      title: 'Goldmarkt-Intelligence', confidence: 'Konfidenz', score: 'Gesamtwert',
      events: 'Wirtschaftstermin-Radar', support: 'Haupttreiber', counter: 'Gegenfaktoren',
      open: 'News- und Signalzentrum öffnen', empty: 'Keine Termine',
      signals: ['Stark positiv', 'Leicht positiv', 'Ausgeglichen', 'Leicht negativ', 'Stark negativ'],
      factors: ['Warsh-Position', 'Zinspfad', 'Goldmomentum', 'Dollarindex'],
      eventNames: ['FOMC-Zinsentscheid', 'US-Verbraucherpreisindex', 'US-Arbeitsmarktbericht', 'US-Erzeugerpreisindex', 'US-JOLTS-Stellenangebote', 'US-Beschäftigungskostenindex']
    },
    fr: {
      title: 'Brief intelligent du marché de l’or', confidence: 'Confiance', score: 'Score global',
      events: 'Radar des événements économiques', support: 'Facteurs moteurs', counter: 'Facteurs contraires',
      open: 'Ouvrir le centre actualités et signaux', empty: 'Aucun événement à venir',
      signals: ['Fortement haussier', 'Modérément haussier', 'Équilibré', 'Modérément baissier', 'Fortement baissier'],
      factors: ['Position de Warsh', 'Trajectoire des taux', 'Momentum de l’or', 'Indice dollar'],
      eventNames: ['Décision de taux du FOMC', 'IPC américain', 'Rapport sur l’emploi américain', 'IPP américain', 'Offres d’emploi JOLTS', 'Indice du coût de l’emploi']
    }
  }[language] || null;

  const copy = locale || {
    title: 'Gold Market Intelligence Brief', confidence: 'Confidence', score: 'Composite score',
    events: 'Economic Event Radar', support: 'Key drivers', counter: 'Counter factors',
    open: 'Open full News & Signal Center', empty: 'No upcoming events',
    signals: ['Strong bullish', 'Mild bullish', 'Balanced', 'Mild bearish', 'Strong bearish'],
    factors: ['Warsh stance', 'Rate path', 'Gold momentum', 'Dollar index'],
    eventNames: ['FOMC Rate Decision', 'U.S. Consumer Price Index', 'U.S. Employment Report', 'U.S. Producer Price Index', 'U.S. JOLTS Job Openings', 'U.S. Employment Cost Index']
  };
  const factorKeys = ['warsh', 'fedwatch', 'xau', 'dxy'];
  const eventKeys = ['fomc', 'cpi', 'nfp', 'ppi', 'jolts', 'eci'];
  const signalKeys = ['strong_bullish', 'mild_bullish', 'balanced', 'mild_bearish', 'strong_bearish'];

  function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, character => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    })[character]);
  }

  function newsUrl() {
    return language === 'zh-cn' ? '/news.html' : `/${language}/news.html`;
  }

  function signalLabel(key) {
    const index = signalKeys.indexOf(key);
    return index >= 0 ? copy.signals[index] : copy.signals[2];
  }

  function factorLabel(key) {
    const index = factorKeys.indexOf(key);
    return index >= 0 ? copy.factors[index] : String(key).toUpperCase();
  }

  function eventLabel(event) {
    const index = eventKeys.indexOf(event.event_key);
    return index >= 0 ? copy.eventNames[index] : event.title;
  }

  function formatTime(iso) {
    const date = new Date(iso);
    return Number.isNaN(date.getTime()) ? '—' : date.toLocaleString(language, { hour12: false });
  }

  function countdown(iso) {
    const difference = new Date(iso).getTime() - Date.now();
    if (!Number.isFinite(difference) || difference <= 0) return '00:00';
    const hours = Math.floor(difference / 3600000);
    const minutes = Math.floor((difference % 3600000) / 60000);
    return `${hours}h ${minutes}m`;
  }

  function chips(items, direction) {
    return (items || []).map(item =>
      `<span class="brief-chip ${escapeHtml(direction)}">${escapeHtml(factorLabel(item))}</span>`
    ).join('');
  }

  function briefMarkup(brief) {
    const score = Number(brief.score || 0);
    const confidence = Math.max(0, Math.min(100, Number(brief.confidence || 0)));
    const opposite = brief.direction === 'bullish' ? 'bearish' : 'bullish';
    const evidence = [
      { title: copy.support, items: brief.drivers, direction: brief.direction },
      { title: copy.counter, items: brief.counter_risks, direction: opposite }
    ].filter(group => Array.isArray(group.items) && group.items.length);
    return `<div class="brief-top"><div><div class="intel-kicker">${escapeHtml(copy.score)}</div>
      <div class="brief-direction">${escapeHtml(signalLabel(brief.label_key))}</div></div>
      <div class="intel-score">${score > 0 ? '+' : ''}${score}</div></div>
      <div class="confidence-head"><span>${escapeHtml(copy.confidence)}</span><strong>${confidence}%</strong></div>
      <div class="confidence-track"><span style="width:${confidence}%"></span></div>
      <div class="brief-evidence ${evidence.length === 1 ? 'single' : ''}">${evidence.map(group =>
        `<div><span class="evidence-label">${escapeHtml(group.title)}</span><div class="brief-chips">${chips(group.items, group.direction)}</div></div>`
      ).join('')}</div>`;
  }

  function eventsMarkup(data) {
    const events = Array.isArray(data?.events) ? data.events.slice(0, 3) : [];
    if (!events.length) return `<div class="intel-muted">${escapeHtml(copy.empty)}</div>`;
    return events.map(event => `<div class="event-row">
      <div class="event-meta"><span class="event-source">${escapeHtml(event.event_key === 'fomc' ? 'FOMC' : event.source)}</span>
      <span class="event-countdown" data-event-time="${escapeHtml(event.starts_at)}">${countdown(event.starts_at)}</span></div>
      <strong>${escapeHtml(eventLabel(event))}</strong>
      <time class="intel-muted">${escapeHtml(formatTime(event.starts_at))}</time>
    </div>`).join('');
  }

  async function fetchJson(name) {
    const response = await fetch(`/data/${name}`, { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async function render() {
    const anchor = document.getElementById('features');
    if (!anchor) return;
    try {
      const [brief, events] = await Promise.all([fetchJson('brief.json'), fetchJson('events.json')]);
      const section = document.createElement('section');
      section.className = 'intel-shell';
      section.innerHTML = `<div class="intel-kicker">INTELLIGENCE</div><h2 class="intel-title">${escapeHtml(copy.title)}</h2>
        <div class="intel-grid"><div class="intel-card">${briefMarkup(brief)}</div>
        <div class="intel-card"><div class="intel-kicker">CALENDAR</div><h3>${escapeHtml(copy.events)}</h3>
        <div class="event-list">${eventsMarkup(events)}</div></div></div>
        <a class="intel-open" href="${escapeHtml(newsUrl())}">${escapeHtml(copy.open)} →</a>`;
      anchor.parentNode.insertBefore(section, anchor);
      setInterval(() => document.querySelectorAll('[data-event-time]').forEach(element => {
        element.textContent = countdown(element.dataset.eventTime);
      }), 60000);
    } catch (_) {
      return;
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', render);
  } else {
    render();
  }
})();
