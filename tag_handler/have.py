import os

# ファイル名のリスト（カンマ区切りに修正済み）
code_filenames = [
    "meta_module",
    "significant_childhood_experiences", # カンマ追加
    "influential_people",                # カンマ追加
    "inner_complexes_traumas",           # トラウマ・イベントもここに特別な属性で記録
    "personality_traits",
    "beliefs_values",
    "hobbies_interests",
    "interpersonal_style",               # カンマ追加
    "emotional_reaction_patterns",       # カンマ追加
    "aspirations_dreams",
    "past_failures_learnings",
    "internal_conflicts_coping",
    "emotional_triggers",
    "behavioral_patterns_underlying_needs",
    "thought_processes_cognitive_biases",
    "verbal_nonverbal_tics_indicated_thoughts",
    "evolution_of_values_turning_points",
    "self_perception_self_esteem",
    "conflict_resolution_style",
    "relationship_history_adaptation",
    "future_outlook_anxieties_hopes"
]

# ファイルを生成するディレクトリ (現在のディレクトリを指定)
output_directory = "./search" # もし特定のサブディレクトリに作りたい場合は "./subdir_name" のように指定

# ディレクトリが存在しない場合は作成 (今回はカレントディレクトリなので通常不要)
# if not os.path.exists(output_directory) and output_directory != ".":
#     os.makedirs(output_directory)

# 各ファイル名に対して .py ファイルを生成
for base_name in code_filenames:
    file_name = f"{base_name}.py"
    file_path = os.path.join(output_directory, file_name)

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            # ファイルに初期内容を書き込みたい場合はここに追加
            # 例: f.write("#!/usr/bin/env python3\n")
            # 例: f.write(f"# This is {file_name}\n\n")
            # 例: f.write("print('Hello from this module!')\n")
            pass # 空のファイルを作成
        print(f"ファイルを作成しました: {file_path}")
    except IOError as e:
        print(f"エラー: {file_path} の作成に失敗しました - {e}")
    except Exception as e:
        print(f"予期せぬエラーが発生しました ({file_name}): {e}")


print("\nすべてのファイルの作成処理が完了しました。")