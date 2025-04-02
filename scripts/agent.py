import requests
import json
import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

class ChatAgent:
    """
    OpenRouterのAPIを使用してAIとマルチターンの会話を行うクラス
    """
    
    def __init__(self, model="google/gemini-2.0-flash-lite-001"):
        """
        ChatAgentクラスのコンストラクタ
        
        Args:
            model (str): 使用するAIモデルの名前
        """
        self.model = model
        self.conversation_history = []  # 会話履歴を保存するリスト
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        
    def chat(self, message):
        """
        ユーザーメッセージを送信し、AIからの応答を取得するメソッド
        
        Args:
            message (str): ユーザーからのメッセージ
            
        Returns:
            str: AIからの応答メッセージ
        """
        # ユーザーメッセージを会話履歴に追加
        self.conversation_history.append({"role": "user", "content": message})
        
        # APIリクエストを送信し、応答を取得
        response = self._send_api_request()
        
        # 応答を返す
        return response
        
    def _send_api_request(self):
        """
        OpenRouterのAPIにリクエストを送信する内部メソッド
        
        Returns:
            str: AIからの応答メッセージ
        """
        # APIキーのチェック
        if not self.api_key or self.api_key == "your_openrouter_api_key":
            return "エラー: OpenRouterのAPIキーが設定されていません。.envファイルを確認してください。"
        
        try:
            # APIリクエストを送信
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": "http://localhost",  # ローカル開発用
                    "X-Title": "ChatAgent",  # アプリケーション名
                },
                data=json.dumps({
                    "model": self.model,
                    "messages": self.conversation_history
                })
            )
            
            # レスポンスをJSONとして解析
            response_data = response.json()
            
            # レスポンスからAIの応答を抽出
            if "choices" in response_data and len(response_data["choices"]) > 0:
                ai_message = response_data["choices"][0]["message"]["content"]
                # AIの応答を会話履歴に追加
                self.conversation_history.append({"role": "assistant", "content": ai_message})
                return ai_message
            else:
                return f"エラー: 予期しないレスポンス形式です。\n{json.dumps(response_data, indent=2, ensure_ascii=False)}"
                
        except Exception as e:
            return f"エラー: APIリクエスト中に問題が発生しました。\n{str(e)}"
            
    def reset_conversation(self):
        """
        会話履歴をリセットするメソッド
        """
        self.conversation_history = []

class ContextAwareAgent(ChatAgent):
    """
    ChatAgentを拡張し、会話履歴を圧縮する機能とシステムプロンプトを使用する機能を持つクラス
    """
    
    def __init__(self, model="google/gemini-2.0-flash-lite-001", system_prompt_path=None):
        """
        ContextAwareAgentクラスのコンストラクタ
        
        Args:
            model (str): 使用するAIモデルの名前
            system_prompt_path (str, optional): システムプロンプトファイルのパス。デフォルトはNone（システムプロンプトなし）
        """
        super().__init__(model)
        self.summary = None  # 会話の要約を保存する変数
        self.system_prompt = None  # システムプロンプトを保存する変数
        
        # システムプロンプトファイルが指定されている場合、読み込む
        if system_prompt_path:
            self._load_system_prompt(system_prompt_path)
    
    def _load_system_prompt(self, file_path):
        """
        指定されたファイルからシステムプロンプトを読み込むメソッド
        
        Args:
            file_path (str): システムプロンプトファイルのパス
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    self.system_prompt = content
                    # 会話履歴の先頭にシステムプロンプトを追加
                    if not self.conversation_history or self.conversation_history[0].get("role") != "system":
                        self.conversation_history.insert(0, {"role": "system", "content": self.system_prompt})
                else:
                    print(f"警告: システムプロンプトファイル '{file_path}' は空です。")
        except FileNotFoundError:
            print(f"警告: システムプロンプトファイル '{file_path}' が見つかりません。")
        except Exception as e:
            print(f"警告: システムプロンプトファイルの読み込み中にエラーが発生しました: {str(e)}")
    
    def reset_conversation(self):
        """
        会話履歴をリセットするメソッド
        システムプロンプトは保持する
        """
        self.conversation_history = []
        # システムプロンプトがある場合は再追加
        if self.system_prompt:
            self.conversation_history.append({"role": "system", "content": self.system_prompt})
    
    def cleanup(self, target_length):
        """
        会話履歴を圧縮するメソッド
        要約後、会話履歴をリセットし、要約を元に新しい会話を開始します
        
        Args:
            target_length (int): 要約の目標文字数
            
        Returns:
            str: 生成された要約文
        """
        # 会話履歴が空の場合は何もしない
        if not self.conversation_history:
            return None
            
        # システムプロンプトを除外した会話履歴を取得
        conversation_to_summarize = [msg for msg in self.conversation_history if msg.get("role") != "system"]
        if not conversation_to_summarize:
            return None
            
        # 新たなChatAgentインスタンスを作成
        summarizer = ChatAgent(self.model)
        
        # 会話履歴を文字列化
        conversation_text = ""
        for message in conversation_to_summarize:
            role = "ユーザー" if message["role"] == "user" else "AI"
            conversation_text += f"{role}: {message['content']}\n\n"
        
        # 要約指示のプロンプト
        prompt = f"""
