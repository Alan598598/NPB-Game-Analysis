'use strict';
(function () {
  const target = document.getElementById('games');
  const count = document.getElementById('count');
  const el = (tag, className, text) => {
    const n = document.createElement(tag);
    if (className) n.className = className;
    if (text !== undefined) n.textContent = text;
    return n;
  };
  function localized(parent, value) {
    const re = /[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9,.'’%:+\-/ ]*/g;
    let i=0, m;
    while ((m = re.exec(value)) !== null) {
      if (m.index > i) parent.append(document.createTextNode(value.slice(i,m.index)));
      const s=el('span','number-run',m[0]);s.lang='en';parent.append(s);i=re.lastIndex;
    }
    if (i<value.length) parent.append(document.createTextNode(value.slice(i)));
  }
  async function init() {
    try {
      const response = await fetch('data/games.json', {cache:'no-store'});
      if (!response.ok) throw new Error('HTTP '+response.status);
      const data = await response.json();
      if (data.schema_version !== 1 || !Array.isArray(data.games)) throw new Error('賽事資料格式不符');
      target.replaceChildren();
      count.textContent = `${data.games.length} 場賽事`;
      for (const game of data.games) {
        const card = el('a','game-card');card.href=game.slides_path;
        card.setAttribute('aria-label',`${game.date} ${game.away_team} ${game.away_score} 比 ${game.home_score} ${game.home_team}，開啟簡報`);
        const head = el('div','game-header');
        const meta = el('div');meta.append(el('div','game-date',game.date),el('div','game-competition',game.competition));
        const arrow = el('span','game-arrow','↗');arrow.setAttribute('aria-hidden','true');head.append(meta,arrow);
        const mid = el('div','game-match');const teams=el('div','game-teams');
        const away=el('div');localized(away,game.away_team);const home=el('div');localized(home,game.home_team);teams.append(away,home);
        const score=el('div','game-score');score.append(el('span','',String(game.away_score)),el('span','colon','–'),el('span','',String(game.home_score)));mid.append(teams,score);
        const foot=el('div','game-footer','查看完整互動式賽後分析簡報');card.append(head,mid,foot);target.append(card);
      }
      if (!data.games.length) target.append(el('p','loading-message','目前還沒有已發布的簡報。'));
    } catch (error) {
      target.replaceChildren(el('p','error-message','賽事索引無法載入。請以本機 HTTP 伺服器開啟，而不是直接雙擊 HTML 檔案。'));
      count.textContent='載入失敗';console.error(error);
    }
  }
  init();
})();
