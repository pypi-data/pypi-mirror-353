```feature_request.md
---
name: ✨ Feature Request / Improvement
about: 新機能の追加や既存機能の改善を提案する
title: "[Feature/Improvement] "
labels: "enhancement"
assignees: ""

---

## 機能概要
実装したい機能や改善の簡潔な説明

## 目的
この機能/改善が解決する問題や達成したい目標

## 詳細
- 具体的な変更内容や必要な手順
- 新しいAPIエンドポイント、CLIコマンド、バックエンド処理など、影響を受ける部分
- 必要なデータモデルやスキーマの変更
- 外部サービスとの連携方法
- 想定される入力、出力、エラーシナリオ
- （任意）画面イメージやUML図などの補足資料へのリンク

## 技術的考慮事項
- 使用するライブラリやフレームワーク
- 非同期処理、エラーハンドリング、リトライ、特定の設計パターンの要件
- パフォーマンス、スケーラビリティ、セキュリティに関する懸念
- 既存コードベースとの互換性

## テスト要件
- 必要なテストの層と種類（単体、統合、エッジケースなど）
- 特定のテストデータや環境セットアップが必要な場合

## 関連Issue/PR
- 関連する既存のissueやpull requestへのリンク

## TODOリスト（任意）
- 実装に必要なタスクの分解（実装者向けの具体的な指示として）
```

```bug_report.md
---
name: 🐛 Bug Report
about: 再現可能なバグや予期しない動作を報告する
title: "[Bug] "
labels: "bug"
assignees: ""

---

## 問題概要
発生した問題の簡潔な説明

## 再現手順
問題を再現するために必要な具体的な手順
1. ...
2. ...
3. ...

## 期待される動作
問題が発生した際に理想的に起こるべきこと

## 実際の動作
問題が発生した際に実際に起こること

## 環境
- OS: 
- Python version: 
- 関連ライブラリのバージョン: 
- devcontainer環境: 

## エラーメッセージ / ログ
発生したエラーメッセージや関連するログ出力
（必要に応じてコードブロックやファイルリンクで提供）

## 関連コード / 設定
問題に関連するコードファイルや設定ファイルのリンクや抜粋

## 技術的考慮事項（任意）
問題の原因や可能な解決策についての考察

## 関連Issue/PR
- 関連する既存のissueやpull requestへのリンク
```

```refactoring.md
---
name: 🧹 Refactoring / Technical Debt
about: コード構造、パフォーマンス、保守性の問題に対処する
title: "[Refactoring/Tech Debt] "
labels: "refactoring, tech-debt"
assignees: ""

---

## 問題
現在のコードに存在する問題（可読性の低さ、重複、非効率性、特定パターンからの逸脱など）

## 目的
このリファクタリング/技術的負債解決により改善されること（保守性、パフォーマンス、開発効率など）

## 提案する解決策
具体的な修正方法や新しい設計方針

## 対象範囲
- 影響を受けるファイル、モジュール、コンポーネント
- 機能的な変更があるかどうか

## 技術的考慮事項
- 既存機能やテストへの影響
- 外部サービスとの連携への影響
- 段階的なリファクタリングが必要かどうか

## テスト要件
- 既存テストの修正や新しいテストの追加が必要かどうか
- 特に注意すべきテスト観点（既存機能の回帰防止など）

## 関連Issue/PR
- このリファクタリングに関連するissueや、このリファクタリングで解決される他のissueへのリンク
```

```architecture_setup.md
---
name: 🏗️ Architecture Setup / New Application
about: 新しいアプリケーションのクリーンアーキテクチャ構造を作成する
title: "[Architecture] "
labels: "architecture, setup"
assignees: ""

---

## アプリケーション概要
作成する新しいアプリケーションの目的と機能

## アーキテクチャ構造
以下のクリーンアーキテクチャパターンに従って構造を作成：

```
{app_name}/
├── cmd/{feature}/run_{action}.py          # エントリーポイント
├── config/config.py                       # 設定クラス
├── di/injector.py                        # 依存性注入設定
├── domain/
│   ├── entities/{entity}.py              # ドメインエンティティ
│   ├── repositories/{repository}.py      # リポジトリインターフェース
│   └── services/{service}.py             # ドメインサービス
├── infrastructure/
│   ├── api/{client}.py                   # 外部API実装
│   ├── aws/{client}.py                   # AWS実装
│   └── persistence/{repository}.py       # データ永続化実装
├── usecases/{feature}/{action}_usecase.py # ユースケース
└── utils/
```

## 必要な設定
### 依存性注入設定
```python
# di/injector.py
class AppModule(Module):
    def configure(self, binder: Binder):
        # 新しいサービス/リポジトリのバインディング追加
        binder.bind({Interface}, to={Implementation}, scope=singleton)
        binder.bind({Usecase}, to={Usecase}, scope=singleton)
```

### 設定クラス
```python
# config/config.py
class {Service}Config:
    def __init__(self):
        # 本格実装時はos.environ["{ENV_VAR}"]またはpydanticを使用
        self.{property} = os.environ.get("{ENV_VAR}")
```

## 開発環境設定
devcontainer環境の構築：
```
.devcontainer/dc-{app_name}/
├── devcontainer.json    # VSCode設定
├── docker-compose.yml   # コンテナ構成
├── .env.example        # 環境変数テンプレート
└── initCommand.sh      # 初期化スクリプト
```

## 技術的考慮事項
- 各層の責務を明確に分離し、依存関係を適切に管理
- 命名規則の統一（ユースケース