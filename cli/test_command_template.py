class CommandTemplate:
    def __init__(self) -> None:
        self.name = "NoName"
        # 辞書の構文を修正
        self.args = {
            "a": {"description": "全ての項目を表示", "long": "all"},
            "h": {"description": "ヘルプを表示", "long": "help"},
            "v": {"description": "詳細モード", "long": "verbose"}
        }
        self.flags = ["-a", "--all", "-h", "--help", "-v", "--verbose"]
    
    def run(self, args: str = "-a", target: str = "[target]"):
        """コマンドを実行する"""
        # 引数の解析
        parsed_args = self._parse_args(args)
        
        if "h" in parsed_args or "help" in parsed_args:
            self._show_help()
            return
        
        if "a" in parsed_args or "all" in parsed_args:
            print(f"全ての項目を処理中: {target}")
            # 実際の処理をここに実装
        
        if "v" in parsed_args or "verbose" in parsed_args:
            print(f"詳細モード: {target}")
    
    def _parse_args(self, args: str) -> list:
        """引数文字列を解析してリストで返す"""
        # 簡単な引数解析（実際にはargparseを使用することを推奨）
        args = args.replace("-", "").replace(" ", "")
        return list(args)
    
    def _show_help(self):
        """ヘルプを表示"""
        print(f"コマンド: {self.name}")
        print("使用可能なオプション:")
        for short, info in self.args.items():
            print(f"  -{short}, --{info['long']}: {info['description']}")


# より汎用的なコマンドシステム
class CommandSystem:
    def __init__(self):
        self.commands = {}
    
    def register_command(self, command_instance: CommandTemplate):
        """コマンドを登録"""
        self.commands[command_instance.name] = command_instance
    
    def execute(self, command_name: str, args: str = "", target: str = ""):
        """コマンドを実行"""
        if command_name in self.commands:
            self.commands[command_name].run(args, target)
        else:
            print(f"コマンド '{command_name}' が見つかりません")
    
    def list_commands(self):
        """登録されているコマンドを一覧表示"""
        print("使用可能なコマンド:")
        for name, cmd in self.commands.items():
            print(f"  {name}")


# 使用例
if __name__ == "__main__":
    # コマンドシステムの初期化
    cmd_system = CommandSystem()
    
    # カスタムコマンドの作成
    class ListCommand(CommandTemplate):
        def __init__(self):
            super().__init__()
            self.name = "list"
    
    class CopyCommand(CommandTemplate):
        def __init__(self):
            super().__init__()
            self.name = "copy"
    
    # コマンドを登録
    cmd_system.register_command(ListCommand())
    cmd_system.register_command(CopyCommand())
    
    # メインループ
    while True:
        try:
            user_input = input("> ")
            args = ""
            
            if user_input.strip() == "exit":
                break
            
            user_box = user_input.split(' ')
            
            # 空の入力をチェック
            if not user_box or user_box[0] == "":
                continue
            
            # 引数の抽出（-で始まるもの）
            for i in user_box:
                if i.startswith("-"):
                    args += i[1:]  # -を除いた部分を追加
            
            # ターゲットの取得（引数以外の2番目の要素）
            target = ""
            non_flag_args = [arg for arg in user_box[1:] if not arg.startswith("-")]
            if non_flag_args:
                target = non_flag_args[0]
            
            # コマンドの実行
            cmd_system.execute(user_box[0], args, target)
            
        except KeyboardInterrupt:
            print("\n終了します...")
            break
        except IndexError:
            print("引数が不足しています")
        except Exception as e:
            print(f"エラー: {e}")
    
    # # コマンドの実行例
    # cmd_system.execute("list", "-a", "documents")
    # cmd_system.execute("copy", "-v", "file.txt")