# 恒久指示の起動・復旧手順

## 通常起動

将来のAI・自動化環境は、会話の記憶に依存せず次の順に読みます。

1. `AGENTS.md`
2. `OPERATIONS/DIRECTIVE_MANIFEST.json`
3. `OPERATIONS/CORE_DIRECTIVE.md`
4. `state/current.json`
5. `state/user_action_requests.json`
6. `OPERATIONS/AUTOMATION_BEFORE_USER_GATE.md`

その後、`python scripts/check_directive_integrity.py` を実行します。検査に合格するまで、収益・公開・ユーザー操作依頼に影響する新規作業へ進みません。

## 冗長化

恒久指示は次の3形式で保持します。

- 正本: `OPERATIONS/CORE_DIRECTIVE.md`
- 同文ミラー: `OPERATIONS/CORE_DIRECTIVE_MIRROR.md`
- Base64バックアップ: `OPERATIONS/CORE_DIRECTIVE.b64`

`OPERATIONS/DIRECTIVE_MANIFEST.json` が、版、UTF-8バイト数、SHA-256、必須文言を保持します。

## 自動復旧

- 3コピーのうち1つだけが欠落・破損し、残り2つがマニフェストと一致する場合、自動復旧可能です。
- 2つ以上が不一致の場合は、誤った多数決をせず、作業を閉じてP0インシデントを作成します。
- 意図的に指示を更新する場合、正本、ミラー、Base64、マニフェスト、版番号、検証記録を同一PRで更新します。

## 絶対保証できない範囲

「永久に絶対失われない」という保証はできません。次では全層が停止し得ます。

- GitHubリポジトリ自体の削除、所有権喪失、アカウント停止
- 接続権限の解除
- GitHub Actionsの無効化やサービス終了
- 正本・ミラー・バックアップ・検査処理を同時に変更または削除
- 将来のAIがこのリポジトリを参照できず、起動ファイルも読まない

このため設計目標は「永久保証」ではなく、単一障害では消えず、異常を自動検出し、通常のAI開発環境で再発見・復旧できる状態です。
