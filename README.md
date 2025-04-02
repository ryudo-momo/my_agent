# 🤖 AIチャットエージェント

OpenRouter APIを使用して様々なAIモデルと簡単に会話できるPythonプログラムです。

## 📋 主な特徴

- ✅ **簡単な会話機能**: 数行のコードでAIとの会話を実現
- ✅ **会話履歴の管理**: 複数回のやり取りを記憶して文脈を維持
- ✅ **会話の要約機能**: 長い会話を自動的に要約して記憶容量を節約
- ✅ **システムプロンプト対応**: ファイルからシステムプロンプトを読み込んでAIの振る舞いを制御
- ✅ **複数のAIモデル対応**: OpenRouterを通じて様々なAIモデルを利用可能

## 🔧 セットアップ方法

### 1. 必要なパッケージのインストール

```bash
pip install requests python-dotenv
```

### 2. OpenRouter APIキーの取得

1. [OpenRouter](https://openrouter.ai/)にアクセスしてアカウントを作成
2. ダッシュボードからAPIキーを発行
3. コピーしたAPIキーを`.env`ファイルに設定

### 3. 環境変数の設定

プロジェクトのルートディレクトリに`.env`ファイルを作成し、以下の内容を記述：

```
OPENROUTER_API_KEY=あなたのOpenRouterAPIキー
```

> ⚠️ **注意**: APIキーは秘密情報です。GitHubなどに公開しないでください。

## 🧩 主要クラスと機能

### ChatAgent

基本的な会話機能を提供するクラスです。

```python
from scripts.agent import ChatAgent

# エージェントの作成
agent = ChatAgent()

# 会話の実行
response = agent.chat("Pythonについて教えてください")
print(f"AI: {response}")
```

### ContextAwareAgent

ChatAgentを拡張し、システムプロンプトの読み込みと会話要約の機能を持つクラスです。

```python
from scripts.agent import ContextAwareAgent

# システムプロンプトファイルを指定してエージェントを作成
agent = ContextAwareAgent(system_prompt_path="scripts/system_prompt.txt")

# 会話の実行
response = agent.chat("「は」と「が」の違いを教えてください")
print(f"AI: {response}")

# 会話を要約
summary = agent.cleanup(150)
print(f"会話要約: {summary}")

# 要約を踏まえた上で会話を継続（システムプロンプトは維持される）
agent.chat("助詞「に」と「へ」の違いは？")
```

## 🚀 コマンドラインでの使用方法

プログラムを直接実行すると、インタラクティブモードで会話できます：

```bash
# デフォルト（ContextAwareAgent、システムプロンプトなし）
python scripts/agent.py

# ChatAgentを使用
python scripts/agent.py --agent chat

# ContextAwareAgentを使用し、システムプロンプトファイルを指定
python scripts/agent.py --agent context --system-prompt scripts/system_prompt.txt

# 別のAIモデルを指定
python scripts/agent.py --model openai/gpt-4o
```

### コマンドライン引数

| 引数 | 説明 | デフォルト値 |
|------|------|------------|
| `--agent` | 使用するエージェントタイプ（chat, context） | context |
| `--model` | 使用するAIモデル | google/gemini-2.0-flash-lite-001 |
| `--system-prompt` | システムプロンプトファイルのパス | なし |

### インタラクティブコマンド

- 通常のテキスト: AIに送信されるメッセージ
- `summary [文字数]`: 会話を指定文字数に要約（例: `summary 100`）
- `exit`: プログラムを終了

## 📝 システムプロンプトの作成

システムプロンプトは、AIの振る舞いや応答スタイルを制御するための指示文です。テキストファイルに記述し、ContextAwareAgentのコンストラクタで指定します。

### 例：日本語教師としてのシステムプロンプト

```
あなたは親切な日本語教師です。簡潔に、わかりやすく回答してください。
専門用語を使う場合は、必ず解説を加えてください。
例えば、文法について質問された場合は、具体例を挙げて説明してください。
```

### 例：プログラミング講師としてのシステムプロンプト

```
あなたは経験豊富なプログラミング講師です。
コードの例を示す際は、必ず詳細なコメントを付けてください。
初心者にもわかりやすく、ステップバイステップで説明してください。
```

## 📄 ライセンス

MITライセンス
