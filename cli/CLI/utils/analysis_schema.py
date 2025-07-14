

class Token_Base(): 
    def __init__(self,text: str = "Not-Found",cofidence: float = -1.0):
        self.text: str = text # なんも設定されない時は説明されないことを示す
        self.cofidence: float = cofidence # 通常は設定されないため-1.0を設定する
    