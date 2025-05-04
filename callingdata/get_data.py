import mysql.connector
import pandas as pd
from trendspy import Trends
import os
import uuid

id = str(uuid.uuid4())[:8]

# Load danh sách keyword từ file CSV
csv_file = 'keyword.csv'
if not os.path.exists(csv_file):
    print("❌ File keyword.csv không tồn tại.")
    exit()

keywords_df = pd.read_csv(csv_file)

# Nếu file rỗng
if keywords_df.empty:
    print("✅ Không còn từ khóa nào để xử lý.")
    exit()

# Lấy dòng đầu tiên để xử lý
row = keywords_df.iloc[0]
keyword = row['keyword']
category = row['category']
detail_cat = row['detail_cat']  # ✅ Thêm dòng này

# Cấu hình thông tin truy vấn Trends
tr = Trends(hl='vi-VN', tz=360)
geo = 'VN'

start_date = '2024-01-01'
end_date = '2024-12-31'

# Lấy dữ liệu Google Trends
df = tr.interest_over_time(
    [keyword],
    headers={'referer': 'https://www.google.com/'},
    timeframe=f'{start_date} {end_date}',
    geo='VN'
)

# Tính trung bình và chuyển sang JSON
if not df.empty:
    trend_json = df.reset_index().to_json(orient='records', date_format='iso')
else:
    trend_json = '[]'


# Chuẩn bị dữ liệu để lưu
data = {
    'id': id,
    'keyword': keyword,
    'start_date': start_date,
    'end_date': end_date,
    'raw_trend_data': trend_json,
    'category': category,
    'detail_cat': detail_cat  # ✅ Thêm dòng này
}

# Kết nối đến MySQL
conn = mysql.connector.connect(
    host='127.0.0.1',
    user='baopham',
    password='Bao1808...',
    database='baopham$test',
    port=3307
)
cursor = conn.cursor()

# Tạo bảng nếu chưa tồn tại
cursor.execute("""
CREATE TABLE IF NOT EXISTS raw_db_ptdl1 (
    id VARCHAR(255) PRIMARY KEY,
    keyword VARCHAR(255),
    start_date DATE,
    end_date DATE,
    raw_trend_data JSON,
    category VARCHAR(50),
    detail_cat VARCHAR(100)
);
""")

# Chèn hoặc cập nhật dữ liệu
cursor.execute("""
INSERT INTO raw_db_ptdl1 (
    id, keyword, start_date, end_date, raw_trend_data, category, detail_cat
) VALUES (%s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    raw_trend_data=VALUES(raw_trend_data),
    category=VALUES(category),
    detail_cat=VALUES(detail_cat);
""", tuple(data.values()))

# Hoàn tất lưu
conn.commit()
cursor.close()
conn.close()

print("✅ Dữ liệu Google Trends đã được lưu thành công vào MySQL.")

# Xóa keyword vừa xử lý khỏi file CSV
keywords_df = keywords_df.drop(index=0)
keywords_df.to_csv(csv_file, index=False)
print(f"🧹 Đã xoá '{keyword}' khỏi file CSV.")
