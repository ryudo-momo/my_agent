# <RM_AGENT_TOOL>
# Tool Name: ask_user
# Description: ユーザーに質問や会話をするためのツールです。
# Input: ユーザーに対する質問の文
# Output: ユーザーからの回答
# </RM_AGENT_TOOL>

def ask_user(arg):
    """
    ユーザーに質問や会話をするためのツール関数
    
    Args:
        arg (str): 質問や会話の内容
        
    Returns:
        str: 入力された質問や会話の内容をそのまま返します
    """

    # ユーザーからの入力をそのまま返す
    ret = input(arg + "\n")

    return ret
