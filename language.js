(function(){
  const supported=['zh-CN','zh-TW','en','ja','ko','de','fr'];
  const labels={'zh-CN':'简体中文','zh-TW':'繁體中文',en:'English',ja:'日本語',ko:'한국어',de:'Deutsch',fr:'Français'};
  const locale={
    'zh-CN':{button:'打赏 USDT',title:'支持网站与 EA 开发',copy:'复制收款地址',copied:'已复制',note:'请务必选择 TRC-20 网络。转账前请仔细核对地址，区块链交易无法撤销。',close:'关闭'},
    'zh-TW':{button:'打賞 USDT',title:'支持網站與 EA 開發',copy:'複製收款地址',copied:'已複製',note:'請務必選擇 TRC-20 網路。轉帳前請仔細核對地址，區塊鏈交易無法撤銷。',close:'關閉'},
    en:{button:'Donate USDT',title:'Support the website and EA development',copy:'Copy wallet address',copied:'Copied',note:'Use the TRC-20 network only. Verify the address before sending; blockchain transfers cannot be reversed.',close:'Close'},
    ja:{button:'USDT寄付',title:'サイトとEA開発を支援',copy:'アドレスをコピー',copied:'コピーしました',note:'TRC-20ネットワークのみを使用し、送金前にアドレスを確認してください。',close:'閉じる'},
    ko:{button:'USDT 후원',title:'웹사이트와 EA 개발 후원',copy:'지갑 주소 복사',copied:'복사됨',note:'TRC-20 네트워크만 사용하세요. 전송 전에 주소를 확인하십시오. 블록체인 전송은 취소할 수 없습니다.',close:'닫기'},
    de:{button:'USDT spenden',title:'Website und EA-Entwicklung unterstützen',copy:'Wallet-Adresse kopieren',copied:'Kopiert',note:'Verwenden Sie ausschließlich das TRC-20-Netzwerk. Prüfen Sie die Adresse vor der Überweisung; Blockchain-Transaktionen sind nicht rückgängig zu machen.',close:'Schließen'},
    fr:{button:'Don USDT',title:'Soutenir le site et le développement des EA',copy:"Copier l’adresse",copied:'Copié',note:"Utilisez uniquement le réseau TRC-20. Vérifiez l’adresse avant l’envoi; les transactions blockchain sont irréversibles.",close:'Fermer'}
  };
  const path=location.pathname;
  const isFree=path.endsWith('/free-ea.html')||path==='/free-ea.html';
  function current(){
    const lang=(document.documentElement.lang||'').toLowerCase();
    if(lang.startsWith('zh-tw')||lang.startsWith('zh-hant'))return 'zh-TW';
    if(lang.startsWith('zh'))return 'zh-CN';
    if(lang.startsWith('ja'))return 'ja';
    if(lang.startsWith('ko'))return 'ko';
    if(lang.startsWith('de'))return 'de';
    if(lang.startsWith('fr'))return 'fr';
    return 'en';
  }
  function browserLanguage(){
    const lang=(navigator.languages&&navigator.languages[0]||navigator.language||'').toLowerCase();
    if(lang.startsWith('zh-tw')||lang.startsWith('zh-hk')||lang.startsWith('zh-mo')||lang.startsWith('zh-hant'))return 'zh-TW';
    if(lang.startsWith('zh'))return 'zh-CN';
    for(const code of ['ja','ko','de','fr'])if(lang.startsWith(code))return code;
    return 'en';
  }
  function target(code){
    const base={'zh-CN':'','zh-TW':'/zh-tw',en:'/en',ja:'/ja',ko:'/ko',de:'/de',fr:'/fr'}[code];
    return base+(isFree?'/free-ea.html':'/');
  }
  const active=current();
  if(!sessionStorage.getItem('languageChecked')&&!localStorage.getItem('siteLanguage')){
    sessionStorage.setItem('languageChecked','1');
    const detected=browserLanguage(),destination=target(detected);
    if(detected!==active){location.replace(destination);return;}
  }
  document.addEventListener('DOMContentLoaded',function(){
    const select=document.getElementById('siteLanguage');
    if(select){
      select.innerHTML=supported.map(code=>'<option value="'+target(code)+'" data-lang="'+code+'"'+(code===active?' selected':'')+'>'+labels[code]+'</option>').join('');
      select.onchange=function(){localStorage.setItem('siteLanguage',this.selectedOptions[0].dataset.lang);location.href=this.value;};
    }
    const text=locale[active]||locale.en;
    const open=document.getElementById('donateOpen'),dialog=document.getElementById('donateDialog'),copy=document.getElementById('donateCopy'),close=document.getElementById('donateClose');
    if(open)open.textContent=text.button;
    if(dialog){const title=dialog.querySelector('.donate-head h2'),note=dialog.querySelector('.donate-note');if(title)title.textContent=text.title;if(note)note.textContent=text.note;}
    if(copy){copy.textContent=text.copy;copy.addEventListener('click',function(){copy.textContent=text.copied;setTimeout(()=>copy.textContent=text.copy,1600);});}
    if(close)close.setAttribute('aria-label',text.close);
  });
})();
