(function () {
  'use strict';
  const language = document.documentElement.lang.toLowerCase();
  const copies = {
    'zh-cn': ['黄金市场智能简报', '置信度', '打开完整新闻与信号中心', '偏多', '偏空', '中性'],
    'zh-tw': ['黃金市場智能簡報', '信心度', '開啟完整新聞與訊號中心', '偏多', '偏空', '中性'],
    en: ['Gold Market Intelligence Brief', 'Confidence', 'Open full News & Signal Center', 'Bullish', 'Bearish', 'Neutral'],
    ja: ['金市場インテリジェンス', '信頼度', 'ニュース・シグナルセンターを開く', '強気', '弱気', '中立'],
    ko: ['금 시장 인텔리전스 브리핑', '신뢰도', '뉴스 및 신호 센터 열기', '강세', '약세', '중립'],
    de: ['Goldmarkt-Intelligence', 'Konfidenz', 'News- und Signalzentrum öffnen', 'Positiv', 'Negativ', 'Neutral'],
    fr: ['Brief intelligent du marché de l’or', 'Confiance', 'Ouvrir le centre actualités et signaux', 'Haussier', 'Baissier', 'Neutre']
  };
  const values = copies[language] || copies.en;
  const copy = { kicker: 'AI MARKET BRIEF', title: values[0], confidence: values[1], open: values[2], bullish: values[3], bearish: values[4], neutral: values[5] };

  function label(direction) {
    return copy[direction] || copy.neutral;
  }

  async function render() {
    const anchor = document.getElementById('features');
    if (!anchor) return;
    try {
      const response = await fetch('/data/brief.json', { cache: 'no-store' });
      if (!response.ok) return;
      const brief = await response.json();
      const section = document.createElement('section');
      section.className = 'intel-shell';
      section.innerHTML = `<div class="intel-card">
        <div class="intel-kicker">${copy.kicker}</div>
        <h2 class="intel-title">${copy.title}</h2>
        <div class="intel-grid">
          <div><span class="intel-tag ${brief.direction}">${label(brief.direction)}</span>
          <div class="intel-tags">${(brief.drivers || []).map(item => `<span class="intel-tag">${String(item).toUpperCase()}</span>`).join('')}</div></div>
          <div><div class="intel-score">${Number(brief.score || 0) > 0 ? '+' : ''}${Number(brief.score || 0)}</div>
          <div class="intel-meta">${copy.confidence} ${Number(brief.confidence || 0)}%</div></div>
        </div>
        <p style="margin:18px 0 0"><a href="${language === 'zh-cn' ? '/news.html' : `/${language}/news.html`}" style="color:#f3d58a">${copy.open} →</a></p>
      </div>`;
      anchor.parentNode.insertBefore(section, anchor);
    } catch (_) {
      return;
    }
  }

  document.addEventListener('DOMContentLoaded', render);
})();
