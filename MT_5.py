import os
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import tkinter as tk
from tkinter import messagebox

"""
calculate_priority関数:

キーワード（「急ぎ」や「重要」など）に基づいて優先度スコアを加算します。
タスク内に「締切」というキーワードがある場合、締め切り日を解析してさらにスコアを追加します。
sort_tasks_by_priority関数:

calculate_priorityを使用してタスクの優先度を計算し、優先度が高い順にタスクを並べ替えます。
GUI:

Tkinterを使用してファイル選択、実行開始ボタンを設置します。
ユーザーが選択したファイルのタスク内容を読み込み、優先度を計算し、Google Tasksに追加します。
"""

# スコープを設定
SCOPES = ['https://www.googleapis.com/auth/tasks']

# Google API認証
def authenticate():
    """Google APIへの認証を行います"""
    flow = InstalledAppFlow.from_client_secrets_file(
        'path_to_your_client_secret.json', SCOPES)
    creds = flow.run_local_server(port=0)
    return creds

# タスクをGoogle Tasksに追加
def add_tasks(creds, task_list_name, tasks):
    """タスクをGoogle Tasksに追加します"""
    service = build('tasks', 'v1', credentials=creds)

    # タスクリストを取得または作成
    task_lists = service.tasklists().list().execute().get('items', [])
    task_list_id = None
    for task_list in task_lists:
        if task_list['title'] == task_list_name:
            task_list_id = task_list['id']
            break
    if not task_list_id:
        task_list = service.tasklists().insert(body={"title": task_list_name}).execute()
        task_list_id = task_list['id']

    # タスクを追加
    for task in tasks:
        service.tasks().insert(tasklist=task_list_id, body={"title": task["title"]}).execute()

# 優先順位計算関数
def calculate_priority(task_text):
    """タスクの優先順位を計算します"""
    priority_score = 0
    
    # キーワードでスコア付け
    if "急ぎ" in task_text or "締切" in task_text:
        priority_score += 10
    if "重要" in task_text:
        priority_score += 5
    
    # 締切が記載されている場合、緊急度を計算
    if "締切" in task_text:
        deadline_text = task_text.split("締切")[1].strip()
        try:
            deadline_date = datetime.strptime(deadline_text, "%Y/%m/%d")
            days_to_deadline = (deadline_date - datetime.now()).days
            if days_to_deadline < 3:  # 締切まで3日未満なら高優先度
                priority_score += 20
        except ValueError:
            pass
    return priority_score

# 優先順位でタスクを並べ替える関数
def sort_tasks_by_priority(tasks):
    """優先順位に基づいてタスクを並べ替えます"""
    return sorted(tasks, key=lambda task: calculate_priority(task["title"]), reverse=True)

# タスクファイルの処理
def process_tasks_from_file(file_path):
    """ファイルからタスクを処理します"""
    task_data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split()  # 1つ目がリスト名、残りがタスク内容
                    list_name = parts[0]
                    tasks = [{"title": " ".join(parts[1:])}]
                    task_data.append((list_name, tasks))
    except FileNotFoundError:
        messagebox.showerror("エラー", f"指定されたファイルが見つかりません: {file_path}")
    except Exception as e:
        messagebox.showerror("エラー", f"ファイル読み込み中にエラーが発生しました: {e}")
    return task_data

# タスク実行
def execute_task(file_path):
    """指定されたタスクリストファイルを処理"""
    try:
        credentials = authenticate()
        tasks_data = process_tasks_from_file(file_path)
        for list_name, tasks in tasks_data:
            sorted_tasks = sort_tasks_by_priority(tasks)
            add_tasks(credentials, list_name, sorted_tasks)
        messagebox.showinfo("成功", f"タスクを追加しました: {file_path}")
    except Exception as e:
        messagebox.showerror("エラー", f"タスク処理中にエラーが発生しました: {e}")

# GUIを作成
def create_gui():
    """GUIを作成"""
    root = tk.Tk()
    root.title("Google Tasks 優先順位追加")
    root.geometry("400x300")

    # タイトル
    label = tk.Label(root, text="タスクファイルを選択して実行開始", font=("Arial", 14))
    label.pack(pady=10)

    # ファイルボタンを配置
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    # 実行開始ボタン
    def execute_selected_file():
        if selected_file.get():
            execute_task(selected_file.get())
        else:
            messagebox.showwarning("警告", "タスクファイルを選択してください")

    # ファイル選択用変数
    selected_file = tk.StringVar()

    # .txtファイルのボタン生成
    files = [f for f in os.listdir('.') if f.endswith('.txt')]
    for file in files:
        def on_click(f=file):
            selected_file.set(f)
            messagebox.showinfo("ファイル選択", f"選択中のファイル: {f}")
        file_button = tk.Button(button_frame, text=file, command=on_click, width=30)
        file_button.pack(pady=5)

    # 実行ボタン
    execute_button = tk.Button(root, text="実行開始", command=execute_selected_file, bg="green", fg="white")
    execute_button.pack(pady=20)

    root.mainloop()

if __name__ == '__main__':
    create_gui()
