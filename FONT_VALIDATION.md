# 字型專項修正與驗收紀錄 — v1.1

## 修正範圍與資料保全

本版僅修正字型語言分流、加入官方姓名對照欄位、增設驗收工具。`AGENTS.md`、`rules/` 三份規範、`wiki/`、`slides-content/`、每張投影片的標題、內容、數據、評級、版型及配色 **全部保持 v1.0 原樣**。

## 修正內容

1. 日本漢字姓名共 30 位：`name_lang` 由 `zh-TW` 改為 `ja`；四位拉丁字母姓名保留 `en`。
2. 依 NPB 2026 年兩隊官方球員名單，比對 30 位日本球員的正式姓名寫法。`name` 一律保留 Wiki 的原字串，新欄位 `official_name_ja` 記錄官方寫法，不直接覆蓋畫面或原文。
3. 有兩筆原文字形差異：
   - `p003`：原文 `西川遙輝`；NPB 官方 `西川遥輝`。
   - `p024`：原文 `山川穗高`；NPB 官方 `山川穂高`。
   因本輪只處理字型，原文字串不改寫；在資料中以 `source_name_variant: true` 明確標記。即使日文字型正確，兩筆畫面上仍顯示原文異體字，**不得稱為與官方日文寫法完全一致**。
4. 在中文句子、投影片標題與說明中，若出現清冊已核對的**完整日文姓名**，前端依完整名字串分段套用 `lang="ja"`，而非以漢字區塊或國籍猜測。原本句子與文字內容不變。
5. 改用 CSS `:lang(ja)`、`:lang(en)`、`:lang(zh-TW)` 規則，以涵蓋相應語言及地區化標記；英文頁面標籤補足 `lang="en"`。
6. 提供 `tests/font-check.html` 本機用字型範例，並新增 `scripts/validate_font_routing.py` 防止姓名語言標記回退。

## 查證來源（僅供姓名字形比對）

- [NPB 北海道日本ハムファイターズ 2026 選手一覧](https://npb.jp/bis/teams/rst_f.html)
- [NPB 福岡ソフトバンクホークス 2026 選手一覧](https://npb.jp/bis/teams/rst_h.html)

NPB 官方球員名單可核實姓名字形，但**不代表這份示範賽事的比賽記錄已重新由官方驗證**。

## 環境驗收狀態

| 項目 | 狀態 | 說明 |
|---|---|---|
| 日文姓名語言資料 | 已通過程式檢查 | 30 位 `ja`、4 位 `en`，原始 `name` 不變 |
| 三組 CSS 字型宣告與語言分流 | 已通過程式檢查 | 不代表目標字型已安裝 |
| Linux Chromium 截圖呈現指定字型 | **未通過** | 測試環境缺少 DFKai-SB 及 UD Digi Kyokasho N-R，無法由網頁程式憑空補齊 |
| Windows Chrome 指定字型（v1.1） | **使用者回報通過** | 使用者已在 Windows Chrome 確認三種指定字型正確顯示；v1.2 標題分段仍需另外抽查 |
| 其他裝置 | **未執行** | 可按規範採備援字型，但不得聲稱完全一致 |

## Windows Chrome 人工驗收流程（不使用 Codex）

1. 將 `tests/font-check.html` 用 Chrome 直接開啟（此診斷檔不放在 `docs/` 發布目錄）。
2. 按 **F12 → Elements**，使用選取工具點選每一組示例字元。
3. 切換 **Computed**，展開底部的 **Rendered Fonts**；檢查中文是否 `DFKai-SB`、英數是否 `Times New Roman`、日文是否 `UD Digi Kyokasho N-R`（實際顯示可能使用介面化別名）。
4. 若字型名稱不符，先確認 Windows 有安裝該字型及 Chrome 已重新啟動；不要把未取得散布授權的字型檔複製到專案。
5. 使用正常 HTTP 伺服器開啟 `http://localhost:8000/`，再對首頁標題、球員清冊中的姓名與英文名字進行相同檢查。
6. 將每類字型記錄為通過／未通過／未執行，確認後才可宣稱完成字型驗收。

## 本機驗證命令

```powershell
py scripts/validate_project.py
py scripts/validate_font_routing.py
py -m http.server 8000 --directory docs
```

## v1.2 增補：標題與姓氏語言分流

- 原 v1.1 只依清冊中的**完整日文姓名**標記 `lang="ja"`；標題包含「野村」「水野」「山縣」「鈴木」「松本」等簡稱時可能落回中文字型。
- v1.2 在 35 頁 `slides.json` 中加入 `title_segments`，以人工核對的 `player_id` 連結簡稱，保留所有 `title` 原字串。`scripts/validate_font_routing.py` 同時檢查關鍵標題與前端程式是否有依分段輸出。
- 使用者先前的 v1.1 Windows Chrome 全域字型驗收已通過；本次新增的**標題層級實際顯示**還需使用者在 Windows Chrome 針對第 14、16、28、30 頁確認。
- 本機 Chrome 以 F12 檢查標題姓名元素 `span[lang="ja"]` 的 Rendered Fonts；英文姓名則看 `span[lang="en"]`。若缺少目標字型，請回報未通過，不應將 Linux 備援字型判定為驗收成功。
