# from dotenv import load_dotenv
# import os
# import asyncio
# import openai
# load_dotenv()

# # --- LM Studio 設定 ---
# # .envファイルからLM StudioのエンドポイントURLを読み込む
# # デフォルトは http://localhost:1234/v1
# LM_STUDIO_URL = os.getenv("LM_STUDIO_BASE_URL")
# # LM StudioはAPIキーを必要としない場合が多いので、ダミーを設定
# LM_STUDIO_API_KEY = "lm-studio" # または "dummy-key", "not-needed" など
# LM_STUDIO_MODEL_REQUEST = os.getenv("LM_STUDIO_MODEL_REQUEST")
# LM_STUDIO_MODEL_RESPONSE = os.getenv("LM_STUDIO_MODEL_RESPONSE")


# system_prompt = """
# 人間です。楽しんで
# """

# user_prompt = """
# いええええい楽しんでる?
# """

# sys = """
# あなたは真面目な人間です。とある友人が適当な回答を指摘ました。適切に回答をしてください。
# """

# client = openai.AsyncOpenAI(
#     base_url=LM_STUDIO_URL,
#     api_key=LM_STUDIO_API_KEY,
# )

# messages = [
#         {"role": "system", "content": sys},
#         {"role": "user", "content": user_prompt},
# ]

# async def test(mes:list):
#     c_h = mes
    
#     completion = await client.chat.completions.create(
#             model=LM_STUDIO_MODEL_REQUEST,
#             messages=c_h, # 修正されたメッセージリストを使用
#             temperature=0.7,
#             max_tokens=300 # 長い応答が必要な場合は増やす
#         )
#     response_text = completion.choices[0].message.content.strip()
#     print(response_text)
#     c_h.append({"role": "assistant", "content": response_text})
#     c_h.append({"role": "system", "content": system_prompt})
#     c_h.append({"role": "user", "content": response_text})
    
    
#     completion = await client.chat.completions.create(
#             model=LM_STUDIO_MODEL_REQUEST,
#             messages=c_h, # 修正されたメッセージリストを使用
#             temperature=0.7,
#             max_tokens=300 # 長い応答が必要な場合は増やす
#         )
#     response_text = completion.choices[0].message.content.strip()
#     c_h.append({"role": "assistant", "content": response_text})
#     # save(c_h)
#     print(f"""
# ======LOGGG================
#           {c_h}
# ===========================
#           """)
#     print(response_text)
    

# import json
# def save(fe:list):
#     with open("teketou.json","a",encoding="utf-8")as f:
#         json.dumps(fe, f,indent=4)


# asyncio.run(test(mes=messages))
# # print(mes)

import json
with open("test_config.json","r",encoding="utf-8")as f:
    test_data = json.load(f)
    
print(test_data)
# ユーザーからのメッセージと状況 (例)
user_id = test_data["userID"]
user_message = test_data["user_message"]
situation_data = test_data["situation_data"]

print(f"""     
user_id = {user_id}
user_message = {user_message}
situation_data = {situation_data}
      """)

