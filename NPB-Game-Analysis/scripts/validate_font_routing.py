#!/usr/bin/env python3
"""Font-routing assertions for the 2026 NPB sample. No external network dependency."""
from pathlib import Path
import json
import re
import sys
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'docs/slides/2026-10-14-fighters-hawks/slides.json').read_text(encoding='utf8'))
AUDIT=json.loads((ROOT/'tests/font-name-audit.json').read_text(encoding='utf8'))
CSS=(ROOT/'docs/css/site.css').read_text(encoding='utf8')
JS=(ROOT/'docs/js/deck.js').read_text(encoding='utf8')
errors=[]
def verify(p,reason):
 if not p:errors.append(reason)
roster=DATA['roster']; by_id={p['player_id']:p for p in roster}; names=AUDIT['japanese_official_spellings']
verify(len(roster)==34,'清冊必須有 34 位')
verify(len(names)==30,'官方字形清冊必須有 30 位日文漢字姓名')
verify(set(by_id)==set(names)|set(AUDIT['english_name_player_ids']),'每個球員必須有姓名來源語言')
for pid,name in names.items():
 p=by_id[pid]
 verify(p['name_lang']=='ja',f'{pid} 日文姓名未標 ja')
 verify(p.get('official_name_ja')==name,f'{pid} 官方日文姓名未記錄正確')
 variant=AUDIT['expected_source_variants'].get(pid)
 verify(bool(p.get('source_name_variant',False))==bool(variant),f'{pid} 原文異體字標示錯誤')
 if variant:verify(p['name']==variant['wiki_name'] and name==variant['official_name'],f'{pid} 原文姓名遭改寫')
 else:verify(p['name']==name,f'{pid} 原文姓名與官方姓名不一致，請人工審核')
for pid in AUDIT['english_name_player_ids']:
 verify(by_id[pid]['name_lang']=='en',f'{pid} 英文姓名未標 en')
# Every title must be segmented exactly; shortened Japanese/English names get audited person IDs.
for s in DATA['slides']:
 segments=s.get('title_segments',[])
 verify(bool(segments) and ''.join(a.get('text','') for a in segments)==s['title'],s['id']+' 標題語言分段不一致')
 for seg in segments:
  if 'player_id' in seg:
   person=by_id.get(seg['player_id'])
   verify(person is not None and seg['text'] in person['name'] and seg['lang']==person['name_lang'],s['id']+' 姓氏語言標記或球員連結不正確')
for sid,names in {'s14':['野村','水野'],'s16':['山縣','奈良間','進藤'],'s28':['Moinelo','鈴木'],'s30':['Osuna','松本','杉山']}.items():
 segments=next(s for s in DATA['slides'] if s['id']==sid)['title_segments']
 verify(all(any(p['text']==name and 'player_id' in p for p in segments) for name in names),sid+' 日文簡稱分段缺漏')
verify("appendLocalized(title,slide.title,'zh-TW',slide.title_segments)" in JS,'簡報標題未套用明確的 title_segments')
for label,needle in {
 '繁中標楷體':'"DFKai-SB"',
 '英數 Times New Roman':'"Times New Roman"',
 '日文 UD Digi Kyokasho':'"UD Digi Kyokasho N-R"',
 '日文 lang 規則':':lang(ja)',
 '英文 lang 規則':':lang(en)',
 '繁中 lang 規則':':lang(zh-TW)'
}.items():verify(needle in CSS,label+' 缺少必要 CSS')
verify("appendLocalized(n,player.name,player.name_lang,player.name_segments)" in JS,'球員姓名未依語言欄位輸出')
verify("sectionLabel.lang='en'" in JS,'章節英文代碼未套正確語言')
verify('verifiedJapaneseNames=[...new Set(' in JS,'沒有建立已核對的完整日本姓名名單')
verify("if (lang==='zh-TW' && verifiedJapaneseNames.length)" in JS,'中文段落未依完整姓名做日文片段標記')
verify((ROOT/'tests/font-check.html').exists(),'Windows 人工字型驗收頁不存在')
print('Font-routing checks:', 'FAIL' if errors else 'PASS')
print('Roster: 30 ja, 4 en; official-name variants: 2')
if errors:
 for e in errors:print('FAIL:',e)
 sys.exit(1)
print('Note: Browser font rendering on Windows still needs manual verification.')
