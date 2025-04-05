# <RM_AGENT_TOOL>
# Tool Name: myname
# Description: エージェントの自分の名前を保持します。
# Subtools:
#   - myname: 通常の名前を返します
#   - anothername: 別名義を返します
# Input: None
# Output: エージェントの名前
# </RM_AGENT_TOOL>

def myname(arg):
    """
    エージェントの名前「えーじぇんと」を返します
    """
    return "えーじぇんと"

def anothername(arg):
    """
    エージェントの別名義「遠藤英治」を返します
    """
    return "遠藤英治"
