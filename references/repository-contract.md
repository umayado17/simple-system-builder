# GitHubリポジトリ契約

## 最小構成

新規プロジェクトでは次を初期値にする。技術スタックに合わないファイルは作らない。

```text
README.md

docs/
  requirements.md
  architecture.md
  data-ux.md
  complexity-boundaries.md
  enterprise-path.md
  operations.md
  decisions/

.chatdev/
  project-state.json
  autonomy-policy.json
  open-questions.md

.github/workflows/   # 技術スタック決定後に必要最小限を作る
```

コードのディレクトリは言語とフレームワークの標準へ従う。独自の多層ディレクトリを先に作らない。

## 文書の役割

- `requirements.md`: 目的、利用者、範囲、受入条件、制約を置く。
- `architecture.md`: 選んだ構成、最小十分である理由、主要境界を置く。
- `data-ux.md`: データ意味、主要操作、状態遷移、役割を置く。
- `complexity-boundaries.md`: 帳票、computer use、外部連携の隔離方法を置く。
- `enterprise-path.md`: 将来の導入条件と移行経路だけを置く。
- `operations.md`: 起動、テスト、デプロイ、復旧、ログ確認を置く。
- `decisions/`: 後で理由を失う重要判断だけを置く。

同じ説明を複数文書へ複製しない。小規模プロジェクトでは文書を統合してよい。

## プロジェクト状態

`.chatdev/project-state.json` をChat間の引継ぎに使う。最低限次を保つ。

- 現在フェーズ
- 現在タスク
- 次の行動
- 重要な承認済み基準線
- blocker
- 最終更新時刻

状態ファイルは実装の事実を上書きしない。コード、テスト、CI結果を確認してから更新する。

## 自律方針

`.chatdev/autonomy-policy.json` に、プロジェクト固有の自動実行範囲と人へ戻す範囲を置く。既存方針があればそれを優先する。

## 変更単位

- 一つの受入条件または一つの明確な改善ごとに変更する。
- コードだけでなく、該当するテストと文書を同じ変更に含める。
- 大規模な一括生成より、小さく検証可能な変更を選ぶ。
- 既存履歴、命名、ブランチ、PR方針を尊重する。

## 再開手順

既存プロジェクトを再開するときは次を読む。

1. `README.md`
2. `.chatdev/project-state.json`
3. `docs/requirements.md`
4. `docs/architecture.md`
5. 直近の変更とCI結果
6. `.chatdev/open-questions.md`

記録と実装が食い違う場合は、実装と実行結果を優先し、文書を修正する。
