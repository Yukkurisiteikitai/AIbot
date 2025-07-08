# pip install prompt_toolkit が必要
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter, Completer, Completion
from prompt_toolkit.history import InMemoryHistory

class CustomCompleter(Completer):
    def __init__(self, cli_instance):
        self.cli = cli_instance
    
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        parts = text.split()
        
        if not parts or (len(parts) == 1 and not text.endswith(' ')):
            # コマンド名の補完
            for cmd in self.cli.commands.keys():
                if cmd.startswith(text):
                    yield Completion(cmd, start_position=-len(text))
        else:
            # 引数の補完
            command = parts[0].lower()
            current_word = parts[-1] if not text.endswith(' ') else ''
            
            if command == "mode":
                modes = ["ANA", "DEBUG", "PROD", "TEST", "DEV"]
                for mode in modes:
                    if mode.lower().startswith(current_word.lower()):
                        yield Completion(mode, start_position=-len(current_word))
            elif command == "check":
                items = ["status", "config", "memory", "disk", "network", "system"]
                for item in items:
                    if item.startswith(current_word):
                        yield Completion(item, start_position=-len(current_word))

class PromptToolkitCLI:
    def __init__(self):
        self.mode = "ANA"
        self.current_path = "home/"
        self.commands = {
            "help": self.show_help,
            "mode": self.change_mode,
            "check": self.check_status,
            "exit": self.exit_cli,
            "end": self.exit_cli,
        }
        self.history = InMemoryHistory()
        self.completer = CustomCompleter(self)
    
    def show_help(self, args=None):
        print("利用可能なコマンド: help, mode, check, exit, end")
        print("Tabキーで自動補完、↑↓キーで履歴参照")
    
    def change_mode(self, args=None):
        if args:
            self.mode = args[0].upper()
            print(f"モードを {self.mode} に変更しました")
        else:
            print(f"現在のモード: {self.mode}")
    
    def check_status(self, args=None):
        if args:
            print(f"チェック実行: {args[0]}")
        else:
            print("チェック項目を指定してください: status, config, memory, disk")
    
    def exit_cli(self, args=None):
        print("Goodbye!")
        return True
    
    def run(self):
        print(f"{self.mode} analysisモード（prompt_toolkit版）")
        
        while True:
            try:
                user_input = prompt(
                    f"[{self.mode}] {self.current_path} > ",
                    completer=self.completer,
                    history=self.history
                )
                
                if not user_input.strip():
                    continue
                
                parts = user_input.strip().split()
                command = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                if command in self.commands:
                    should_exit = self.commands[command](args)
                    if should_exit:
                        break
                else:
                    print(f"コマンド '{command}' が見つかりません")
                    
            except KeyboardInterrupt:
                print("\n終了します")
                break
            except EOFError:
                print("\n終了します")
                break

if __name__ == "__main__":
    cli = PromptToolkitCLI()
    cli.run()