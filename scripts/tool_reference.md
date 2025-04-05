★これはまだ実装してない

# ツールリファレンス

## list_agents

機能：
現在アクティブなエージェントの一覧を取得する。

書式：
<list_agents></list_agents>

戻り値：
<list_agents_result>{AGENT_NAME1},{AGENT_NAME2},...</list_agents_result>

## get_agent_profile

機能：
エージェントの概要を取得する。

書式：
<get_agent_profile>{AGENT_NAME}</get_agent_profile>

戻り値：
<get_agent_profile_result>{AGENT_PROFILE}</get_agent_profile_result>


## call_agent

機能：
他のエージェントに話しかける。

書式：
<call>{AGENT_NAME},{PROMPT}</call>

戻り値：
<call_result>{AGENT_RESPONSE}</call_result>


## add_task

機能：
他のエージェントまたはユーザーにタスクを与える。

書式：
<call>{NAME},{TASK}</call>
※{NAME}には、エージェント名またはユーザーIDを格納する。

戻り値：
<call_result>{AGENT_RESPONSE}</call_result>

## list_task

機能：
タスクリストを取得する。

書式：
<list_task></list_task>

戻り値：
<list_task_result>{NAME},{TASK}\n\n{NAME},{TASK}\n\n{NAME},{TASK}\n\n...</clist_task_result>

