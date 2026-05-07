# comfyui-image-judge

ComfyUI で生成した画像を OK / NG で人手判定し、データセット作成を支援するカスタムノードです。

> Status: **v0.1 alpha** — 保存ノード `SaveForJudge` と判定 Web UI が動作します。LoRA / kohya_ss 用の特殊エクスポート機能は今のところ実装していません (OK 画像はメタデータ付きの素のフォルダに集まります)。

## 主な機能

### 保存ノード `SaveForJudge`

ComfyUI ワークフローの末尾に挿入すると、生成画像を「判定待ち」フォルダに保存します。

- **入力**: `IMAGE` テンソル + `dataset_name` + (任意) `caption` / `trigger_word`
- **保存内容** (1 枚あたり 3 ファイル):
  - `<stem>.png` — PNG。`prompt` と `workflow` を `tEXt` チャンクに埋め込み済み (= ComfyUI のキャンバスにドラッグ & ドロップで当時のワークフローを完全復元)
  - `<stem>.txt` — kohya 互換のキャプション (`trigger_word, caption` 形式)
  - `<stem>.json` — 判定状態を含むメタデータ (`judgment` / `judged_at` / `comment` / `ng_reason`)
- **ファイル名 (stem)**: `YYYYMMDD_HHMMSS_NNN` でタイムスタンプ + 連番

### 判定 Web UI

ComfyUI 起動中、ブラウザで **`http://127.0.0.1:8188/imagejudge/ui`** を別タブで開くと判定画面が出ます。ComfyUI 画面右下の緑色 **「Image Judge」** ボタンからも起動できます。

操作:

| キー | 動作 |
|---|---|
| `O` | OK 判定 |
| `1` | NG: キャラ違い |
| `2` | NG: 技術破綻 |
| `3` | NG: ポーズ/構図不適 |
| `4` | NG: 演出不適 |
| `5` | NG: 衣装/小物不適 |
| `6` | NG: その他 |
| `7` | NG: 問題外 |
| `←` `→` | 前/次の画像 |

判定するとファイル trio (`png` / `txt` / `json`) が自動で `pending/` から `ok/` または `ng/` に移動します。

#### Single モード (デフォルト)

dataset を 1 つ選び、その `pending` / `ok` / `ng` のいずれかをフィルタしてキューを表示します。`ok` 一覧で `1-7` を押すと `ng/<理由>` に付け直し、`ng` 一覧で `O` を押すと `ok/` に戻せます (再判定)。

#### All (集約) モード

全 dataset の `pending` を 1 つのキューにまとめて表示します。ヘッダーの「集約先」入力欄に dataset 名を入れて (新規でも可)、`O` または `1-7` で判定すると、判定後のファイル trio は **すべて集約先 dataset の `ok/` `ng/`** に集まります。

> 「複数のワークフロー名で散らばってしまった画像を、判定時に 1 つの dataset に整理する」用途を想定しています。

## 出力レイアウト

```
output/judge/<dataset_name>/
  pending/
    20260507_143022_001.png
    20260507_143022_001.txt
    20260507_143022_001.json   { "judgment": "pending", ... }
  ok/
    20260507_140000_005.png
    20260507_140000_005.txt
    20260507_140000_005.json   { "judgment": "ok", "comment": "...", ... }
  ng/
    20260507_141500_002.png
    20260507_141500_002.txt
    20260507_141500_002.json   { "judgment": "ng", "ng_reason": "技術破綻", ... }
```

OK 画像は `output/judge/<dataset>/ok/` に PNG + キャプション + メタデータの 3 ファイル trio で集まります。学習に使うときはここをそのまま読むか、必要なフォーマットに加工してください (kohya_ss 形式への変換は別途スクリプトでどうぞ)。

## インストール

### git clone (現状)

```bash
cd <ComfyUI のパス>/custom_nodes
git clone https://github.com/o-ankomochi-o/comfyui-image-judge.git
```

ComfyUI を再起動するとノード一覧の **ImageJudge** カテゴリに `Save for Judge` が追加されます。

依存は `Pillow` と `numpy` のみで、これらは ComfyUI が既に持っているため追加 `pip install` は通常不要です。

### ComfyUI Manager

(ComfyUI Registry 登録後に対応予定)

## 開発

このプロジェクトは TDD で開発しています。詳しい運用方針は `CLAUDE.md` を参照してください (リポジトリ管理外、ローカルのみ)。

```bash
uv sync                 # 依存をセットアップ
uv run pytest           # 23 件のユニットテスト
```

純粋ロジックは `core.py` に閉じてあり、`tests/test_core.py` から ComfyUI 非依存で網羅的にテストしています。ComfyUI 連携部 (`nodes.py`、aiohttp ルート) は ComfyUI 実環境での手動確認が必要です。

## ライセンス

MIT — see [LICENSE](LICENSE).
