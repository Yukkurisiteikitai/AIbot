#!/usr/bin/env python3
import os
import sys
import readline # <- 1. readlineをインポート
from typing import TypeAlias, Any
from collections.abc import Callable

# handler
CommandHandler: TypeAlias = Callable[[list[str]], bool | None]


class InteractiveCLI: # クラス名をより一般的なものに変更
    def __init__(self):
        self.mode: str = "ANA"
        self.current_path = "home/"
        self.commands:dict[str, CommandHandler] = {
            "help": self.show_help,
            "mode": self.change_mode,
            "check": self.check_status,
            # 'complete' と 'c' はTab補完の代替なので、コメントアウトまたは削除しても良い
            # "complete": self.manual_complete, 
            # "c": self.manual_complete,
            # "complete":self.completer,
            "exit": self.exit_cli,
            "end": self.exit_cli,
            "set": self.set_variable,
            "vars": self.show_variables,
            "copy": self.copy_variable,
        }
        
        self.variables: dict[str, Any] = {
            'greeting': 'hello world',
            'numbers': [10, 20, 30]
        }
    
    # --- 2. Tabキー補完のための関数を追加 ---
    def completer(self, text, state):
        """Readline用の補完関数"""
        # 現在の入力行全体を取得
        line = readline.get_line_buffer()
        
        # 入力行をスペースで分割
        parts = line.lstrip().split()
        
        # 補完候補を格納するリスト
        options = []
        
        # コマンド名（最初の単語）を補完する場合
        # (入力が空 or 最初の単語を入力中の場合)
        if len(parts) == 0 or (len(parts) == 1 and not line.endswith(' ')):
            # 現在入力中の単語(text)で始まるコマンドを候補とする
            options = [cmd for cmd in self.commands.keys() if cmd.startswith(text)]
        
        # 将来的に引数の補完を追加する場合はここにelif文を追加する
        # elif parts[0] == 'mode' and len(parts) == 2:
        #     modes = ['ANA', 'DEV', 'PROD']
        #     options = [m for m in modes if m.startswith(text.upper())]

        # state番目の候補を返す
        if state < len(options):
            return options[state]
        else:
            return None

    def show_help(self, args=None) -> None:
        """ヘルプを表示"""
        print("利用可能なコマンド:")
        # 短縮形 'c' を除外して表示
        for cmd in sorted([c for c in self.commands.keys() if len(c) > 1]):
             print(f"  {cmd}")
    
    def change_mode(self, args=None):
        """モードを変更"""
        if args:
            self.mode = args[0].upper()
            print(f"モードを {self.mode} に変更しました")
        else:
            print(f"現在のモード: {self.mode}")
    
    def check_status(self, args=None):
        """システム状態をチェック"""
        print("システム状態: OK")
    
    def set_variable(self, args: list[str]) -> None:
        """変数を設定します。 例: set my_var 123"""
        if len(args) < 2:
            print("使い方: set <変数名> <値>")
            return
        
        var_name = args[0]
        # 簡単のため、evalを使いますが、実際のアプリではセキュリティリスクがあります！
        # 文字列として設定する場合は ' をつけてください。例: set name 'Taro'
        try:
            value_str = " ".join(args[1:])
            value = eval(value_str) 
            self.variables[var_name] = value
            print(f"変数 '{var_name}' に値を設定しました。型: {type(value).__name__}")
        except Exception as e:
            print(f"値の評価に失敗しました: {e}")

    def show_variables(self, _args: list[str]) -> None:
        """保存されている変数を一覧表示します。"""
        if not self.variables:
            print("変数は設定されていません。")
            return
        
        print("--- 変数一覧 ---")
        for name, value in self.variables.items():
            print(f"  {name} ({type(value).__name__}): {value!r}")
        print("----------------")

    def copy_variable(self, args: list[str]) -> None:
        """変数をシャローコピーします。 例: copy source_var new_var"""
        if len(args) != 2:
            print("使い方: copy <コピー元変数> <新しい変数名>")
            return
        
        source_name, dest_name = args
        
        if source_name not in self.variables:
            print(f"エラー: 変数 '{source_name}' が見つかりません。")
            return
            
        # copy.copy() を使ってシャローコピーを実行
        original_value = self.variables[source_name]
        copied_value = copy.copy(original_value)
        
        self.variables[dest_name] = copied_value
        
        print(f"変数 '{source_name}' を '{dest_name}' にコピーしました。")
        print(f"コピー元のID: {id(original_value)}, コピー先のID: {id(copied_value)}")
        # リストなどのミュータブルなオブジェクトは、IDが変わり新しいオブジェクトが作られる

    def exit_cli(self, args=None) -> bool:
        """CLIを終了"""
        print("Goodbye!")
        return True
    
    def parse_command(self, command_line):
        """コマンドを解析"""
        if not command_line.strip():
            return None, []
        
        parts = command_line.strip().split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        return command, args
    
    def execute_command(self, command, args):
        """コマンドを実行"""
        if command in self.commands:
            return self.commands[command](args)
        else:
            print(f"コマンド '{command}' が見つかりません")
            # 不明なコマンドに対しても補完候補を提案
            suggestions = [cmd for cmd in self.commands.keys() if cmd.startswith(command)]
            if suggestions:
                print(f"もしかして: {', '.join(suggestions)}")
            return False
    
    def run(self):
        """メインループ"""
        # --- 3. readlineに補完関数を登録 ---
        readline.set_completer(self.completer)
        # Tabキーを押したときに補完が実行されるように設定
        readline.parse_and_bind("tab: complete")
        
        print(f"\n{self.mode} analysisモード（Tabキーで自動補完）")
        print("'help' でコマンド一覧を表示。入力中にTabキーを押すとコマンドを補完します。")
        
        while True:
            try:
                # input()をそのまま使うだけで、readlineが機能する
                user_input = input(f"[{self.mode}] {self.current_path} > ")
                
                command, args = self.parse_command(user_input)
                
                if command is None:
                    continue
                
                should_exit = self.execute_command(command, args)
                
                if should_exit:
                    break
                    
            except KeyboardInterrupt:
                print("\n\nCtrl+C が押されました。終了します。")
                break
            except EOFError:
                print("\n\nEOF が検出されました。終了します。")
                break
            except Exception as e:
                print(f"エラーが発生しました: {e}")

def main():
    print("=== Tab補完機能付きCLI ===")
    cli = InteractiveCLI()
    cli.run()

if __name__ == "__main__":
    main()