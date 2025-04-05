import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

# 同じディレクトリ内のモジュールをインポート
from agent import ContextAwareAgent
from tool_router import get_tool_list, call_tool

class Manager:
    """
    AIエージェントとの会話を管理し、ツールの呼び出しを処理するクラス
    
    このクラスは以下の機能を提供します：
    1. ユーザーからのメッセージを受け取る
    2. メッセージをエージェントに送信する
    3. エージェントからの応答を受け取る
    4. エージェントからの返答にツールタグが含まれている場合、ツールを呼び出す
    5. ツールの結果をエージェントに送信する
    6. エージェントからの応答に<<END>>が含まれていたら、会話を終了する
    """
    
    def __init__(self, model: str = "google/gemini-2.5-pro-preview-03-25"):
        """
        Managerクラスのコンストラクタ
        
        Args:
            model (str): 使用するAIモデルの名前
        """
        # システムプロンプトの準備
        system_prompt_path = os.path.join(os.path.dirname(__file__), 'system_prompt.txt')
        self.system_prompt = self._prepare_system_prompt(system_prompt_path)
        
        # エージェントの初期化（システムプロンプトを直接渡す）
        self.agent = ContextAwareAgent(model=model, system_prompt=self.system_prompt)
    
    def _prepare_system_prompt(self, system_prompt_path: str) -> str:
        """
        システムプロンプトを準備するメソッド
        
        Args:
            system_prompt_path (str): システムプロンプトファイルのパス
            
        Returns:
            str: 準備されたシステムプロンプト
        """
        try:
            # システムプロンプトファイルを読み込む
            with open(system_prompt_path, 'r', encoding='utf-8') as f:
                base_prompt = f.read().strip()
        except FileNotFoundError:
            print(f"エラー: システムプロンプトファイル '{system_prompt_path}' が見つかりません。")
            sys.exit(1)
        except Exception as e:
            print(f"エラー: システムプロンプトファイルの読み込み中にエラーが発生しました: {str(e)}")
            sys.exit(1)
        
        # ツールリストを取得
        tool_list = get_tool_list()
        
        # システムプロンプトとツールリストを結合
        return f"{base_prompt}\n\n{tool_list}"
    
    def extract_tool_calls(self, message: str) -> List[Tuple[str, str, str]]:
        """
        メッセージからツール呼び出しを抽出するメソッド
        
        Args:
            message (str): エージェントからのメッセージ
            
        Returns:
            List[Tuple[str, str, str]]: 抽出されたツール呼び出しのリスト（ツール名, 引数, サブツール名）
                                       サブツールが指定されていない場合、サブツール名はNone
        """
        # 通常のツール呼び出しのパターン: <ツール名>引数</ツール名>
        standard_pattern = r'<([a-zA-Z0-9_]+)>(.*?)</\1>'
        standard_matches = re.findall(standard_pattern, message, re.DOTALL)
        
        # サブツール呼び出しのパターン: <ツール名.サブツール名>引数</ツール名.サブツール名>
        subtool_pattern = r'<([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)>(.*?)</\1\.\2>'
        subtool_matches = re.findall(subtool_pattern, message, re.DOTALL)
        
        # 結果を統合
        result = []
        # 通常のツール呼び出し: (ツール名, 引数, None)
        for tool_name, arg in standard_matches:
            result.append((tool_name, arg, None))
        
        # サブツール呼び出し: (ツール名, 引数, サブツール名)
        for tool_name, subtool_name, arg in subtool_matches:
            result.append((tool_name, arg, subtool_name))
        
        return result
    
    # process_messageメソッドは削除（run内で直接処理するように変更）
    
    def run(self):
        """
        会話ループを実行するメソッド
        """
        print("=" * 80)
        print("AIエージェントとの会話を開始します")
        print("終了するには 'exit' と入力してください")
        print("=" * 80)
        
        try:
            # ユーザー入力を受け取る（最初の1回だけ）
            user_input = input("\nユーザー: ")
            
            # 終了コマンド
            if user_input.lower() == "exit":
                print("会話を終了します")
                return
            
            # 現在のメッセージ（最初はユーザー入力、その後はツール実行結果）
            current_message = user_input
            
            while True:
                # エージェントにメッセージを送信
                agent_response = self.agent.chat(current_message)
                print(f"\nAI: {agent_response}")
                
                # <<END>>タグがあるか確認
                if "<<END>>" in agent_response:
                    agent_response = agent_response.replace("<<END>>", "")
                    print("AIが会話を終了しました")
                    break
                
                # ツール呼び出しを抽出
                tool_calls = self.extract_tool_calls(agent_response)
                
                # ツール呼び出しがない場合はユーザーに入力を求める
                if not tool_calls:
                    user_input = input("\nユーザー: ")
                    
                    # 終了コマンド
                    if user_input.lower() == "exit":
                        print("会話を終了します")
                        break
                    
                    # ユーザー入力を現在のメッセージとして設定
                    current_message = user_input
                    continue
                
                # ツール呼び出しがある場合
                tool_all_result = ""
                for tool_name, arg, subtool_name in tool_calls:
                    # ツールを呼び出し、結果を取得
                    result = call_tool(tool_name, arg, subtool_name)
                    
                    # ログ出力
                    if subtool_name:
                        print(f"[ツール実行: {tool_name}.{subtool_name}]")
                    else:
                        print(f"[ツール実行: {tool_name}]")
                    print(f"[ツール結果: {result}]")

                    # 結果をフォーマット
                    if subtool_name:
                        tool_all_result += f"<{tool_name}.{subtool_name}_result>{result}</{tool_name}.{subtool_name}_result>"
                    else:
                        tool_all_result += f"<{tool_name}_result>{result}</{tool_name}_result>"
                
                # ツール結果をフォーマット
                current_message = tool_all_result
                
        except KeyboardInterrupt:
            print("\n会話を中断します")
        except Exception as e:
            print(f"\nエラーが発生しました: {str(e)}")


# テスト用コード（直接実行された場合のみ実行）
if __name__ == "__main__":
    # マネージャーを作成
    manager = Manager()
    
    # 会話ループを実行
    manager.run()
