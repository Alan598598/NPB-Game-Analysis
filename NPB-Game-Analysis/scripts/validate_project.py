#!/usr/bin/env python3
"""Validate the NPB static Wiki-to-slides project without third-party packages."""
from __future__ import annotations
import datetime as dt
import json
import math
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'
GRADE=re.compile(r'^(?:S|[A-E][+-]?)$')
GAME_ID=re.compile(r'^\d{4}-\d{2}-\d{2}-[a-z0-9-]+$')
SOURCE_ID=re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
ALLOWED_LAYOUT={'match-overview','roster-overview','game-timeline','key-play','player-analysis','comparison','summary','sources'}
ALLOWED_LANG={'zh-TW','ja','en'}
ALLOWED_KIND={'official_record','participant_statement','media_commentary','analysis_inference','uncertainty'}
ALLOWED_BLOCK_TYPES={'text','stat','player','event','chart','table'}
ERRORS=[];CHECKS=[]

def check(ok,msg):
    CHECKS.append((bool(ok),msg))
    if not ok: ERRORS.append(msg)

def required_fields(obj, schema, label):
    check(isinstance(obj,dict),label+' 必須為 object')
    if not isinstance(obj,dict): return False
    for key,cls in schema.items():check(key in obj and isinstance(obj.get(key),cls),label+'.'+key+' 必須為 '+str(cls))
    return True

def strings(value):return isinstance(value,list) and all(isinstance(v,str) and bool(v.strip()) for v in value)

def known_sources(values, known, label):
    check(strings(values),label+' 必須為非空字串陣列')
    if isinstance(values,list):
        check(bool(values),label+' 不得空白')
        check(len(values)==len(set(map(str,values))),label+' 不得重複 source-id')
        check(all(isinstance(x,str) and x in known for x in values),label+' 必須指向 Wiki 實際來源 ID')

def check_segmentation(obj,field,parts,label):
    if parts not in obj: return
    pieces=obj[parts]
    check(isinstance(pieces,list) and bool(pieces),label+'.'+parts+' 必須為非空陣列')
    if not isinstance(pieces,list):return
    valid=all(isinstance(s,dict) and isinstance(s.get('text'),str) and s.get('lang') in ALLOWED_LANG for s in pieces)
    check(valid,label+'.'+parts+' 語言分段錯誤')
    if valid:check(''.join(s['text'] for s in pieces)==obj[field],label+'.'+parts+' 串接結果不等於 '+field)

def resolve_inside(root, rel, label):
    if not isinstance(rel,str) or not rel.strip():check(False,label+' 路徑無效');return None
    parsed=urlsplit(rel)
    check(not parsed.scheme and not parsed.netloc and not parsed.query and not parsed.fragment,label+' 不可是外部或帶參數網址')
    check(not rel.startswith(('/','\\')) and '\\' not in rel and '..' not in Path(rel).parts,label+' 必須安全的相對路徑')
    p=(root/rel).resolve()
    try:p.relative_to(root.resolve())
    except ValueError:check(False,label+' 路徑越界');return None
    check(p.is_file(),label+' 檔案不存在：'+str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else label)
    return p

