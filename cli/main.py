#!/usr/bin/env python3
import os
import sys
import readline

class DebugCLI:
    def __init__(self):
        self.mode = "ANA"
        self.current_path = "home/"
        self.commands = {
            "help": self.show_help,
            "mode": self.change_mode,
            "check": self.check_status,
            "test": self.test_completion,
            "debug": self.debug_readline,
            "exit": self.exit_cli,
            "end": self.exit_cli,
        }
        self.setup_autocomplete()
    
    def setup_autocomplete(self):
        """自動補完の設定"""
        try:
            print("🔧 自動補完の設定を開始...")
            
            # 現在の設定を表示
            print(f"   現在のデリミタ: '{readline.get_completer_delims()}'")
            
            # デリミタを設定
            readline.set_completer_delims(' \t\n')
            print(f"   新しいデリミタ: '{readline.get_completer_delims()}'")
            
            # 補完関数を設定
            readline.set_completer(self.complete)
            print("   補完関数を設定しました")
            
            # キーバインドを設定
            readline.parse_and_bind('tab: complete')
            print("   Tabキーをバインドしました")
            
            # 追加のキーバインド設定を試す
            readline.parse_and_bind('set completion-ignore-case on')
            readline.parse_and_bind('set show-all-if-ambiguous on')
            readline.parse_and_bind('set completion-query-items 200')
            print("   追加設定を適用しました")
            
            print("✅ 自動補完の設定完了")
            
        except Exception as e:
            print(f"❌ 自動補完の設定に失敗: {e}")
    
    def complete(self, text, state):
        """自動補完のメイン関数"""
        try:
            # デバッグ情報を表示
            line = readline.get_line_buffer()
            print(f"\n[DEBUG] complete() called:")
            print(f"   text: '{text}'")
            print(f"   state: {state}")
            print(f"   line: '{line}'")
            
            # 補完候補を生成
            if not text:
                # 空の場合は全コマンドを候補にする
                options = list(self.commands.keys())
            else:
                # 入力されたテキストで始まるコマンドを探す
                options = [cmd for cmd in self.commands.keys() if cmd.startswith(text)]
            
            print(f"   candidates: {options}")
            
            # 指定された状態の候補を返す
            if state < len(options):
                result = options[state]
                print(f"   returning: '{result}'")
                return result
            else:
                print(f"   no more candidates")
                return None
                
        except Exception as e:
            print(f"\n[ERROR] complete() failed: {e}")
            return None
    
    def show_help(self, args=None):
        """ヘルプを表示"""
        print("利用可能なコマンド:")
        print("  help   - このヘルプを表示")
        print("  mode   - モードを表示/変更")
        print("  check  - システム状態をチェック")
        print("  test   - 補完テストを実行")
        print("  debug  - readline設定を表示")
        print("  exit   - CLIを終了")
        print("\n使い方:")
        print("  'm' + Tab → 'mode' に補完されるはずです")
        print("  'c' + Tab → 'check' に補完されるはずです")
    
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
    
    def test_completion(self, args=None):
        """補完機能のテスト"""
        print("補完テスト:")
        print("以下を試してください:")
        print("1. 'm' と入力してTab")
        print("2. 'c' と入力してTab")
        print("3. 'he' と入力してTab")
        print("4. 空の状態でTab")
    
    def debug_readline(self, args=None):
        """readline設定のデバッグ情報を表示"""
        print("=== readline デバッグ情報 ===")
        print(f"readline version: {readline.__doc__}")
        print(f"completer_delims: '{readline.get_completer_delims()}'")
        print(f"completer function: {readline.get_completer()}")
        
        # 手動でcompleteを呼び出してテスト
        print("\n=== 手動補完テスト ===")
        test_cases = [('m', 0), ('c', 0), ('he', 0), ('', 0)]
        
        for text, state in test_cases:
            try:
                result = self.complete(text, state)
                print(f"complete('{text}', {state}) = '{result}'")
            except Exception as e:
                print(f"complete('{text}', {state}) = ERROR: {e}")
    
    def exit_cli(self, args=None):
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
            return False
    
    def run(self):
        """メインループ"""
        print(f"{self.mode} analysisモード（デバッグ版）")
        print("'help' でコマンド一覧を表示")
        print("'test' で補完テストを実行")
        print("'debug' でreadline設定を確認")
        
        while True:
            try:
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
    print("=== デバッグ機能付きCLI ===")
    cli = DebugCLI()
    cli.run()

if __name__ == "__main__":
    main()