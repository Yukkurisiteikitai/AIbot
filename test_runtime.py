# import question_agent
from runtime.runtime import Runtime
import asyncio
runt = Runtime()

print(asyncio.run(runt.process_message(1,"君は生きるということについてどう考えるのか")))