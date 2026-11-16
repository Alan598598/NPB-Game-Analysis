NPB Game Analysis · Wiki → Slides
將完整日本職棒（NPB）單場賽後分析保存在 Markdown Wiki，並使用可重用的原生 HTML／CSS／JavaScript 元件轉換成互動式網頁簡報。

目前狀態：v1.2 已上傳 GitHub 並發布 GitHub Pages。2026-11-16 由使用者完成 Windows Chrome 與正式網站的指定項目驗收。
正式交付連結
- 完整 GitHub Repository：Alan598598/NPB-Game-Analysis（main 分支；包含規範、Wiki、完整原始碼及測試）
- 正式展示網站：NPB Game Analysis（GitHub Pages；由 main 分支的 /docs 資料夾發布）
驗收依據：專案自動檢查結果，以及使用者於 2026-11-16 回報的 Windows Chrome 與 GitHub Pages 實際操作結果。使用者已確認的項目與尚未獨立驗證的項目會在第 7 節區分；本 README 更新本身不重新測試或變更網站。

1. 目前內容
項目	結果
第一場比賽	2026-10-14 北海道日本火腿鬥士 4：6 福岡軟銀鷹，洋聯高潮系列賽決勝輪第 1 戰
Wiki 全文	wiki/2026/2026-10-14-fighters-hawks.md
網頁簡報	docs/slides/2026-10-14-fighters-hawks/index.html
投影片	35 頁，使用 8 種標準版型
球員	34 人（日本火腿 17 人、軟銀 17 人），均在評級總覽中出現一次
評級	原文 S～E 規則；郡司「打擊 A-／綜合 C」分面向保留
JS/CSS 依賴	零第三方套件、零外部圖片
作業設計	GitHub Repository 公開規則、Wiki 與程式；GitHub Pages 由 /docs 發布互動簡報


關鍵入口
- [AGENTS.md](AGENTS.md)：AI 專案總規則，以 v0.4 為基礎，僅增補本次核准的標題語言與表格契約。
- [npb-analysis.md](rules/npb-analysis.md)：原始 NPB 賽後分析規範，未改寫。
- [wiki-to-slides.md](rules/wiki-to-slides.md)：Wiki 轉簡報規範，以 v0.4 為基礎增補 v1.2 資料欄位。
- [design-system.md](rules/design-system.md)：配色、字型、評級徽章與操作規範，沿用 v0.4 並增加 v1.2 表格規則。
- [index.md](wiki/index.md)：完整 Wiki 索引。
- [2026-10-14-fighters-hawks.md](slides-content/2026-10-14-fighters-hawks.md)：逐頁簡報內容稿與來源 ID。
- [games.json](docs/data/games.json)：公開簡報首頁資料。
- [slides.json](docs/slides/2026-10-14-fighters-hawks/slides.json)：35 頁簡報資料及全員清冊。
- [validate_project.py](scripts/validate_project.py)：不需另安裝套件的資料驗證程式。
2. Windows 本機開啟方法（不消耗 Codex 額度）
1. 下載專案 ZIP，完整解壓縮至專用資料夾，例如 C:\Projects\NPB-Game-Analysis。
2. 先進入專案最內層的 docs 資料夾，確認看得到 index.html。在 Windows 檔案總管該資料夾的網址列輸入 cmd，按 Enter。這樣命令提示字元就會開在正確位置。
3. 確認有安裝 Python，於上述 docs 資料夾中執行：
   py -m http.server 8000
   若 Windows 沒有 py 指令，但 python 可用，改用：
   python -m http.server 8000
4. 使用 Chrome 開啟 http://localhost:8000/，點擊唯一的賽事卡片進入簡報。若看到 404，先確認指令視窗所在資料夾就是含有 index.html 的 docs；若是在 C:\Users\... 直接執行 --directory docs，將找錯目錄。
   若想改由專案根目錄啟動，也可以先 cd 到真正的專案根目錄（同時看得到 AGENTS.md 與 docs），再執行 py -m http.server 8000 --directory docs。
5. 簡報操作：左上角箭頭回首頁；下方中央左右箭頭翻頁；也能按鍵盤左右方向鍵。
6. 結束時在終端機按 Ctrl+C 停止伺服器。
不要直接雙擊 docs/index.html。 多數瀏覽器會限制 file:// 頁面讀取 JSON，造成資料載入失敗。若尚未安裝 Python，可先安裝 Python 再執行上述指令；不需安裝 Codex 才能預覽。
資料驗證
在專案根目錄執行：
py scripts/validate_project.py
通過時會顯示檢查數量、失敗數量與未執行的人工測試。Python 標準函式庫即可，不需 pip install。
3. 固定目錄結構
NPB-Game-Analysis/
├─ AGENTS.md
├─ README.md
├─ FONT_VALIDATION.md
├─ .gitignore
├─ rules/
│  ├─ npb-analysis.md
│  ├─ wiki-to-slides.md
│  └─ design-system.md
├─ wiki/
│  ├─ index.md
│  └─ 2026/
│     └─ 2026-10-14-fighters-hawks.md
├─ slides-content/
│  └─ 2026-10-14-fighters-hawks.md
├─ scripts/
│  ├─ validate_project.py
│  └─ validate_font_routing.py
├─ tests/
│  ├─ font-check.html
│  └─ font-name-audit.json
└─ docs/
   ├─ index.html
   ├─ css/site.css
   ├─ js/home.js
   ├─ js/deck.js
   ├─ data/games.json
   └─ slides/2026-10-14-fighters-hawks/
      ├─ index.html
      └─ slides.json
