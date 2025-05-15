import db_manager
import json
import asyncio

user_id = 1015220054528364584

with open("sample_user.json","r",encoding="utf-8")as f:
    data = json.load(f)


async def add_info(info_type: str, content: str):
    global user_id
    print(user_id)
    success = await db_manager.add_user_info(user_id=user_id, info_type=info_type.lower(),content=content)
    if success:
        print(f"情報タイプ `{info_type}` を登録/更新しました。")
    else:
        print("情報の登録中にエラーが発生しました。")
        

print(data)

for key,value in data.items():
    # print(f"{key}:{value}")
    asyncio.run(add_info(info_type=key,content=value))
