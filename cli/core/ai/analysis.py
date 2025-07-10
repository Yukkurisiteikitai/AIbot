from typing import Any, Dict

class Command_template:
    def __init__(self) -> None:
        self.name = "NoName"
        self.flag: Dict[str, bool] = {"detail_second": False}
        self.args: Dict[str, Any] = {
            "a": {"description": "hello", "flag": self.flag["detail_second"]},
            "all": {"description": "hello", "flag": self.flag["detail_second"]}
        }
        self.now_thread_id: str = "sef_22"

    def run(self, args: str = "-a", target: str = "[target]") -> None:
        """基本的な実行メソッド（サブクラスでオーバーライドされる）"""
        pass

class Analysis(Command_template):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # 必要に応じて analysis 固有の設定を追加
        self.name = "Analysis"
        self.flag: Dict[str, bool] = {"detail_second": False}
        self.args: Dict[str, Any] = {key: {"description": "hello", "flag": self.flag["detail_second"]} for key in ["a", "all"]}
        print(self.args)
        
    def run(self, args: str = "-a", target: str = "[target]") -> None:
        """分析コマンドの実行"""
        print(f"Running analysis with args: {args}, target: {target}")
        
        # 引数の処理
        if args in ["-a", "--all"]:
            self._run_all_analysis(target)
        elif args in ["-d", "--detail"]:
            self.flag["detail_second"] = True
            self._run_detailed_analysis(target)
        else:
            print(f"Unknown argument: {args}")
    
    def _run_all_analysis(self, target: str) -> None:
        """すべての分析を実行"""
        print(f"Running all analysis on {target}")
        # 実際の分析処理をここに実装
        
    def _run_detailed_analysis(self, target: str) -> None:
        """詳細分析を実行"""
        print(f"Running detailed analysis on {target}")
        # 実際の詳細分析処理をここに実装

# 使用例
if __name__ == "__main__":
    # 基本的な使用
    analysis_cmd = Analysis()
    analysis_cmd.run("-a", "sample_target")
    
    # 詳細分析
    analysis_cmd.run("-d", "sample_target")
    
    # 属性の確認
    print(f"Command name: {analysis_cmd.name}")
    print(f"Available args: {list(analysis_cmd.args.keys())}")
    print(f"Thread ID: {analysis_cmd.now_thread_id}")