4. 如何新增第二場賽事
在提出具體檔案清單並取得同意後：
1. 閱讀 AGENTS.md 及轉換與設計規範。確認新文章、賽事 ID 及公開安全性。
2. 在 wiki/YYYY/<game-id>.md 保存完整文章，建立段落 <!-- source-id: ... -->；更新 wiki/index.md。
3. 建立新的逐頁內容稿 slides-content/<game-id>.md；納入所有實際出賽者與原始評級。
4. 新增 docs/slides/<game-id>/index.html，複製首場簡報入口 HTML，沿用 ../../css/site.css 與 ../../js/deck.js，不重建樣式引擎。
5. 新增符合 schema_version: 1 的 docs/slides/<game-id>/slides.json；如有其他評級面向，在 roster.additional_ratings 保留。
6. 將賽事加入 docs/data/games.json，再執行驗證程式和實際瀏覽器測試。
7. 未經批准，不執行 git push、變更 Repository 可見性或啟用 Pages。
5. GitHub Repository 與 Pages 部署（已完成；2026-11-16）
使用者已將 v1.2 完整專案原始碼上傳至公開 GitHub Repository，並透過 GitHub Pages 發布展示網站。ZIP 僅作為離線專案備份，不是公開網址本身。
- Repository：https://github.com/Alan598598/NPB-Game-Analysis
- GitHub Pages：https://alan598598.github.io/NPB-Game-Analysis/
- 發布來源：Repository 的 main 分支、`/docs` 資料夾
在 Repository 的 Settings → Pages 已完成以下設定：
- Source：Deploy from a branch
- Branch：`main`
- Folder：`/docs`
網站採用相對路徑，支援 GitHub Pages 的 Repository 子路徑。使用者已於 2026-11-16 確認正式網站首頁、賽事入口、35 頁翻頁、第 2 頁逐局得分表、中英日字型及返回首頁功能均正常。 這是使用者的線上實測確認，不代表另外完成了全部裝置與無障礙測試。
6. 來源與內容處理說明
- 唯一比賽內容依據為使用者提供的完整 2026/10/14 賽後分析文章；本輪只進行內容轉換，沒有重新上網核對 NPB 官方成績。
- 原文章純文字包含來源名稱，但部分圖片、統計圖及超連結在轉存時遺失。Wiki 保留原文敘述，簡報不補造來源網址或缺失圖像；沒有在公開專案內重複保存原始原貌快照。
- Wiki 只進行 Markdown 格式整理及加入來源識別碼；部分轉存殘留的無法辨識圖表文字仍留在 Wiki，簡報沒有把它當成精確圖表來源。
- 原文章小標題「三名代打與代跑球員」下面實際列了四名球員。為忠實保留原始文字，Wiki 未更改該小標題；簡報將四名實際列出的球員全數呈現。
- 球員中文寫法、異體字與拉丁字母依原文保留；v1.1 已針對 30 位日文漢字姓名核對 NPB 官方寫法，兩筆與原文不同的字形記錄在 tests/font-name-audit.json，沒有擅自修改原文。已確認的日文片段使用語言標記，不僅憑漢字字形推測語言。
- 原稿使用的「官方紀錄」等說明是原文章中的來源歸類，不表示本專案已自行向官方網站再次核證。
- 公開 GitHub Repository 內的 Markdown Wiki 仍然公開可讀，即使 GitHub Pages 網站不設 Wiki 全文瀏覽頁面。因專案已公開，仍應確認全文公開與引用權利適當，並持續留意內容是否需要調整。
7. 測試與待辦（2026-11-16）
項目	狀態	說明
Python 靜態資料驗證	通過	v1.2：2,988 項檢查，0 失敗；涵蓋 34 人名單、35 頁標題語言分段、逐局得分表與 Wiki 逐格一致、原文評級、來源 ID、JSON 型態、8 版型、6 種可用區塊及連結
JavaScript 靜態語法	通過	node --check 驗證共用前端程式
HTTP 靜態檔案回應	通過	本機 HTTP 伺服器回傳首頁 200；使用者後續已在 Windows Chrome 完成本機網站及正式公開站點的操作驗收
Chromium DOM／互動測試	通過（模擬資料載入）	在 1440×900、390×844、720×800 三種視窗依序走完 35 頁；v1.2 檢查全頁標題文字不變、日英姓氏語言標記、逐局得分表及橫向捲動，無水平頁面溢出或 JS 例外。先前亦通過翻頁和鍵盤操作。瀏覽器環境限制 HTTP／file 導覽，改採將本地 JSON 注入相同前端程式測試；此項自動化測試未涵蓋瀏覽器 HTTP 整合載入；使用者已另於 Windows Chrome 與線上網站完成實測
Windows Chrome 指定字型實測	使用者確認通過（v1.2）	v1.1 三種指定字型已確認；v1.2 標題中日文姓氏／英文姓名分流亦已由使用者於 Windows Chrome 驗收通過
真正瀏覽器 200% 縮放	未執行	720px 窄視窗僅是布局壓力測試，不能冒稱等於真實 200% 縮放
手機裝置、灰階／色覺模擬	未執行	僅有 390px 桌面 Chromium 模擬視窗，尚未在實體手機驗收
原始比賽官方資訊再次核證	未執行	此輪為文章轉換，不含重新查證授權
GitHub Pages 實際發布與公開連結	使用者確認通過（2026-11-16）	Repository 與 Pages 已公開；使用者確認首頁、賽事入口、35 頁翻頁、第 2 頁比分表、指定字型及返回首頁六項功能正常


