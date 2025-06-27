import yaml


class Question_Data:
    def __init__(self,meta_data_path:str):
        self.meta_data_path = meta_data_path
        with open(self.meta_data_path, 'r', encoding='utf-8') as f:
            self.question_data = yaml.safe_load(f)
    
    def get_theme(self,theme:str) -> dict:
        return self.question_data["question_themes"][theme]
    
    def get_question_list(self) -> dict:
        return self.question_data["presentation_order"]
    