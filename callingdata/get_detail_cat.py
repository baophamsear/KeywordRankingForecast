# import json
#
# from deep_translator import GoogleTranslator
# from sentence_transformers import SentenceTransformer, util
# import pandas as pd
#
# model = SentenceTransformer('all-MiniLM-L6-v2')
#
#
# def get_cat(keyword):
#     df = pd.read_csv("unique_categories.csv")
#     categories = df["name"].astype(str).tolist()
#
#     keyword_en = GoogleTranslator(source='vi', target='en').translate(keyword)
#     print("Từ khoá tiếng Anh:", keyword_en)
#
#     # Không cần load model lại, dùng model global
#     category_embeddings = model.encode(categories, convert_to_tensor=True)
#     keyword_embedding = model.encode(keyword_en, convert_to_tensor=True)
#
#     cosine_scores = util.cos_sim(keyword_embedding, category_embeddings)[0]
#
#     top_index = int(cosine_scores.argmax())
#     best_match = df.iloc[top_index]
#
#     print("Danh mục phù hợp nhất:", best_match["name"])
#     print("Điểm tương đồng:", float(cosine_scores[top_index]))
#     print("========================================")
#     return best_match["name"], keyword_en  # Trả thêm từ khoá tiếng Anh
#
#
# def get_detail_cat(keyword):
#     with open("category_detailcat.json", 'r', encoding='utf-8') as f:
#         data = json.load(f)
#
#     category, keyword_en = get_cat(keyword)
#
#     if category not in data:
#         raise ValueError(f"Category '{category}' không có trong danh sách")
#
#     detail_cats = data[category]
#     print("Danh sách detail_cats:", detail_cats)
#
#     # Encode detail_cats và keyword_en (chứ không phải category!)
#     detail_cats_embeddings = model.encode(detail_cats, convert_to_tensor=True)
#     keyword_embedding = model.encode(keyword_en, convert_to_tensor=True)
#
#     cosine_scores = util.cos_sim(keyword_embedding, detail_cats_embeddings)[0]
#
#     best_match_idx = cosine_scores.argmax()
#     best_match = detail_cats[best_match_idx]
#     best_score = float(cosine_scores[best_match_idx])
#
#     print("Detail_cat phù hợp nhất:", best_match)
#     print("Similarity:", best_score)
#     return best_match
#
#
# # get_detail_cat("Du lịch Hàn Quốc")
#

import json
import os
from deep_translator import GoogleTranslator
from sentence_transformers import SentenceTransformer, util
import pandas as pd

model = SentenceTransformer('all-MiniLM-L6-v2')

# Đường dẫn tuyệt đối tới file JSON
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "category_detailcat.json")
CSV_PATH = os.path.join(BASE_DIR, "unique_categories.csv")

def get_cat(keyword):
    df = pd.read_csv(CSV_PATH)
    categories = df["name"].astype(str).tolist()

    keyword_en = GoogleTranslator(source='vi', target='en').translate(keyword)
    print("Từ khoá tiếng Anh:", keyword_en)

    category_embeddings = model.encode(categories, convert_to_tensor=True)
    keyword_embedding = model.encode(keyword_en, convert_to_tensor=True)

    cosine_scores = util.cos_sim(keyword_embedding, category_embeddings)[0]
    top_index = int(cosine_scores.argmax())
    best_match = df.iloc[top_index]

    print("Danh mục phù hợp nhất:", best_match["name"])
    print("Điểm tương đồng:", float(cosine_scores[top_index]))
    print("========================================")
    return best_match["name"], keyword_en


def get_detail_cat(keyword):
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    category, keyword_en = get_cat(keyword)

    if category not in data:
        raise ValueError(f"Category '{category}' không có trong danh sách")

    detail_cats = data[category]
    print("Danh sách detail_cats:", detail_cats)

    detail_cats_embeddings = model.encode(detail_cats, convert_to_tensor=True)
    keyword_embedding = model.encode(keyword_en, convert_to_tensor=True)

    cosine_scores = util.cos_sim(keyword_embedding, detail_cats_embeddings)[0]
    best_match_idx = cosine_scores.argmax()
    best_match = detail_cats[best_match_idx]
    best_score = float(cosine_scores[best_match_idx])

    print("Detail_cat phù hợp nhất:", best_match)
    print("Similarity:", best_score)
    return best_match