特殊可讀性說明： S 徽章依指定金底白字，純色對比約 2.51:1，CSS 已加入深色細描邊，但不能自動宣稱符合 WCAG AA；仍需人工視覺檢查。A～E 採深暖灰底及已指定的各字母顏色。
本版本採用「ChatGPT 製作完整初稿、使用者本機驗收、Codex 只處理必要修復」的低額度消耗流程，目前製作過程不需要使用 Codex。
8. v1.1 字型專項修正（2026-11-16）
本版僅修正多語姓名標記與檢查機制；詳細差異、官方姓名字形核對、Windows Chrome 人工驗收步驟見 [FONT_VALIDATION.md](FONT_VALIDATION.md)。
- 日文漢字姓名 30 位改以 lang="ja" 套用 UD Digi Kyokasho；英文姓名 4 位維持 en。
- 兩筆原文與 NPB 官方寫法不同，原文字串保留；見 tests/font-name-audit.json。
- 直接用 Windows Chrome 開啟 tests/font-check.html，按 F12 檢查 Rendered Fonts，不可只看 CSS 宣告。
- 額外執行 py scripts/validate_font_routing.py。
- Linux 截圖仍使用備援字型，不能作為 Windows 字型驗收證據；使用者已確認 v1.1 三種字型，以及 v1.2 新增的標題姓氏分流在 Windows Chrome 通過驗收。
9. v1.2 標題字型與逐局得分表修正（2026-11-16）
- 標題語言：全場 35 張投影片新增 title_segments，已確認之日文完整姓名與姓氏、英文姓名皆參照現有 roster.player_id，而不是靠漢字自動判斷；各頁 title 字串完全不變。
- 第二頁逐局得分：以原生 HTML <table> 取代長條圖，完整保留第 1～9 局與合計，軟銀九局下顯示 X，附未進攻說明。原本四張安打／失誤統計卡、分析文句不變。
- 資料與規則：加入第六種 table 區塊的必要欄位／驗證器；`AGENTS.md`、`rules/wiki-to-slides.md`、`rules/design-system.md` 只補入本次核准的規則；`rules/npb-analysis.md` 與完整 Wiki 全文均未修改。
- 檢查：`py scripts/validate_project.py` 通過 2,988 項；`py scripts/validate_font_routing.py` 通過；`node --check docs/js/deck.js` 通過。離線 Chromium 使用三種視窗尺寸遍歷 35 頁，標題與原文字串全部一致；第 2 頁表格與 Wiki 原始逐局比分完全相同；手機視窗可在表格內水平捲動。
- 實際驗收結果：使用者已於 Windows Chrome 確認簡報標題字型與第 2 頁得分表，且已完成 GitHub Pages 的首頁、賽事入口、35 頁翻頁、指定字型及返回首頁驗收。真正的 200% 縮放、實體手機及灰階／色覺模擬仍沒有獨立的通過紀錄。Linux 截圖使用備援字型，不能作為 Windows 指定字型的驗收證據。
這次建議抽測的標題
頁碼	應顯示為日文字型的姓名	應顯示為英文字型的姓名
14	野村、水野	—
16	山縣、奈良間、進藤	—
28	鈴木	Moinelo
30	松本、杉山	Osuna


在 Windows Chrome 可按 F12 → 選取標題內姓名 → Computed → Rendered Fonts，確認日文為 UD Digi Kyokasho N-R、英文為 Times New Roman。使用者已確認 v1.2 實際顯示通過，並於 2026-11-16 完成 GitHub Pages 發布與線上驗收。 本專案製作與本次 README 更新均未動用 Codex 額度。
