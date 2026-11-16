'use strict';
(function () {
  const page=document.getElementById('slide');
  const counter=document.getElementById('slide-counter');
  const previous=document.getElementById('prev');
  const next=document.getElementById('next');
  let deck=null, index=0;
  const rosterById=new Map();
  let verifiedJapaneseNames=[]; // Exact names from verified roster, never inferred from Unicode ranges.
  const tag=(t,cls,text)=>{const n=document.createElement(t);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
  function appendLocalized(parent, text, lang='zh-TW', segments) {
    if (segments && segments.length) {for(const part of segments)appendLocalized(parent,part.text,part.lang);return;}
    if (lang==='en') {const s=tag('span','',text);s.lang='en';parent.append(s);return;}
    // In Chinese prose, mark only exact full Japanese names from the audited roster.
    // The characters themselves are preserved, including source-specific variants.
    // Do not guess Chinese/Japanese from Unicode range or the player's nationality.
    if (lang==='zh-TW' && verifiedJapaneseNames.length) {
      let match=null;
      for(const name of verifiedJapaneseNames) {
        const at=text.indexOf(name);
        if(at>=0 && (!match || at<match.at || (at===match.at && name.length>match.name.length)))match={at,name};
      }
      if(match) {
        if(match.at>0)appendLocalized(parent,text.slice(0,match.at),lang);
        const jp=tag('span','',match.name);jp.lang='ja';parent.append(jp);
        const after=match.at+match.name.length;
        if(after<text.length)appendLocalized(parent,text.slice(after),lang);
        return;
      }
    }
    // Only Latin letters and numbers are segmented automatically; never infer Kanji's language from Unicode.
    const re=/[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9,.'’%:+\-/ ]*/g;let last=0,m;
    while ((m=re.exec(text)) !== null) {
      if(m.index>last){const s=tag('span','',text.slice(last,m.index));s.lang=lang;parent.append(s);}
      const roman=tag('span','number-run',m[0]);roman.lang='en';parent.append(roman);last=re.lastIndex;
    }
    if(last<text.length){const s=tag('span','',text.slice(last));s.lang=lang;parent.append(s);}
  }
  const labeled=(t,cls,text)=>{const n=tag(t,cls);appendLocalized(n,text);return n;};
  function badge(grade,context='單場評級') {
    const letter=grade[0], suffix=grade.slice(1);
    const b=tag('span',`rating-badge rating-${letter}`);b.setAttribute('role','img');
    b.setAttribute('aria-label',`${context} ${letter}${suffix==='+'?' 加':suffix==='-'?' 減':''}`);
    b.append(tag('span','',letter));if(suffix)b.append(tag('span','sign',suffix));return b;
  }
  function rosterName(player) {
    const n=tag('span');appendLocalized(n,player.name,player.name_lang,player.name_segments);return n;
  }
  function statCard(block) {
    const c=tag('div','stat-card');const value=tag('div','stat-value');
    appendLocalized(value,block.value,'en');if(block.unit) value.append(labeled('span','stat-unit',block.unit));
    c.append(labeled('div','stat-label',block.label),value);return c;
  }
  const kindLabels={official_record:'紀錄／原文引述',participant_statement:'當事人說法',media_commentary:'媒體報導',analysis_inference:'分析判讀',uncertainty:'資料限制'};
  function textCard(block) {
    const c=tag('div','evidence-card kind-'+block.evidence_kind);
    c.append(tag('span','evidence-kind',kindLabels[block.evidence_kind]||'資料'));const p=tag('p');
    appendLocalized(p,block.text,'zh-TW',block.text_segments);c.append(p);return c;
  }
  function playerCard(block) {
    const player=rosterById.get(block.player_id);
    if(!player)return textCard({text:'球員資料缺漏（'+block.player_id+'）',evidence_kind:'uncertainty'});
    const c=tag('article','player-card');const head=tag('div','player-head');const info=tag('div');
    const title=tag('h3','player-name');title.append(rosterName(player));
    const roles=labeled('div','player-role',player.roles.join(' · '));info.append(title,roles);head.append(badge(player.rating),info);c.append(head);
    const extra=Object.entries(player.additional_ratings||{});
    if(extra.length){const area=tag('div','player-meta');
      for(const [kind,grade] of extra){const item=tag('div','additional-rating');item.append(labeled('span','',kind),badge(grade,kind));area.append(item);}c.append(area);
    }
    const p=tag('p','player-summary');appendLocalized(p,block.summary);c.append(p);
    if(player.rating_note)c.append(labeled('p','player-meta-note',player.rating_note));
    return c;
  }
  function rosterGrid(ids) {
    const grid=tag('div','roster-grid');
    ids.forEach(id=>{
      const player=rosterById.get(id);if(!player)return;
      const item=tag('div','roster-item');item.append(badge(player.rating));
      const info=tag('div','roster-info');const name=tag('div','roster-name');name.append(rosterName(player));
      info.append(name,labeled('div','roster-note',player.quick_note||player.roles.join('、')));
      if(Object.keys(player.additional_ratings||{}).length)info.append(labeled('div','roster-extended',Object.entries(player.additional_ratings).map(([k,v])=>k+' '+v).join('；')));
      item.append(info,labeled('span','roster-role',player.roles.join(' / ')));grid.append(item);
    });return grid;
  }
  function eventCard(b) {
    const card=tag('div','event-card');const marker=tag('div','event-pin',String(b.inning));
    const body=tag('div','event-content');body.append(labeled('div','event-heading',`${b.inning} 局${b.half==='top'?'上':'下'}`));
    body.append(labeled('p','',b.description));
    if(b.score_after){const score=tag('p','event-score');score.append(tag('span','',`${b.score_before.away}–${b.score_before.home}  →  ${b.score_after.away}–${b.score_after.home}`));body.append(score);}
    card.append(marker,body);return card;
  }
  const SVG_NS='http://www.w3.org/2000/svg';
  function svgElement(name,attrs={},text){const e=document.createElementNS(SVG_NS,name);for(const[k,v]of Object.entries(attrs))e.setAttribute(k,String(v));if(text!==undefined)e.textContent=text;return e;}
  function chartCard(block) {
    const c=tag('div','chart-card');c.append(labeled('div','chart-heading',block.metric));
    const legend=tag('div','chart-legend');const tones=['#995D49','#596452','#7C7A9B'];
    block.series.forEach((name,i)=>{const item=tag('span','legend-item');const swatch=tag('span','legend-swatch');swatch.style.background=tones[i%tones.length];item.append(swatch,labeled('span','',name));legend.append(item);});c.append(legend);
    const svg=svgElement('svg',{viewBox:'0 0 760 290',role:'img','aria-label':block.metric+'。'+block.series.map((name,i)=>name+'：'+block.values[i].join('、')).join('；')});
    const values=block.values.flat(),top=Math.max(1,...values),maxValue=Math.ceil(top*1.15);
    const x0=46,y0=25,w=685,h=216,base=y0+h;
    for(let j=0;j<=4;j++){
      const v=maxValue*j/4,y=base-v/maxValue*h;
      svg.append(svgElement('line',{x1:x0,y1:y,x2:x0+w,y2:y,class:'grid-line'}));
      svg.append(svgElement('text',{x:36,y:y+4,'text-anchor':'end'},String(Number(v.toFixed(2)))));
    }
    svg.append(svgElement('line',{x1:x0,y1:base,x2:x0+w,y2:base,class:'axis'}));
    if(block.chart_type==='line'){
      block.series.forEach((name,seriesIndex)=>{
        const points=block.values[seriesIndex].map((v,i)=>[x0+(i+.5)*w/block.labels.length,base-v/maxValue*h]);
        svg.append(svgElement('polyline',{points:points.map(p=>p.join(',')).join(' '),fill:'none',stroke:tones[seriesIndex%tones.length],'stroke-width':3,'stroke-dasharray':seriesIndex?'8 5':'none'}));
        for(const [x,y]of points)svg.append(svgElement('circle',{cx:x,cy:y,r:4,fill:tones[seriesIndex%tones.length]}));
      });
    } else {
      const groupW=w/block.labels.length;
      block.labels.forEach((label,i)=>{
        const count=block.series.length,bw=Math.max(4,Math.min(29,groupW/(count+1.5))),gap=4;
        block.values.forEach((row,j)=>{
          const val=row[i],height=val/maxValue*h,x=x0+i*groupW+(groupW-count*bw-(count-1)*gap)/2+j*(bw+gap),y=base-height;
          svg.append(svgElement('rect',{x,y,width:bw,height,rx:2,fill:tones[j%tones.length]}));
          if(val>0)svg.append(svgElement('text',{x:x+bw/2,y:y-7,'text-anchor':'middle'},String(val)));
        });
        svg.append(svgElement('text',{x:x0+(i+.5)*groupW,y:base+20,'text-anchor':'middle'},label));
      });
    }
    c.append(svg);return c;
  }
  function tableCard(block) {
    const panel=tag('section','score-table-card');
    const scroll=tag('div','score-table-scroll');scroll.tabIndex=0;
    scroll.setAttribute('role','region');scroll.setAttribute('aria-label',block.title+'，可水平捲動');
    const table=tag('table','score-table');
    const caption=tag('caption','score-table-caption');appendLocalized(caption,block.title);table.append(caption);
    const head=tag('thead');const hr=tag('tr');
    for (const heading of block.headers) {
      const th=tag('th','score-table-column');th.scope='col';
      appendLocalized(th,heading);hr.append(th);
    }
    head.append(hr);table.append(head);
    const body=tag('tbody');
    for (const row of block.rows) {
      const tr=tag('tr');
      row.forEach((value,i)=>{
        const cell=tag(i===0?'th':'td',i===0?'score-table-team':'score-table-number');
        if(i===0){cell.scope='row';appendLocalized(cell,value);}
        else {appendLocalized(cell,value,'en');if(i===row.length-1)cell.classList.add('score-table-total');}
        tr.append(cell);
      });
      body.append(tr);
    }
    table.append(body);scroll.append(table);panel.append(scroll);
    if(block.note)panel.append(labeled('p','score-table-note',block.note));
    return panel;
  }
  function render(idx,{focus=false,updateHash=true}={}) {
    if(!deck)return;
    index=Math.min(Math.max(idx,0),deck.slides.length-1);
    const slide=deck.slides[index];page.className='slide-panel layout-'+slide.layout;
    const kicker=tag('div','slide-kicker');const sectionLabel=tag('span','',slide.section.replaceAll('-',' / '));sectionLabel.lang='en';const dateLabel=tag('span','',deck.game_id.slice(0,10));dateLabel.lang='en';kicker.append(sectionLabel,dateLabel);
    const title=tag('h1','slide-title');appendLocalized(title,slide.title,'zh-TW',slide.title_segments);title.id='slide-title';title.tabIndex=-1;
    const message=labeled('p','slide-message',slide.message);
    const body=tag('div','slide-body');
    for(const block of slide.blocks){
      let card;
      switch(block.type){case 'stat':card=statCard(block);break;case 'text':card=textCard(block);break;
      case 'player':card=playerCard(block);break;case 'event':card=eventCard(block);break;
      case 'chart':card=chartCard(block);break;case 'table':card=tableCard(block);break;default:continue;}
      body.append(card);
    }
    if(slide.layout==='roster-overview')body.append(rosterGrid(slide.roster_player_ids));
    const caveats=tag('footer','slide-caveats');
    if(slide.caveats.length){caveats.append(tag('div','caveat-label','閱讀限制'));for(const text of slide.caveats)caveats.append(labeled('p','',text));}
    const citations=tag('div','slide-source');citations.append(labeled('span','','Wiki 來源：'));
    for(const id of slide.source_sections)citations.append(tag('span','source-id',id));caveats.append(citations);
    page.replaceChildren(kicker,title,message,body,caveats);
    counter.textContent=String(index+1).padStart(2,'0')+' / '+String(deck.slides.length).padStart(2,'0');
    previous.disabled=index===0;next.disabled=index===deck.slides.length-1;
    document.title=slide.title+'｜NPB 賽後簡報';
    if(updateHash && location.hash!=='#'+slide.id)history.replaceState(null,'','#'+slide.id);
    if(focus)title.focus({preventScroll:true});
    window.scrollTo({top:0,behavior:'instant'});
  }
  async function init() {
    try {
      const response=await fetch('./slides.json',{cache:'no-store'});
      if(!response.ok)throw new Error('HTTP '+response.status);
      deck=await response.json();
      if(deck.schema_version!==1 || !Array.isArray(deck.slides)||!Array.isArray(deck.roster)||!deck.slides.length)throw new Error('簡報資料結構不符');
      deck.roster.forEach(p=>rosterById.set(p.player_id,p));
      verifiedJapaneseNames=[...new Set(deck.roster.filter(p=>p.name_lang==='ja').map(p=>p.name))].sort((a,b)=>b.length-a.length);
      const hash=decodeURIComponent(location.hash.slice(1));const initial=deck.slides.findIndex(s=>s.id===hash);
      render(initial<0?0:initial,{updateHash:!!hash});
      previous.addEventListener('click',()=>render(index-1,{focus:true}));
      next.addEventListener('click',()=>render(index+1,{focus:true}));
      document.addEventListener('keydown',e=>{
        const elem=document.activeElement;
        if(elem && (['INPUT','TEXTAREA','SELECT'].includes(elem.tagName)||elem.isContentEditable)||e.altKey||e.ctrlKey||e.metaKey)return;
        if(e.key==='ArrowLeft' && index>0){e.preventDefault();render(index-1,{focus:true});}
        if(e.key==='ArrowRight' && index<deck.slides.length-1){e.preventDefault();render(index+1,{focus:true});}
      });
      window.addEventListener('hashchange',()=>{const hash=decodeURIComponent(location.hash.slice(1));const i=deck.slides.findIndex(s=>s.id===hash);if(i>=0 && i!==index)render(i,{focus:true,updateHash:false});});
    }catch(error){page.replaceChildren(tag('p','error-message','簡報資料無法載入。請在專案根目錄執行 Python HTTP 伺服器，勿直接雙擊 HTML。'));console.error(error);}
  }
  init();
})();