def validate():
    manifest=DOCS/'data/games.json'
    try:catalog=json.loads(manifest.read_text(encoding='utf-8'))
    except Exception as e:check(False,'games.json 無法讀取：'+str(e));return
    required_fields(catalog,{'schema_version':int,'games':list},'games.json')
    check(catalog.get('schema_version')==1,'games.json schema_version 必須為 1')
    games=catalog.get('games',[])
    check(bool(games),'games.json 至少收錄一場賽事')
    seen_games=set()
    for ix,game in enumerate(games):
        label=f'games[{ix}]'
        required_fields(game,{'id':str,'date':str,'competition':str,'away_team':str,'home_team':str,'away_score':int,'home_score':int,'slides_path':str,'wiki_source':str},label)
        game_id=game.get('id','')
        check(isinstance(game_id,str) and bool(GAME_ID.fullmatch(game_id)),label+' game-id 格式不符')
        check(game_id not in seen_games,label+' game-id 重複')
        seen_games.add(game_id)
        try:dt.date.fromisoformat(game.get('date','')); date_valid=True
        except Exception:date_valid=False
        check(date_valid,label+' 日期無效')
        check(game_id.startswith(game.get('date','')+'-'),label+' game-id 日期不一致')
        for k in ('away_score','home_score'):
            v=game.get(k)
            check(type(v) is int and v>=0,label+'.'+k+' 必須非負整數')
        for k in ('competition','away_team','home_team'):
            check(isinstance(game.get(k),str) and bool(game[k].strip()),label+'.'+k+' 不得空白')
        game_html=resolve_inside(DOCS,game.get('slides_path',''),label+'.slides_path')
        check(game.get('slides_path')==f'slides/{game_id}/index.html',label+' slides_path 與 game-id 不一致')
        wiki=resolve_inside(ROOT,game.get('wiki_source',''),label+'.wiki_source')
        expected_wiki=f'wiki/{game.get("date", "")[:4]}/{game_id}.md'
        check(game.get('wiki_source')==expected_wiki,label+' Wiki 路徑與 game-id 不一致')
        content_path=resolve_inside(ROOT,f'slides-content/{game_id}.md',label+' slides-content')
        slide_data_path=resolve_inside(DOCS,f'slides/{game_id}/slides.json',label+' slides.json')
        if not (wiki and wiki.is_file() and slide_data_path and slide_data_path.is_file()):continue
        wiki_text=wiki.read_text(encoding='utf-8')
        markers=re.findall(r'<!-- source-id: ([a-z0-9-]+) -->',wiki_text)
        check(len(set(markers))==len(markers),label+' Wiki source-id 不可重複')
        check(bool(markers) and all(SOURCE_ID.fullmatch(x) for x in markers),label+' Wiki source-id 格式不正確')
        marker_set=set(markers)
        try:data=json.loads(slide_data_path.read_text(encoding='utf-8'))
        except Exception as e:check(False,label+' slides.json 無法讀取：'+str(e));continue
        required_fields(data,{'schema_version':int,'game_id':str,'wiki_source':str,'roster':list,'slides':list},label+'.slides.json')
        check(data.get('schema_version')==1,label+' slides.json schema_version 必須 1')
        check(data.get('game_id')==game_id,label+' slides.json game-id 不一致')
        check(data.get('wiki_source')==game.get('wiki_source'),label+' slides.json wiki_source 不一致')
        roster=data.get('roster',[]);slides=data.get('slides',[])
        check(bool(roster),label+' roster 不得為空')
        check(bool(slides),label+' slides 不得為空')
        seen_players={}; seen_names=set()
        for ri,p in enumerate(roster):
            x=f'{label}.roster[{ri}]'
            required_fields(p,{'player_id':str,'team':str,'name':str,'name_lang':str,'roles':list,'rating':str,'additional_ratings':dict,'rating_note':str,'source_sections':list},x)
            pid=p.get('player_id','')
            check(bool(re.fullmatch(r'p\d{3,}',pid)),x+' player_id 格式錯誤')
            check(pid not in seen_players,x+' player_id 重複')
            seen_players[pid]=p
            check((p.get('team'),p.get('name')) not in seen_names,x+' 同一球隊姓名重複')
            seen_names.add((p.get('team'),p.get('name')))
            check(p.get('team') in {game.get('away_team'),game.get('home_team')},x+' team 不符合比賽')
            check(p.get('name_lang') in ALLOWED_LANG,x+' name_lang 不允許')
            check(isinstance(p.get('name'),str) and bool(p['name'].strip()),x+' name 不得空白')
            check(strings(p.get('roles')),x+' roles 必須為非空字串陣列')
            check(isinstance(p.get('rating'),str) and bool(GRADE.fullmatch(p['rating'])),x+' rating 必須 S～E 合法值')
            for name,g in p.get('additional_ratings',{}).items():
                check(isinstance(name,str) and bool(name.strip()) and isinstance(g,str) and bool(GRADE.fullmatch(g)),x+' additional_ratings 不合法')
            if 'name_segments' in p:check_segmentation(p,'name','name_segments',x)
            known_sources(p.get('source_sections'),marker_set,x)
        # Source roster table is checked directly against JSON, not only JSON self-consistency.
        try:
            section1=wiki_text.split('<!-- source-id: roster-fighters -->',1)[1].split('<!-- source-id: roster-hawks -->',1)[0]
            section2=wiki_text.split('<!-- source-id: roster-hawks -->',1)[1].split('<!-- source-id: game-flow -->',1)[0]
            expected={}
            for team,section in [(game['away_team'],section1),(game['home_team'],section2)]:
                for line in section.splitlines():
                    m=re.match(r'^\|\s*(.+?)\s*\|\s*([A-E][+-]?|S)\s*\|',line)
                    if m:
                        name,rating=m.groups()
                        check((team,name) not in expected,label+' 原文章清單重複 '+name)
                        expected[(team,name)]=rating
            actual={(p['team'],p['name']):p['rating'] for p in roster}
            check(bool(expected) and actual==expected,label+f' 與 Wiki 球員快速清單／評級不相符（原文 {len(expected)} 位，JSON {len(actual)} 位）')
        except Exception as e:check(False,label+' 無法解析 Wiki 快速清單：'+str(e))
        all_overviews=[]; slide_ids=set(); seen_types=set(); seen_layouts=set()
        for si,s in enumerate(slides):
            y=f'{label}.slides[{si}]'
            required_fields(s,{'id':str,'section':str,'layout':str,'title':str,'message':str,'blocks':list,'source_sections':list,'caveats':list},y)
            sid=s.get('id')
            check(isinstance(sid,str) and bool(sid.strip()) and sid not in slide_ids,y+' id 重複或空白')
            slide_ids.add(sid)
            layout=s.get('layout');check(layout in ALLOWED_LAYOUT,y+' 版型不符');seen_layouts.add(layout)
            for k in ('section','title','message'):
                check(isinstance(s.get(k),str) and bool(s[k].strip()),y+'.'+k+' 不得空白')
            check('title_segments' in s,y+' title_segments 缺漏')
            check_segmentation(s,'title','title_segments',y)
            for seg in s.get('title_segments',[]):
                if not isinstance(seg,dict) or not isinstance(seg.get('text'),str):continue
                if 'player_id' in seg:
                    p=seen_players.get(seg['player_id'])
                    check(p is not None,y+' 標題片段 player_id 不存在')
                    if p:
                        check(seg['text'] in p['name'],y+' 標題片段不是對應球員姓名的一部分')
                        check(seg['lang']==p['name_lang'],y+' 標題片段語言與清冊姓名不一致')
            known_sources(s.get('source_sections'),marker_set,y+'.source_sections')
            check(isinstance(s.get('caveats'),list) and all(isinstance(x,str) for x in s['caveats']),y+'.caveats 格式錯誤')
            if layout=='roster-overview':
                ids=s.get('roster_player_ids')
                check(strings(ids),y+' roster_player_ids 必要且不可空')
                if isinstance(ids,list):all_overviews.extend(ids)
            else:check('roster_player_ids' not in s,y+' 非清冊版型不應使用 roster_player_ids')
            observed=[];seen_event_orders=set()
            for bi,b in enumerate(s.get('blocks',[])):
                z=f'{y}.blocks[{bi}]';t=b.get('type') if isinstance(b,dict) else None
                check(t in ALLOWED_BLOCK_TYPES,z+' type 不合法')
                if not isinstance(b,dict) or t not in ALLOWED_BLOCK_TYPES:continue
                seen_types.add(t)
                known_sources(b.get('source_sections'),marker_set,z+'.source_sections')
                observed.extend(b.get('source_sections',[]))
                if t=='text':
                    required_fields(b,{'text':str,'evidence_kind':str},z)
                    check(b.get('evidence_kind') in ALLOWED_KIND,z+' evidence_kind 無效')
                    check(bool(b.get('text','').strip()),z+' text 空白')
                    check_segmentation(b,'text','text_segments',z)
                elif t=='stat':required_fields(b,{'label':str,'value':str,'unit':str},z)
                elif t=='player':
                    required_fields(b,{'player_id':str,'summary':str},z)
                    check(b.get('player_id') in seen_players,z+' player_id 不存在')
                elif t=='event':
                    required_fields(b,{'inning':int,'half':str,'order':int,'description':str},z)
                    check(type(b.get('inning')) is int and b['inning']>=1 and type(b.get('order')) is int and b['order']>=1,z+' inning/order 無效')
                    check(b.get('half') in {'top','bottom'},z+' half 不合法')
                    check(b.get('order') not in seen_event_orders,z+' 事件 order 重複')
                    seen_event_orders.add(b.get('order'))
                    check(('score_before' in b)==('score_after' in b),z+' 前後比分必須一起存在')
                    for sk in ('score_before','score_after'):
                        if sk in b:
                            check(isinstance(b[sk],dict),z+'.'+sk+' 格式錯誤')
                            if isinstance(b[sk],dict):
                                for side in ('away','home'):check(type(b[sk].get(side)) is int and b[sk][side]>=0,z+'.'+sk+'.'+side+' 需要非負整數')
                elif t=='chart':
                    required_fields(b,{'chart_type':str,'metric':str,'unit':str,'labels':list,'series':list,'values':list},z)
                    check(b.get('chart_type') in {'line','bar'},z+' chart_type 無效')
                    check(strings(b.get('labels')) and strings(b.get('series')),z+' labels/series 不能空')
                    vals=b.get('values')
                    check(isinstance(vals,list) and len(vals)==len(b.get('series',[])),z+' values 系列維度不符')
                    if isinstance(vals,list):
                        for row in vals:
                            check(isinstance(row,list) and len(row)==len(b.get('labels',[])) and all(type(v) in (int,float) and math.isfinite(v) for v in row),z+' 圖表資料必須等長、為有限數值')
                elif t=='table':
                    required_fields(b,{'title':str,'headers':list,'rows':list,'note':str},z)
                    headers=b.get('headers',[]);rows=b.get('rows',[])
                    check(strings(headers) and len(headers)>=2,z+' 表格須有至少 2 欄標題')
                    check(isinstance(headers,list) and len(set(map(str,headers)))==len(headers),z+' 欄標題不可重複')
                    check(isinstance(rows,list) and bool(rows),z+' 表格資料不可空白')
                    for ri,row in enumerate(rows):
                        check(isinstance(row,list) and len(row)==len(headers) and all(isinstance(cell,str) and bool(cell.strip()) for cell in row),z+f' 表格第 {ri+1} 列必須完整且所有儲存格為字串')
            check(set(observed).issubset(set(s.get('source_sections',[]))),y+' 頁面來源必須涵蓋每個資料區塊')
        check(len(all_overviews)==len(set(all_overviews)) and set(all_overviews)==set(seen_players),label+f' roster-overview 必須完整無重複呈現清冊（{len(all_overviews)}/{len(roster)}）')
        check(len(seen_layouts)==8,label+' 測試場次須實際涵蓋全部 8 種版型')
        check(bool(seen_types),label+' 簡報須有資料區塊')
        # v1.2 test-case regression: score table must match the Wiki (nine innings and totals).
        if game_id=='2026-10-14-fighters-hawks':
            second=next((s for s in slides if s.get('id')=='s02'),None)
            checks=[b for b in second.get('blocks',[]) if b.get('type')=='table'] if second else []
            check(len(checks)==1 and not any(b.get('type')=='chart' for b in second.get('blocks',[])),label+' 第二頁必須以一張表格取代長條圖' if second else label+' 第二頁不存在')
            if len(checks)==1:
                block=checks[0]
                source_intro=wiki_text.split('<!-- source-id: intro -->',1)[1].split('<!-- source-id: umpires -->',1)[0]
                source_rows=[]
                for line in source_intro.splitlines():
                    if re.match(r'^\|\s*(?:局數|日本火腿|軟銀)\s*\|',line):
                        source_rows.append([x.strip() for x in line.split('|')[1:-1]])
                check(len(source_rows)==3,label+' Wiki 原文逐局比分表不可解析')
                if len(source_rows)==3:
                    expected_headers=['球隊']+source_rows[0][1:]
                    check(block.get('headers')==expected_headers,label+' 第 2 頁表格欄標題與 Wiki 不一致')
                    check(block.get('rows')==source_rows[1:],label+' 第 2 頁逐局比分與 Wiki 不一致')
                rows=block.get('rows',[])
                if len(rows)==2 and all(isinstance(row,list) and len(row)==11 for row in rows):
                    away,home=rows
                    check(away[0]=='日本火腿' and home[0]=='軟銀' and away[9]=='0' and home[9]=='X',label+' 九局狀態錯誤')
                    check(all(v.isdecimal() for v in away[1:]) and all(v.isdecimal() for v in home[1:9]+home[10:]),label+' 逐局得分必須是非負整數，僅主場第九局允許 X')
                    check(sum(map(int,away[1:10]))==int(away[10])==game.get('away_score') and sum(map(int,home[1:9]))==int(home[10])==game.get('home_score'),label+' 逐局得分合計與賽事結果不一致')
                    check('未進攻' in block.get('note','') and 'X' in block.get('note',''),label+' 必須解釋 X 表示未進攻')
        if content_path and content_path.is_file():
            doc=content_path.read_text(encoding='utf-8')
            check(len(re.findall(r'^## Slide \d+',doc,re.M))==len(slides),label+' 逐頁內容稿頁數不一致')
            check(all(s['title'] in doc and ('- `id`：'+s['id']+'\n') in doc for s in slides),label+' 逐頁內容稿標題或 ID 不一致')
    # Validate wiki index markdown links exist.
    wiki_index=ROOT/'wiki/index.md'
    check(wiki_index.is_file(),'wiki/index.md 不存在')
    if wiki_index.is_file():
        body=wiki_index.read_text(encoding='utf-8')
        for target in re.findall(r'\]\(([^)]+)\)',body):
            resolve_inside(ROOT/'wiki',target,'wiki/index.md 連結')
        for game in games:
            check(game['id'] in body,'Wiki index 未收錄 '+game['id'])
    # No image resources (user's explicit design decision), no external runtime dependencies.
    for path in DOCS.rglob('*'):
        if not path.is_file():continue
        check(path.suffix.lower() not in {'.png','.jpg','.jpeg','.webp','.gif','.svg','.bmp','.ico'},'禁止圖片檔：'+str(path.relative_to(ROOT)))
        if path.suffix.lower() in {'.html','.css','.js'}:
            text=path.read_text(encoding='utf-8')
            check(not re.search(r'<\s*(?:img|image|picture|video|iframe)\b',text,re.I),'禁止圖片/影音標籤：'+str(path.relative_to(ROOT)))
            if path.suffix.lower()=='.css':check(not re.search(r'url\s*\(',text,re.I),'禁止 CSS 外部圖片 URL：'+str(path.relative_to(ROOT)))
            if path.suffix.lower()=='.js':check(not re.search(r'\binnerHTML\b',text),'禁止把資料當 HTML 注入：'+str(path.relative_to(ROOT)))
    for path in [DOCS/'index.html',DOCS/'css/site.css',DOCS/'js/deck.js',DOCS/'js/home.js']:
        check(path.is_file(),'必要前端檔案不存在：'+str(path.relative_to(ROOT)))
    for rule in ['AGENTS.md','rules/npb-analysis.md','rules/wiki-to-slides.md','rules/design-system.md']:
        check((ROOT/rule).is_file() and (ROOT/rule).stat().st_size>0,'必要規則文件不存在：'+rule)

if __name__=='__main__':
    validate()
    print('NPB Wiki → Slides | automated validation')
    print(f'Checks: {len(CHECKS)} | Passed: {len(CHECKS)-len(ERRORS)} | Failed: {len(ERRORS)}')
    if ERRORS:
        for e in ERRORS:print('  [FAIL] '+e)
    else:print('  [PASS] JSON structure, roster/source parity, links, permitted layouts/blocks, image restrictions')
    print('  [NOT RUN] Human fact-check against external official source, Windows font availability, mobile/200% layout, GitHub Pages live deployment')
    sys.exit(1 if ERRORS else 0)
