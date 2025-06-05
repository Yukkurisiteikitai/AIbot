from pydantic import BaseModel

class question_tiket(thread_tiket):
    question: str = "なんも質問が投げられてねーよ"
    answer: str = "なんも回答が投げられてねーよ"



class thread_tiket(BaseModel):
    user_id: str
    thread_id: str = "なんもスレッドが投げられてねーよ"
    mode:str = "search"


class question_tiket(BaseModel):
    user_id:int
    message:str
    
