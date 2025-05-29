from runtime.runtime import Runtime
import asyncio


ai_runtime = Runtime(config_path="config.yaml")
print(asyncio.run(ai_runtime.process_message(user_id="jfoaeg;o3f",message="hello")))