以下の会話を{target_length}文字程度に要約してください。
要約は、会話の重要なポイントを含み、文脈を理解できるものにしてください。
私の発言とあなたの発言が明確に区別できるような要約文にしてください。

会話：
{conversation_text}

要約文字数: {target_length}文字程度
"""
        
        # 要約を依頼
        summary = summarizer.chat(prompt)
        
        # 文字数をチェック
        while abs(len(summary) - target_length) / target_length > 0.3:
            # 誤差が30%以上ある場合は修正を依頼
            adjustment_prompt = f"""
先ほどの要約の文字数は{len(summary)}文字でした。
目標は{target_length}文字です。
{'より短く' if len(summary) > target_length else 'より詳細に'}要約し直してください。

元の要約：
{summary}
"""
            summary = summarizer.chat(adjustment_prompt)
        
        # 要約を保存
        self.summary = summary
        
        # 会話履歴をリセット（システムプロンプトは保持される）
        self.reset_conversation()
        
        return summary
    
    def chat(self, message):
        """
        ユーザーメッセージを送信し、AIからの応答を取得するメソッド
        要約がある場合は、要約を含むプロンプトを使用
        
        Args:
            message (str): ユーザーからのメッセージ
            
        Returns:
            str: AIからの応答メッセージ
        """
        # 要約がある場合は、要約を含むプロンプトを作成
        if self.summary:
            enhanced_message = f"これまでの会話の概要：{self.summary}\n\nメッセージ：{message}"
            return super().chat(enhanced_message)
        else:
            # 要約がない場合は通常のchatメソッドを使用
            return super().chat(message)

# テスト用コード（直接実行された場合のみ実行）
if __name__ == "__main__":
    import argparse
    
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description='AIチャットエージェント')
    parser.add_argument('--agent', choices=['chat', 'context'], default='context',
                      help='使用するエージェントタイプ (デフォルト: context)')
    parser.add_argument('--model', default='google/gemini-2.0-flash-lite-001',
                      help='使用するAIモデル (デフォルト: google/gemini-2.0-flash-lite-001)')
    parser.add_argument('--system-prompt', dest='system_prompt_path',
                      help='システムプロンプトファイルのパス')
    
    args = parser.parse_args()
    
    # 選択されたエージェントタイプに基づいてインスタンスを作成
    if args.agent == 'chat':
        agent = ChatAgent(model=args.model)
        agent_name = "ChatAgent"
    else:  # context
        agent = ContextAwareAgent(model=args.model, system_prompt_path=args.system_prompt_path)
        agent_name = "ContextAwareAgent"
    
    # 使用方法を表示
    print(f"=== {agent_name} ===")
    print("使用方法:")
    print("- メッセージを入力するとAIに送信されます")
    if args.agent == 'context':
        print("- 'summary [文字数]' と入力すると会話を要約します（例: 'summary 100'）")
    print("- 'exit' と入力すると終了します")
    print("====================\n")
    
    # システムプロンプトの情報を表示（ContextAwareAgentの場合）
    if args.agent == 'context' and args.system_prompt_path:
        if agent.system_prompt:
            print(f"システムプロンプトを読み込みました: {args.system_prompt_path}")
        else:
            print(f"警告: システムプロンプトを読み込めませんでした: {args.system_prompt_path}")
    
    # インタラクティブループ
    while True:
        try:
            user_input = input("ユーザー: ")
            
            # 終了コマンド
            if user_input.lower() == "exit":
                print("プログラムを終了します")
                break
                
            # 要約コマンド（ContextAwareAgentの場合のみ）
            elif user_input.lower().startswith("summary") and args.agent == 'context':
                parts = user_input.split()
                target_length = 100  # デフォルト値
                
                # 文字数が指定されている場合
                if len(parts) > 1 and parts[1].isdigit():
                    target_length = int(parts[1])
                    
                print(f"\n=== 会話履歴の圧縮（目標: {target_length}文字） ===")
                summary = agent.cleanup(target_length)
                
                if summary:
                    print(f"会話要約 ({len(summary)}文字):\n{summary}\n")
                    print("会話履歴をリセットしました。要約を元に会話を継続します。")
                else:
                    print("要約するための会話履歴がありません。")
                    
            # 通常のメッセージ
            else:
                response = agent.chat(user_input)
                print(f"AI: {response}\n")
                
        except KeyboardInterrupt:
            print("\nプログラムを終了します")
            break
        except Exception as e:
            print(f"エラーが発生しました: {str(e)}")
