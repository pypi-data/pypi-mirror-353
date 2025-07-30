# Sercher - Grok Web検索ツール

GrokのAPIを使用してWeb検索を実行するコマンドラインツールです。

## インストール

### PyPI からインストール（推奨）
```bash
pip install sercher
```

### ソースからインストール
```bash
git clone https://github.com/sugarkwork/sercher.git
cd sercher
pip install -e .
```

## セットアップ

1. XAI APIキーを取得：
   - [XAI Console](https://console.x.ai/) でアカウントを作成
   - APIキーを生成

2. 環境変数を設定：
   ```bash
   # .envファイルを作成（.env.exampleを参考に）
   cp .env.example .env
   # .envファイルを編集してAPIキーを設定
   ```

   または環境変数として直接設定：
   ```bash
   export XAI_API_KEY=your_api_key_here
   ```

## 使用方法

### 基本的な使用方法
```bash
sercher "検索キーワード"
```

### モジュール形式で実行
```bash
python -m sercher "検索キーワード"
```

## オプション

- `-v, --verbose`: 詳細な出力を表示
- `-h, --help`: ヘルプメッセージを表示

## 使用例

```bash
# 基本的な検索
sercher "フランスの首都は何ですか？"

# 詳細出力付き
sercher -v "最新のAI技術について教えて"

# モジュール形式で実行
python -m sercher "今日の天気は？"
```

## 開発者向け

### パッケージのビルド
```bash
python -m build
```

### PyPI へのアップロード
```bash
python -m twine upload dist/*
```

## ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照してください。

## 貢献

プルリクエストやイシューの報告を歓迎します。
