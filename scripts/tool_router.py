import os
import re
import importlib.util
import sys

tools = []

def get_tool_list():
    # toolsフォルダのファイルリストを取得する
    tools_dir = os.path.join(os.path.dirname(__file__), 'tools')
    files = os.listdir(tools_dir)
    
    # 拡張子が.pyのファイルのみをフィルタリング
    py_files = [f for f in files if f.endswith('.py')]
    
    tool_descriptions = []
    
    # フォルダ内のpyファイルを開く
    for py_file in py_files:
        file_path = os.path.join(tools_dir, py_file)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # <RM_AGENT_TOOL>～</RM_AGENT_TOOL> の部分を取得する
            pattern = r'<RM_AGENT_TOOL>(.*?)</RM_AGENT_TOOL>'
            matches = re.findall(pattern, content, re.DOTALL)
            
            if matches:
                tool_descriptions.append(matches[0])
    
    # 取得したツール説明を１つの文字列に結合して返す
    return '\n'.join(tool_descriptions)

def call_tool(tool_name, arg, subtool=None):
    """
    指定されたツール名に対応するツールを呼び出し、引数を渡して結果を返す関数
    
    Args:
        tool_name (str): 呼び出すツールのファイル名
        arg: ツールに渡す引数
        subtool (str, optional): 呼び出すサブツール名。デフォルトはNone（tool_nameと同じ関数を呼び出す）
        
    Returns:
        ツールの実行結果
        
    Raises:
        ImportError: ツールが見つからない場合
        AttributeError: ツール内に指定された関数が見つからない場合
        Exception: ツールの実行中にエラーが発生した場合
    """
    try:
        # ツールのパスを構築
        tools_dir = os.path.join(os.path.dirname(__file__), 'tools')
        module_path = os.path.join(tools_dir, f"{tool_name}.py")
        
        # モジュールが存在するか確認
        if not os.path.exists(module_path):
            raise ImportError(f"ツール '{tool_name}' が見つかりません")
        
        # モジュールを動的にインポート
        spec = importlib.util.spec_from_file_location(tool_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # サブツールが指定されていない場合は、tool_nameと同じ関数を呼び出す
        function_name = subtool if subtool else tool_name
        
        # ツール関数を取得
        if not hasattr(module, function_name):
            raise AttributeError(f"ツール '{tool_name}' に関数 '{function_name}' が見つかりません")
        
        tool_function = getattr(module, function_name)
        
        # ツール関数を実行
        return tool_function(arg)
        
    except ImportError as e:
        return f"エラー: {str(e)}"
    except AttributeError as e:
        return f"エラー: {str(e)}"
    except Exception as e:
        return f"エラー: ツール '{tool_name}' の実行中にエラーが発生しました: {str(e)}"

if __name__ == "__main__":
    time_str = call_tool('gettime', None)
    print(time_str)
