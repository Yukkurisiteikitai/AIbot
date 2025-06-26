import asyncio
import random
from typing import List, Callable, Any

class TaskLimiter:
    def __init__(self, max_concurrent: int = 3):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.max_concurrent = max_concurrent
    
    async def run_with_limit(self, coro):
        """セマフォを使って同時実行数を制限しながらタスクを実行"""
        async with self.semaphore:
            return await coro
    
    async def run_all_tasks(self, tasks: List[Callable]):
        """全てのタスクを同時実行数制限付きで実行"""
        # 各タスクをrun_with_limitでラップ
        limited_tasks = [self.run_with_limit(task()) for task in tasks]
        
        # 全てのタスクを並行実行（セマフォにより同時実行数は制限される）
        results = await asyncio.gather(*limited_tasks, return_exceptions=True)
        return results

# サンプルタスク関数
async def sample_task(task_id: int, duration: float = None):
    """サンプルのasyncタスク"""
    if duration is None:
        duration = random.uniform(1, 5)  # 1-5秒のランダムな実行時間
    
    print(f"タスク {task_id} 開始 (実行時間: {duration:.2f}秒)")
    await asyncio.sleep(duration)
    print(f"タスク {task_id} 完了")
    return f"結果_{task_id}"

# 使用例1: 基本的な使い方
async def example1():
    print("=== 例1: 基本的な使い方 ===")
    limiter = TaskLimiter(max_concurrent=3)
    
    # 10個のタスクを準備
    tasks = [lambda i=i: sample_task(i) for i in range(10)]
    
    print("10個のタスクを開始（同時実行は最大3つまで）")
    results = await limiter.run_all_tasks(tasks)
    
    print("全タスク完了")
    print(f"結果: {results}")

# 使用例2: asyncio.as_completedを使った方法
async def run_tasks_with_completion_tracking(tasks: List[Callable], max_concurrent: int = 3):
    """タスクの完了を逐次追跡する方法"""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def limited_task(task_func):
        async with semaphore:
            return await task_func()
    
    # タスクを作成
    running_tasks = [asyncio.create_task(limited_task(task)) for task in tasks]
    
    # 完了順に結果を取得
    completed_count = 0
    for completed_task in asyncio.as_completed(running_tasks):
        result = await completed_task
        completed_count += 1
        print(f"タスク完了 ({completed_count}/{len(tasks)}): {result}")
    
    return [task.result() for task in running_tasks]

# 使用例2の実行
async def example2():
    print("\n=== 例2: 完了追跡付き ===")
    
    # 8個のタスクを準備
    tasks = [lambda i=i: sample_task(i+10, random.uniform(1, 3)) for i in range(8)]
    
    print("8個のタスクを開始（同時実行は最大3つまで、完了順に表示）")
    results = await run_tasks_with_completion_tracking(tasks, max_concurrent=3)
    
    print(f"全結果: {results}")

# 使用例3: より柔軟な制御
class AdvancedTaskLimiter:
    def __init__(self, max_concurrent: int = 3):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.running_tasks = set()
        self.completed_tasks = []
    
    async def add_task(self, coro):
        """新しいタスクを追加"""
        task = asyncio.create_task(self._run_task(coro))
        self.running_tasks.add(task)
        return task
    
    async def _run_task(self, coro):
        """タスク実行のラッパー"""
        async with self.semaphore:
            try:
                result = await coro
                self.completed_tasks.append(result)
                return result
            finally:
                # 完了したタスクをrunning_tasksから削除
                current_task = asyncio.current_task()
                self.running_tasks.discard(current_task)
    
    async def wait_for_completion(self):
        """全てのタスクの完了を待つ"""
        while self.running_tasks:
            done, pending = await asyncio.wait(
                self.running_tasks, 
                return_when=asyncio.FIRST_COMPLETED
            )
            self.running_tasks = pending

# 使用例3の実行
async def example3():
    print("\n=== 例3: 動的タスク追加 ===")
    limiter = AdvancedTaskLimiter(max_concurrent=3)
    
    # 最初の5つのタスクを追加
    for i in range(5):
        await limiter.add_task(sample_task(i+20))
    
    # 少し待ってから追加のタスクを投入
    await asyncio.sleep(2)
    print("追加タスクを投入...")
    
    for i in range(5, 10):
        await limiter.add_task(sample_task(i+20))
    
    # 全完了を待つ
    await limiter.wait_for_completion()
    print(f"完了したタスク数: {len(limiter.completed_tasks)}")

# メイン実行
async def main():
    await example1()
    await example2()
    await example3()

if __name__ == "__main__":
    asyncio.run(main())