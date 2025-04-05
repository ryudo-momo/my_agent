# <RM_AGENT_TOOL>
# Tool Name: gettime
# Description: 現在時刻を取得します。
# Input: None
# Output: 現在時刻
# </RM_AGENT_TOOL>

def gettime(arg):
    import datetime
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")