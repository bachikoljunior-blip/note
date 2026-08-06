# note 収益化・自動化リポジトリ

この非公開リポジトリは、note販売と収益化作業を継続運用・改善するための正本です。

## 恒久指示の切り分け

- `OPERATIONS/CORE_DIRECTIVE.md`: ユーザーが指定した恒久指示11項目の原文だけ
- `OPERATIONS/DIRECTIVE_BOUNDARY.md`: ユーザー恒久指示、AI補助方針、外部の上位制約の境界
- `OPERATIONS/ASSISTANT_OPERATING_POLICY.md`: AIが考えた可変方針。恒久指示ではない
- `OPERATIONS/DIRECTIVE_MANIFEST.json`: 原文、版、SHA-256、バイト数、切り分け条件

AIが考えた目的、予算解釈、安全策、終了条件、リポジトリ範囲、作業手順は、恒久指示の原文へ混ぜません。

## 現在の販売ページ

- 商品: 量産に見せないAI雑学Shorts｜100企画＋台本・分析テンプレ【スマホ対応】
- 公開URL: https://note.com/mobile_ai_studio/n/n779329665155
- 初回価格: 1,480円
- 状態: 公開済み・外部検証済み（HTTP 200、記事ID・発行者ID・タイトル・価格表示を確認）

## 追加販売チャネル

- BOOTH: 日本語ZIP、出品文、商品画像3枚、iPhone向けランチャーまで検証済み。本人認証を伴う最終公開待ち
- Gumroad: 英語版ZIP、英語出品文、USD 12価格案、横長カバー3枚、正方形サムネイル1枚、iPhone向け統合ランチャーまで検証済み。本人認証を伴う最終公開待ち
- 英語版商品とGumroadパックはPR #15、主要CI run `31122408743` の全工程成功後にmainへマージ済み

## 自動化

- push・PR・毎日の定期実行時に、恒久指示の原文とAI方針の切り分けを検査
- 恒久指示を正本、同文ミラー、Base64バックアップの3形式で保持
- 1コピーだけの破損は、残り2コピーが原文と一致する場合に限って自動復旧
- 複数不一致やAI文言混入時は、P0 Issueを作成して影響のある処理を停止
- 公開noteページを毎日取得し、URL・記事ID・発行者ID・タイトル・価格表示の破損を検知
- 購入者用商品ZIPと無料サンプルZIPを再生成し、バイト数・SHA-256・ZIP内件数・破損を検証
- 計測値を `data/metrics.csv` に入れると改善レポートを自動生成
- 公開後48時間・7日の時点で、計測依頼Issueを自動作成
- 期限判定は主要CI内でも検査し、Issue作成ワークフローは定期・手動実行に分離
- ユーザーへ操作を依頼する前に、直接実行・公式API・GitHub Actions・共有・一括化・自動検証を評価
- 自動化評価のない操作依頼と、理由のない多手順をCIで拒否

認証、本人確認、決済契約、外部アカウントでの最終公開など、本人固有の権限が必要な操作は無断で実行しません。認証情報やCookieは保存しません。

## 予算

- ChatGPT月額30,000円は基礎費用として扱い、収益がない期間もユーザーが支払う前提
- 追加費用は、原則として実現済み収益から同期間のChatGPT基礎費用と確定費用を差し引いた範囲
- 現在の計算正本: `state/budget_ledger.json`

この予算計算はAIの可変運用方針であり、ユーザー恒久指示の原文とは別管理です。

## リポジトリ操作の範囲

この `bachikoljunior-blip/note` は、本作業用として変更可能です。その他の既存リポジトリは、個別の明示的許可なしに変更しません。

## 開始地点

- `AGENTS.md`: AI向け強制起動順序
- `OPERATIONS/BOOTSTRAP.md`: 起動・切り分け・復旧手順
- `OPERATIONS/CORE_DIRECTIVE.md`: ユーザー恒久指示の原文
- `OPERATIONS/ASSISTANT_OPERATING_POLICY.md`: AI補助運用方針
- `OPERATIONS/AUTOMATION_BEFORE_USER_GATE.md`: 操作依頼前の自動化評価
- `state/current.json`: 現在地と次の作業
- `state/budget_ledger.json`: 収益と使用可能費用
- `state/user_action_requests.json`: 操作ごとの自動化評価と残存手数
- `.github/workflows/`: 検査、監視、復旧、計測の自動化

初期自動化の構築日: 2026-08-06
