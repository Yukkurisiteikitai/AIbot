#!/usr/bin/env python3
import os
import sys
import readline
from core.ai.analysis import Analysis
from core.ai.simulation import Reproduction

class MainCLI:
    def __init__(self):
        self.mode = "MENU"
        self.current_path = "home/"
        self.commands = {
            "help": self.show_help,
            "analysis": self.start_analysis,
            "reproduction": self.start_reproduction,
            "mode": self.show_mode,
            "exit": self.exit_cli,
            "quit": self.exit_cli,
        }
        self.analysis_handler = Analysis()
        self.reproduction_handler = Reproduction()
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
        print("=== YorselfLM CLI ===")
        print("利用可能なコマンド:")
        print("  help         - このヘルプを表示")
        print("  analysis     - Analysisモードを開始")
        print("  reproduction - Reproductionモードを開始")
        print("  mode         - 現在のモードを表示")
        print("  exit/quit    - CLIを終了")
        print("\nモードについて:")
        print("  Analysis     - スレッド管理付きの高度な対話モード")
        print("  Reproduction - シンプルな質問応答モード")
    
    def start_analysis(self, args=None):
        """Analysisモードを開始"""
        print("\nAnalysisモードを開始します...")
        try:
            self.analysis_handler.start_session()
        except Exception as e:
            print(f"Analysisモードでエラーが発生しました: {e}")
        print("\nメインメニューに戻ります。")
    
    def start_reproduction(self, args=None):
        """Reproductionモードを開始"""
        print("\nReproductionモードを開始します...")
        try:
            self.reproduction_handler.start_session()
        except Exception as e:
            print(f"Reproductionモードでエラーが発生しました: {e}")
        print("\nメインメニューに戻ります。")
    
    def show_mode(self, args=None):
        """現在のモードを表示"""
        print(f"現在のモード: {self.mode}")
        print("利用可能なモード: Analysis, Reproduction")
    
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
        print("=== YorselfLM CLI ===\n")
        print("LLMを活用した高度な対話システムです。")
        print("'help' でコマンド一覧を表示")
        print("'analysis' でAnalysisモードを開始")
        print("'reproduction' でReproductionモードを開始\n")
        
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
    cli = MainCLI()
    cli.run()

if __name__ == "__main__":
    main()