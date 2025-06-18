from yaml import safe_load

config_path = "configs/meta_question.yaml"

def load_yaml(path):
    with open(config_path,"r",encoding="utf-8")as f:
        _data = safe_load(f)
        return _data


# _question_meta_data = load_yaml(config_path)
# from dataclasses import dataclass
# @dataclass
# class question_metadata_format():
#     def __init__(self,metadata_config_data:dict):
#         # base_order
#         self.metadata_config_data = metadata_config_data
#         self.metadata_base =self.metadata_config_data["question_themes"]
#         self.init_order_question_ids = self.metadata_config_data["presentation_order"]
        
    
    
#     def get_metadata(self,mode:str = "name",context_name:str = "Whot is you", context_id:int = 0):

#         if mode == "name":
#             self.metadata = self.metadata_base[context_name]
#         elif mode == "id":

#             #　絶対効率悪いオード
#             for t in self.init_order_question_ids:
#                 self.metadata = self.metadata_base[t]
#                 if context_id == self.metadata["original_tag_id"]:
#                     break


        
#         # meta dataですね
#         self.display_name:str = self.metadata["display_name"]
#         self.definition:str = self.metadata["definition"]
#         self.input_examples:list = self.metadata["input_examples"]
#         self.question_prompts_for_ai:list[str] = self.metadata["question_prompts_for_ai"]
#         self.related_person_data_key:str = self.metadata["related_person_data_key"]
#         self.notes:str = self.metadata["notes"]
#         self.original_tag_id:int = self.metadata["original_tag_id"]

#         return {
#             "display_name":self.display_name,
#             "definition":self.definition,
#             "input_examples":self.input_examples, 
#             "question_prompts_for_ai":self.question_prompts_for_ai, 
#             "related_person_data_key":self.related_person_data_key, 
#             "notes":self.notes,
#             "original_tag_id":self.original_tag_id
#         }

#     def get_order_ids(self):
#         return self.init_order_question_ids = self.metadata_config_data["presentation_order"]
