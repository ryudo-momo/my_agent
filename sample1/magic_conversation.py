#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
魔法エンジニアリングに関する市民向け科学講座の会話シミュレーション

このスクリプトは、ContextAwareAgentを使用して、
講師役と中学生役の2つのエージェントを作成し、
魔法エンジニアリングという架空の技術に関する会話をシミュレートします。
"""

import os
import sys
import time
import re
from pathlib import Path

# 親ディレクトリをパスに追加して、scriptsフォルダのモジュールをインポートできるようにする
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

# ContextAwareAgentクラスをインポート
from scripts.agent import ContextAwareAgent

def main():
    """
    メイン関数：市民向け科学講座での講師と中学生の会話をシミュレートします
    """
    print("=" * 80)
    print("魔法エンジニアリングに関する市民向け科学講座の会話シミュレーション")
    print("=" * 80)
    print("\n会話を開始します...\n")

    # 現在のディレクトリパスを取得
    current_dir = Path(__file__).parent
    
    # システムプロンプトファイルのパスを設定
    professor_prompt_path = current_dir / "professor_prompt.txt"
    student_prompt_path = current_dir / "student_prompt.txt"
    
    # エージェントの作成
    teacher = ContextAwareAgent(
        model="google/gemini-2.0-flash-lite-001",
        system_prompt_path=professor_prompt_path
    )
    
    student = ContextAwareAgent(
        model="google/gemini-2.0-flash-lite-001",
        system_prompt_path=student_prompt_path
    )
    
    # 会話の初期メッセージ（中学生からの最初の質問）
    initial_question = "先生、魔法エンジニアリングって何ですか？アニメで見た魔法と同じものなんですか？"
    
    # 会話ログを保存するリスト
    conversation_log = []
    
    # 現在の話者と次の話者を設定
    current_speaker = "中学生"
    current_message = initial_question
    
    # 会話のターン数
    max_turns = 20
    turn_count = 0
    
    try:
        # 会話ループ
        while turn_count < max_turns:
            # 現在のメッセージを表示
            print(f"\n{current_speaker}: {current_message}")
            conversation_log.append(f"{current_speaker}: {current_message}")
            
            # 次の話者とエージェントを設定
            if current_speaker == "中学生":
                next_speaker = "先生"
                next_agent = teacher
            else:
                next_speaker = "中学生"
                next_agent = student
            
            # 次のエージェントに現在のメッセージを送信し、応答を取得
            print(f"\n{next_speaker}が考えています...")
            response = next_agent.chat(current_message)
            
            # <end>タグがあるか確認
            end_tag_match = re.search(r'<end>$', response)
            if end_tag_match:
                # <end>タグを削除
                response = re.sub(r'<end>$', '', response)
                # 次のターンの準備
                current_speaker = next_speaker
                current_message = response
                # 現在のメッセージを表示
                print(f"\n{current_speaker}: {current_message}")
                conversation_log.append(f"{current_speaker}: {current_message}")
                # 会話を終了
                print("\n会話が自然に終了しました。")
                break
            
            # 次のターンの準備
            current_speaker = next_speaker
            current_message = response
            turn_count += 1
            
            # 少し待機して、会話の流れを自然にする
            time.sleep(1)
        
        # 最大ターン数に達した場合のメッセージ
        if turn_count >= max_turns:
            print("\n" + "=" * 80)
            print(f"会話は{max_turns}ターンに達したため終了しました。")
        
    except KeyboardInterrupt:
        # Ctrl+Cで会話を中断した場合
        print("\n\n会話が中断されました。")
    
    except Exception as e:
        # その他のエラーが発生した場合
        print(f"\n\nエラーが発生しました: {str(e)}")
    
    finally:
        # 会話ログの保存
        print("\n" + "=" * 80)
        print("会話ログ:")
        for message in conversation_log:
            print(message)
        
        # 会話ログをファイルに保存
        log_file_path = current_dir / "conversation_log.txt"
        with open(log_file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(conversation_log))
        
        print("\n" + "=" * 80)
        print(f"会話ログは {log_file_path} に保存されました。")

if __name__ == "__main__":
    main()
