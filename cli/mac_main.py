#!/usr/bin/env python3
import os
import sys
import readline # <- 1. readlineをインポート
from typing import TypeAlias
from collections.abc import Callable

# handler
CommandHandler: TypeAlias = Callable[[list[str]], bool | None]


class InteractiveCLI:
    def __init__(self) -> None:
        self.mode: str = "ANA"
        self.current_path: str = "home/"
        
        # --- ここからが追加/変更箇所 ---
        
        # 1. 変数を保存するための辞書を追加
        # キーは変数名(str)、値はどんな型でも入る(Any)
        self.variables: dict[str, Any] = {
            'greeting': 'hello world',
            'numbers': [10, 20, 30]
        }

        self.commands: dict[str, CommandHandler] = {
            "help": self.show_help,
            "mode": self.change_mode,
            "check": self.check_status,
            "exit": self.exit_cli,
            "end": self.exit_cli,
            # 2. 新しいコマンドを登録
            "set": self.set_variable,
            "vars": self.show_variables,
            "copy": self.copy_variable,
        }

    # (completer, show_helpなどの既存メソッドは省略)
    # ...

    # --- 3. 新しいコマンドのメソッドを実装 ---

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