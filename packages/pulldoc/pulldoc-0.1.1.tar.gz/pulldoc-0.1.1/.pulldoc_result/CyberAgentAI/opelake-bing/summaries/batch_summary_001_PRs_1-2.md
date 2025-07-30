## 修正パターンの抽出

### 1. クリーンアーキテクチャの導入パターン

**発生する修正:**
- 新しいアプリケーションにクリーンアーキテクチャを適用する際の基本構造作成

**修正テンプレート:**
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

**具体的なファイルパス例:**
- `requester/cmd/access_token/run_main.py`
- `requester/domain/repositories/queue_repository.py`
- `requester/infrastructure/api/bing_client.py`
- `requester/usecases/access_token/fetch_access_token_usecase.py`

### 2. 依存性注入パターン

**発生する修正:**
- 新しいサービスやリポジトリを追加する際のDI設定更新

**修正テンプレート:**
```python
# di/injector.py
class AppModule(Module):
    def configure(self, binder: Binder):
        # 新しいサービス/リポジトリのバインディング追加
        binder.bind({Interface}, to={Implementation}, scope=singleton)
        binder.bind({Usecase}, to={Usecase}, scope=singleton)
```

### 3. 開発環境設定パターン

**発生する修正:**
- 新しいアプリケーション用のdevcontainer環境構築

**修正テンプレート:**
```
.devcontainer/dc-{app_name}/
├── devcontainer.json    # VSCode設定
├── docker-compose.yml   # コンテナ構成
├── .env.example        # 環境変数テンプレート
└── initCommand.sh      # 初期化スクリプト
```

### 4. 設定管理パターン

**発生する修正:**
- 外部サービス連携時の設定クラス追加

**修正テンプレート:**
```python
# config/config.py
class {Service}Config:
    def __init__(self):
        self.{property} = os.environ.get("{ENV_VAR}", "default_value")
```

## チームが注意すべきポイント

### 1. 環境変数の管理
- レビューコメントで指摘されているように、`default_value`は実際の運用では適切でない
- 本格実装時は`os.environ["{ENV_VAR}"]`でエラーを出すか、pydanticを使用することを検討

### 2. devcontainer設定の統合
- 現在は複数のdevcontainer設定が存在するが、将来的にはdocker-compose版に統一予定
- 開発効率を重視してRedis環境を含む構成を採用

### 3. アーキテクチャの一貫性
- 各層の責務を明確に分離し、依存関係を適切に管理
- 新機能追加時も同じパターンに従って実装する

### 4. 命名規則の統一
- ユースケースクラスで同名クラスが複数ある場合は適切にエイリアスを使用
- ファイル構造とクラス名の一貫性を保つ