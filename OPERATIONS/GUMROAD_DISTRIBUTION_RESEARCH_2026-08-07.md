# Gumroad英語版の流入獲得パック実装判断

## 目的

英語商品、出品文、商品画像が揃った後の最大の未完了である「英語圏から商品ページへ流入を作る導線」を、商品URL公開前から準備する。公開後はiPhoneでGumroadの公開URLを最初に1回入力し、媒体・訴求別UTM、英語告知文、事前入力または共有シート、試行記録を自動生成する。

## 公式情報の確認

- Gumroadは商品ごとに共有用の一意なURLを作成し、商品管理画面からコピーできる。
  - https://gumroad.com/help/article/136-find-your-products-url
  - https://gumroad.com/help/article/149-adding-a-product
- Bluesky公式のcompose intentは、ログイン済みユーザーの投稿画面へ本文を事前入力するが、投稿自体は本人確認が必要である。上限は300 Unicode grapheme clustersと説明されている。
  - https://docs.bsky.app/docs/advanced-guides/intent-links
- Redditは反復的または未承諾の大量行為をspamとして禁止し、販売促進の扱いはコミュニティごとに異なる。
  - https://support.reddithelp.com/hc/en-us/articles/360043504051-Spam
  - https://support.reddithelp.com/hc/en-us/articles/28012014962580-How-do-I-keep-spam-out-of-my-community
- 確認日: 2026-08-07

## チャネル判断

- v1の自動対象はX、Bluesky、同意済みメール、iPhone共有シートとする。
- Xは既存のリポジトリで検証済みのWeb Intent形式を再利用し、動かない場合は一括コピーへ戻せるようにする。
- Blueskyは公式compose intentを使う。
- メールは受信を合理的に期待する相手だけに限定し、コールドDMや一括送信を禁止する。
- 共有シートで選んだ実アプリは取得できないため、LinkedIn等を選んだと推測せず、UTM sourceを`share_sheet`とする。
- Redditはコミュニティ文脈と規則の個別確認なしに同文投稿を自動化しない。v1の自動対象から除外する。
- LinkedIn本文の安定した事前入力に依存せず、必要な場合は共有シートまたはコピーを使う。

## 実装

- 正本: `config/gumroad_distribution.json`
- 生成: `scripts/build_gumroad_distribution_pack.py`
- 出力:
  - `dist/gumroad_distribution_launcher.html`
  - `dist/gumroad_distribution_pack.json`
  - `dist/gumroad_distribution_pack.md`
  - `reports/gumroad_distribution_pack.json`
- 商品URLは公開前の正規状態として`null`にし、認証済み公開後にランチャーへ入力する。
- URLの解決順は、将来の埋込済みURL、`product_url` query、端末内保存、未設定の順とする。
- HTTPS、gumroad.comまたはサブドメイン、公開商品形式の`/l/<slug>`、userinfoなしを検査し、`app.gumroad.com`の管理画面URL、help URL、他ドメインを拒否する。
- localStorageが使えない場合もセッション内保持とURL設定済みランチャーリンクで代替する。
- 4経路×3訴求=12組み合わせを生成し、既存UTMだけを置換して他queryとfragmentを保持する。
- 告知文を編集した場合は`utm_content`へ`_edited`を付け、元の訴求と同一と偽らない。
- 共有試行は経路・訴求・実際に生成した計測URLを履歴として保持し、間に別の投稿を挟んでも24時間以内の同一経路・同一訴求には重複警告を出す。
- Blueskyは実際の本文とUTM付きURLを合算し、公式上限を超える場合は事前入力を停止して短縮を求める。
- Clipboard APIと従来コピーの両方が失敗しても、選択可能な「共有用全文」欄からUTM付きURLごと長押しコピーできる。
- 保存するのは公開商品URLと共有試行だけで、パスワード、Cookie、投稿権限、宛先は保存しない。

## 検証

- config ID、default、組み合わせ数、訴求文字数、禁止表現、商品事実を検査する。
- 合成Gumroad URLを使い、12組み合わせすべてでUTMが1回だけ入り、既存の非UTM queryとfragmentが残ることを検査する。
- `state/current.json`の英語商品100 topics、12 formats、9 prompts、USD 12と突合する。
- 出品説明の非保証文と主要数量を突合する。
- ランチャーのURL保存、UTM、重複警告、Web Share、試行記録、`noopener`を検査する。
- distのHTML、JSON、Markdownには生成時刻を入れず、同じ入力から同じSHA-256を再生成できるようにする。

## 本人操作と費用

- 商品公開後の初回URL入力: 1回。URLが将来configへ反映されれば不要になる。
- 各媒体での最終公開: 1回。アカウント本人の意思と権限が必要。
- 自動投稿、無差別送信、公開成功の虚偽記録は行わない。
- 追加費用: 0円
- 外部依存: 0件
