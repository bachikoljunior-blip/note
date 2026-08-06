# note 収益化・自動化リポジトリ

この非公開リポジトリは、note販売を**無料枠中心で継続運用・改善するための正本**です。

## 現在の販売ページ

- 商品: 量産に見せないAI雑学Shorts｜100企画＋台本・分析テンプレ【スマホ対応】
- 公開URL: https://note.com/mobile_ai_studio/n/n779329665155
- 初回価格: 1,480円
- 状態: 公開済み・外部検証済み（HTTP 200、記事ID・発行者ID・タイトル・価格表示を確認）

## 自動化

- push・PR・毎日の定期実行時に設定・本文・状態・計測表を自動検証
- 公開noteページを毎日取得し、URL・記事ID・発行者ID・タイトル・価格表示の破損を検知
- 購入者用商品ZIPと無料サンプルZIPをprivateリポジトリから再生成し、バイト数・SHA-256・ZIP内件数・破損を検証
- 計測値を `data/metrics.csv` に入れると改善レポートを自動生成
- 公開後48時間・7日の時点で、計測依頼Issueを自動作成
- 恒久指示、判断記録、次の作業を会話外にも保持
- **ユーザーへ操作を依頼する前に、直接実行・公式API・GitHub Actions・共有シート・一括化・自動検証を必ず評価**
- 自動化評価のない操作依頼、3手を超える未説明の本人操作をCIで拒否
- 告知文、商品URL、共有シート、コピー切替、共有時刻を1画面へまとめた0円の共有ランチャーを自動生成

認証、本人確認、決済契約、noteの最終公開は自動化対象外です。認証情報やCookieは保存しません。

## リポジトリ操作の範囲

この `bachikoljunior-blip/note` は、ユーザーが本作業用として明示的に作成したため変更可能です。その他の既存リポジトリは、個別の明示的許可なしに変更しません。

## 開始地点

- `OPERATIONS/CORE_DIRECTIVE.md`: 恒久方針
- `OPERATIONS/AUTOMATION_BEFORE_USER_GATE.md`: 操作依頼前に必ず行う自動化評価
- `state/current.json`: 現在地と次の作業
- `state/user_action_requests.json`: 操作ごとの自動化評価と残存手数
- `config/campaign.json`: 商品・価格・公開URLの正本
- `config/distribution.json`: 告知文と共有設定の正本
- `artifacts/manifest.json`: 商品ZIPと無料サンプルの正本・検証値
- `scripts/check_user_action_gate.py`: 自動化評価漏れを拒否する検査
- `scripts/build_share_launcher.py`: 0円共有ランチャー生成
- `data/metrics.csv`: 公開後の数値
- `reports/latest.md`: 数値から生成される改善案
- `.github/workflows/`: 無料自動化

初期自動化の構築日: 2026-08-06
