import os
import sys
import tkinter as tk
from tkinter import messagebox
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# スコープを設定
SCOPES = ['https://www.googleapis.com/auth/tasks']

def authenticate():
    """Google APIへの認証を行います"""
    flow = InstalledAppFlow.from_client_secrets_file(
        'C:/Users/bxuhe/OneDrive/デスクトップ/mywork_programing/client_secret_658272432022-fh4e1c2gr330omjss4t61e1fvgd1g10d.apps.googleusercontent.com.json'
        ,SCOPES)
    creds = flow.run_local_server(port=0)
    return creds

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
        service.tasks().insert(tasklist=task_list_id, body={"title": task}).execute()

def process_tasks_from_file(file_path):
    """ファイルからリスト名とタスクを処理します"""
    task_data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split()
                    list_name = parts[0]  # リスト名
                    tasks = parts[1:]    # タスク
                    task_data.append((list_name, tasks))
    except FileNotFoundError:
        messagebox.showerror("エラー", f"指定されたファイルが見つかりません: {file_path}")
    except Exception as e:
        messagebox.showerror("エラー", f"ファイル読み込み中にエラーが発生しました: {e}")
    return task_data

def execute_task(file_path):
    """指定されたタスクリストファイルを処理"""
    try:
        credentials = authenticate()
        tasks_data = process_tasks_from_file(file_path)
        for list_name, tasks in tasks_data:
            add_tasks(credentials, list_name, tasks)
        messagebox.showinfo("成功", f"タスクを追加しました: {file_path}")
    except Exception as e:
        messagebox.showerror("エラー", f"タスク処理中にエラーが発生しました: {e}")

def create_gui():
    """GUIを作成"""
    root = tk.Tk()
    root.title("Google Tasks 自動追加")
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
