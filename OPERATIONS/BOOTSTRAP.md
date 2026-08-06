# 恒久指示の起動・分離・復旧手順

## 通常起動

将来のAI・自動化環境は、会話の記憶だけに依存せず次の順に読みます。

1. `AGENTS.md`
2. `OPERATIONS/DIRECTIVE_MANIFEST.json`
3. `OPERATIONS/CORE_DIRECTIVE.md` — ユーザー恒久指示の原文だけ
4. `OPERATIONS/DIRECTIVE_BOUNDARY.md` — 恒久指示とAI方針の境界
5. `OPERATIONS/ASSISTANT_OPERATING_POLICY.md` — AIが考えた可変方針
6. `state/current.json`
7. `state/budget_ledger.json`
8. `state/user_action_requests.json`
9. `OPERATIONS/AUTOMATION_BEFORE_USER_GATE.md`

その後、`python scripts/check_directive_integrity.py` を実行します。検査に合格するまで、収益・費用・公開・ユーザー操作依頼に影響する新規作業へ進みません。

## 厳格な切り分け

- `OPERATIONS/CORE_DIRECTIVE.md` の11項目だけがユーザー恒久指示です。
- AIが考えた解釈、法令・安全上の実装、予算計算、作業手順、終了条件、リポジトリ範囲は `OPERATIONS/ASSISTANT_OPERATING_POLICY.md` などへ置きます。
- 曖昧な会話では恒久指示を変更しません。
- ユーザーが恒久指示の変更であると明示した場合だけ、冗長コピーとマニフェストをまとめて更新します。

## 冗長化

ユーザー恒久指示だけを次の3形式で保持します。

- 正本: `OPERATIONS/CORE_DIRECTIVE.md`
- 同文ミラー: `OPERATIONS/CORE_DIRECTIVE_MIRROR.md`
- Base64バックアップ: `OPERATIONS/CORE_DIRECTIVE.b64`

`OPERATIONS/DIRECTIVE_MANIFEST.json` が版、11項目の原文、UTF-8バイト数、SHA-256、AI文言の混入禁止条件を保持します。

AI補助方針は別ファイルであり、恒久指示の冗長コピーには含めません。

## 自動復旧

- 3コピーのうち1つだけが欠落・破損し、残り2つがマニフェストの原文と一致する場合だけ、自動復旧します。
- 2つ以上が不一致の場合は、誤った多数決をせず、P0インシデントを作成して影響のある作業を停止します。
- 意図的な恒久指示変更は、正本、ミラー、Base64、マニフェスト、版番号、検証記録を同じ変更単位で更新します。
- AI補助方針の変更だけなら、恒久指示の版やハッシュは変更しません。

## 絶対保証できない範囲

「永久に絶対効かなくならない」という保証はできません。次では全層が停止し得ます。

- GitHubリポジトリの削除、所有権喪失、アカウント停止
- 接続権限の解除
- GitHub Actionsの無効化やサービス終了
- 正本・ミラー・バックアップ・マニフェスト・検査処理を同時に変更または削除
- 将来のAIがこのリポジトリへアクセスできず、起動ファイルも読まない

設計目標は、単一障害では消えず、AIが考えたものと混ざらず、異常を自動検出し、通常のAI開発環境で再発見・復旧できることです。
