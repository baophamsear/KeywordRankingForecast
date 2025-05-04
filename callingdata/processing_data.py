import json
import pandas as pd
import numpy as np
import mysql.connector
import uuid
from datetime import datetime

# Kết nối tới MySQL trên PythonAnywhere
conn = mysql.connector.connect(
    host='127.0.0.1',
    user='baopham',
    password='Bao1808...',
    database='baopham$test',
    port=3307
)

cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT id, keyword, start_date, end_date, raw_trend_data, category, detail_cat FROM raw_db_ptdl1")
rows = cursor.fetchall()

all_data = []

for row in rows:
    id_ = row['id']
    keyword = row['keyword']
    raw_json = row['raw_trend_data']
    category = row['category']
    detail_cat = row['detail_cat']

    try:
        trend_data = json.loads(raw_json)

        if isinstance(trend_data, list):
            cleaned_data = []
            for item in trend_data:
                time_val = item.get('time [UTC]')
                values = {k: v for k, v in item.items() if k != 'time [UTC]'}
                if time_val is not None and values:
                    new_item = {'time [UTC]': time_val}
                    new_item.update(values)
                    cleaned_data.append(new_item)

            if not cleaned_data:
                continue

            df = pd.DataFrame(cleaned_data)
        else:
            continue

        if 'time [UTC]' not in df.columns:
            continue

        df['time [UTC]'] = pd.to_datetime(df['time [UTC]'])
        df = df.sort_values('time [UTC]')

        value_column = df.columns[1]
        df[value_column] = pd.to_numeric(df[value_column], errors='coerce')

        # Tính toán các cột mới
        df['ID'] = [str(uuid.uuid4())[:8] for _ in range(len(df))]
        df['ID'].astype(str)
        df['keyword_name'] = keyword
        df['value'] = df[value_column]
        df['moving_avg_3'] = df['value'].shift(1).rolling(window=3).mean() #thay đổi ở đây
        df['std_3'] = df['value'].shift(1).rolling(window=3).std() #thay đổi ở đây


        # Tính slope làm trend_3
        def calc_slope(arr):
            x = np.arange(len(arr))
            slope, _ = np.polyfit(x, arr, 1)
            return slope


        df['trend_3'] = df['value'].shift(1).rolling(window=3).apply(calc_slope, raw=True)

        df['month'] = df['time [UTC]'].dt.month
        df['delta_t_1'] = df['value'].diff()
        # df['weekofyear'] = df['date'].dt.isocalendar().week.astype(int)
        df['pct_change'] = df['value'].pct_change()
        # df['date'] = df['time [UTC]'].dt.strftime('%Y-%m-%d')
        # df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['date'] = pd.to_datetime(df['time [UTC]'], errors='coerce')  # Tạo cột 'date' trước
        df['weekofyear'] = df['date'].dt.isocalendar().week.astype(int)
        df['category'] = category
        df['detail_cat'] = detail_cat

        # Lọc ra các cột cần thiết
        result_df = df[['ID', 'keyword_name', 'value', 'moving_avg_3', 'std_3', 'trend_3', 'month', 'delta_t_1', 'weekofyear',
                        'pct_change', 'date', 'category', 'detail_cat']]

        all_data.append(result_df)

    except Exception as e:
        print(f"Lỗi xử lý dòng {id_} - {keyword}: {e}")

# Gộp toàn bộ dữ liệu
final_df = pd.concat(all_data, ignore_index=True)

pd.set_option('display.max_columns', None)  # Hiển thị tất cả cột
pd.set_option('display.max_rows', None)     # Hiển thị tất cả dòng
pd.set_option('display.width', None)        # Không giới hạn độ rộng
pd.set_option('display.max_colwidth', None) # Hiển thị toàn bộ nội dung trong mỗi ô

final_df['date'] = final_df['date'].dt.strftime('%Y-%m-%d')

final_df = final_df.replace([float('inf'), float('-inf')], pd.NA)
final_df = final_df.where(pd.notnull(final_df), None)
print(final_df)


# Ghi vào file CSV
unique_categories = final_df['category'].dropna().unique()
category_df = pd.DataFrame({'category': unique_categories})
category_df.to_csv('unique_categories.csv', index=False)

# Tạo dictionary theo dạng category: {detail_cat1, detail_cat2, ...}
category_detailcat_dict = (
    final_df.groupby('category')['detail_cat']
    .apply(lambda x: sorted(set(x.dropna())))
    .to_dict()
)

# Ghi dictionary ra file JSON
with open('category_detailcat.json', 'w', encoding='utf-8') as f:
    json.dump(category_detailcat_dict, f, ensure_ascii=False, indent=4)

cursor.execute("""
CREATE TABLE IF NOT EXISTS processed_trend_data3 (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    keyword_name VARCHAR(255),
    value FLOAT,
    moving_avg_3 FLOAT,
    std_3 FLOAT,
    trend_3 FLOAT,
    month INT,
    delta_t_1 FLOAT,
    weekofyear INT,
    pct_change FLOAT,
    date DATE,
    category VARCHAR(255),
    detail_cat VARCHAR(255)
);
""")

insert_query = """
    INSERT INTO processed_trend_data3 (
        keyword_name, value, moving_avg_3, std_3, trend_3,
        month, delta_t_1, weekofyear, pct_change, date, category, detail_cat
    )
    VALUES (
        %(keyword_name)s, %(value)s, %(moving_avg_3)s, %(std_3)s, %(trend_3)s,
        %(month)s, %(delta_t_1)s, %(weekofyear)s, %(pct_change)s, %(date)s, %(category)s, %(detail_cat)s
    )
"""

# Chuyển DataFrame thành list of dict để insert
data_to_insert = final_df.to_dict(orient='records')

try:
    cursor.executemany(insert_query, data_to_insert)
    conn.commit()
    print(f"Đã lưu {cursor.rowcount} dòng dữ liệu vào bảng processed_trend_data.")
except Exception as e:
    print("Lỗi khi lưu vào database:", e)