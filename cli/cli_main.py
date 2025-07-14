#!/usr/bin/env python3
import os
import sys
import readline
import random
import copy # <- 変数コピー機能に必要
from typing import TypeAlias, Any
from collections.abc import Callable
# from core.ai.analysis # このライブラリは使われていないためコメントアウト

# コマンドハンドラの型エイリアス
CommandHandler: TypeAlias = Callable[[list[str]], bool | None]
from core.database



class EnhancedCLI:
    """実用的な機能とデバッグ機能を統合したCLIクラス"""
    
    def __init__(self):
        """コンストラクタ"""
        self.mode: str = "ANA"
        self.current_path = "home/"
        self.debug_mode: bool = False # 補完のデバッグモード用フラグ

        # 利用可能なコマンドを定義
        self.commands: dict[str, CommandHandler] = {
            # --- 実用コマンド ---
            "help": self.show_help,
            "mode": self.change_mode,
            "check": self.check_status,
            "set": self.set_variable,
            "vars": self.show_variables,
            "copy": self.copy_variable,
            "exit": self.exit_cli,
            "end": self.exit_cli,
            # --- デバッグ用コマンド ---
            "debug": self.manage_debug,
            "test": self.test_completion,
            
        }
        
        # ユーザーが利用できる変数を格納
        self.variables: dict[str, Any] = {
            'greeting': 'hello world',
            'numbers': [10, 20, 30]
        }

        # readlineの自動補完を設定
        self.setup_autocomplete()

    # --- 自動補完とデバッグ関連 (DebugCLIから統合・改造) ---

    def setup_autocomplete(self):
        """readlineの自動補完機能を設定する"""
        try:
            # 補完時の区切り文字を設定（スペース、タブ、改行）
            readline.set_completer_delims(' \t\n')
            # 補完関数としてself.completerを登録
            readline.set_completer(self.completer)
            # Tabキーで補完が実行されるようにバインド
            readline.parse_and_bind("tab: complete")
            # 大文字・小文字を区別せずに補完
            readline.parse_and_bind('set completion-ignore-case on')
        except Exception as e:
            print(f"警告: 自動補完の設定中にエラーが発生しました: {e}")

    def completer(self, text, state):
        """Readline用の補完関数"""
        line = readline.get_line_buffer()

        # デバッグモードが有効な場合、現在の状態を出力
        if self.debug_mode:
            print(f"\n[DEBUG] line: '{line}', text: '{text}', state: {state}")
        
        # 入力行をスペースで分割
        parts = line.lstrip().split()
        
        # 補完候補を格納するリスト
        options = []
        
        # コマンド名（最初の単語）を補完する場合
        if len(parts) == 0 or (len(parts) == 1 and not line.endswith(' ')):
            options = [cmd for cmd in self.commands.keys() if cmd.startswith(text)]
        
        # (将来の拡張用) 特定のコマンドの引数を補完する場合
        # elif parts[0] == 'set' and len(parts) == 2:
        #     options = [var for var in self.variables.keys() if var.startswith(text)]

        # デバッグモードが有効な場合、候補リストを出力
        if self.debug_mode:
            print(f"[DEBUG] options: {options}")

        # state番目の候補を返す
        if state < len(options):
            return options[state]
        else:
            return None

    # --- コマンドハンドラ ---

    def show_help(self, _args) -> None:
        """利用可能なコマンドのヘルプを表示する"""
        print("利用可能なコマンド:")
        for cmd in sorted(self.commands.keys()):
            print(f"  {cmd}")
    
    def change_mode(self, args: list[str]) -> None:
        """動作モードを変更する"""
        if args:
            self.mode = args[0].upper()
            print(f"モードを {self.mode} に変更しました")
        else:
            print(f"現在のモード: {self.mode}")
    
    def check_status(self, _args) -> None:
        """システムの簡単な状態をチェックする"""
        print("システム状態: OK")
    
    def set_variable(self, args: list[str]) -> None:
        """変数を設定する。例: set my_var 123"""
        if len(args) < 2:
            print("使い方: set <変数名> <値>")
            return
        
        var_name = args[0]
        value_str = " ".join(args[1:])
        try:
            # 注意: evalは便利ですが、信頼できない入力を扱う場合はセキュリティリスクがあります
            value = eval(value_str, {"__builtins__": {}}, self.variables)
            self.variables[var_name] = value
            print(f"変数 '{var_name}' に値を設定しました。型: {type(value).__name__}")
        except Exception as e:
            # evalが失敗した場合、文字列として扱う
            self.variables[var_name] = value_str
            print(f"変数 '{var_name}' に文字列として値を設定しました。")


    def show_variables(self, _args) -> None:
        """保存されている変数を一覧表示する"""
        if not self.variables:
            print("変数は設定されていません。")
            return
        
        print("--- 変数一覧 ---")
        for name, value in self.variables.items():
            print(f"  {name} ({type(value).__name__}): {value!r}")
        print("----------------")

    def copy_variable(self, args: list[str]) -> None:
        """変数をシャローコピーする。例: copy source_var new_var"""
        if len(args) != 2:
            print("使い方: copy <コピー元変数> <新しい変数名>")
            return
        
        source_name, dest_name = args
        if source_name not in self.variables:
            print(f"エラー: 変数 '{source_name}' が見つかりません。")
            return
            
        self.variables[dest_name] = copy.copy(self.variables[source_name])
        print(f"変数 '{source_name}' を '{dest_name}' にコピーしました。")

    def manage_debug(self, args: list[str]) -> None:
        """デバッグモードの管理やreadline設定の表示を行う"""
        if not args:
            print("--- readline デバッグ情報 ---")
            print(f"補完のデバッグモード: {'ON' if self.debug_mode else 'OFF'}")
            print(f"Completer delims: '{readline.get_completer_delims()}'")
            print(f"Completer function: {readline.get_completer()}")
            print("\nヒント: 'debug on' または 'debug off' で補完情報の表示を切り替えられます。")
            return

        if args[0].lower() == 'on':
            self.debug_mode = True
            print("補完のデバッグモードを ON にしました。")
        elif args[0].lower() == 'off':
            self.debug_mode = False
            print("補完のデバッグモードを OFF にしました。")
        else:
            print(f"不明な引数: {args[0]}。 'on' または 'off' を指定してください。")

    def test_completion(self, _args) -> None:
        """補完機能の簡単なテスト手順を表示する"""
        print("--- 補完機能テスト ---")
        print("以下を試してください:")
        print("1. 'm' と入力してTabキーを押す -> 'mode' に補完されるはずです。")
        print("2. 'c' と入力してTabキーを押す -> 'check', 'copy' が候補に出るはずです。")
        print("3. 何も入力せずにTabキーを2回押す -> 全コマンドが表示されるはずです。")
        print("4. 'debug on' を実行後、再度補完を試してみてください。")

    def exit_cli(self, _args) -> bool:
        """CLIを終了する"""
        thx_list = ["Thank you for your service! We look forward to serving you again.","We hope you enjoyed the CLI. Please try us again next time!","Thank you for using our service! We hope this CLI has helped you in your work.","See you again! I wish you a great experience with this CLI.","Thank you for your service! We look forward to seeing you next time!","Thank you for using the CLI! We hope you enjoy the new features!","We welcome your feedback and look forward to hearing from you! We hope to see you again next time!","We hope this CLI has made your work more efficient!","Thank you very much for your service! We hope to see you again next time!","Thank you very much for using our CLI!","We look forward to working with you again! Have a great day!","We hope this CLI will be useful for your project!","Thank you for using our service! We look forward to seeing you next time!","We hope that your work will be smoother through the CLI!","Thank you for using our service! Please try again next time!","We hope your work becomes more efficient with this CLI!","Thank you for using our service! We hope to see you again next time!""Thank you for using this CLI!","We hope this CLI has met your needs!","Thank you for using our service! We look forward to seeing you again next time!","Thank you from the bottom of our hearts for using the CLI! We hope to see you again!"]
        print(thx_list[random.randint(0, len(thx_list) - 1)])

        
        return True
    
    # --- コマンド処理のコア部分 ---

    def parse_command(self, command_line: str) -> tuple[str | None, list[str]]:
        """入力された一行をコマンドと引数に分割する"""
        if not command_line.strip():
            return None, []
        
        parts = command_line.strip().split()
        command = parts[0].lower()
        args = parts[1:]
        return command, args
    
    def execute_command(self, command: str, args: list[str]) -> bool | None:
        """コマンド名に基づいて対応するメソッドを実行する"""
        if command in self.commands:
            return self.commands[command](args)
        else:
            print(f"コマンド '{command}' が見つかりません")
            # --- ここでコマンド候補を提示 ---
            suggestions = [cmd for cmd in self.commands.keys() if cmd.startswith(command)]
            if suggestions:
                print(f"もしかして: {', '.join(suggestions)}")
            return False
    
    def run(self):
        """CLIアプリケーションのメインループ"""
        print("\n=== 統合CLI (Tabキーで自動補完) ===")
        print("'help'でコマンド一覧、'exit'で終了します。")
        
        while True:
            try:
                prompt = f"[{self.mode}] {self.current_path} > "
                user_input = input(prompt)
                
                command, args = self.parse_command(user_input)
                if command is None:
                    continue
                
                if self.execute_command(command, args):
                    break # Trueが返されたらループを抜けて終了
                    
            except KeyboardInterrupt:
                print("\n終了します。")
                break
            except EOFError:
                print("\n終了します。")
                break
            except Exception as e:
                print(f"予期せぬエラーが発生しました: {e}")

def main():
    cli = EnhancedCLI()
    cli.run()

if __name__ == "__main__":
    main()