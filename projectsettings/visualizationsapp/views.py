import json

import numpy as np
from django.shortcuts import render
from .models import TrendData
import sys
import os

# Thêm thư mục cha của myproject vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from callingdata.get_detail_cat import get_detail_cat
from callingdata.training_model import predict_next_week

# Không cần thay đổi nhiều, chỉ cần truyền các dữ liệu riêng biệt
def trend_chart_view(request):
    keyword = 'hello, world'
    rate = 0

    if request.method == "POST":
        keyword = request.POST.get('keyword', '')
        keyword = get_detail_cat(keyword)
        rate = predict_next_week(keyword)
        print(rate)

    data = TrendData.objects.filter(detail_cat=keyword).order_by('date')
    labels = [d.date.strftime("%Y-%m-%d") for d in data]
    values = [d.value for d in data]
    values = [float(v) if isinstance(v, np.float64) else v for v in values]

    # Thêm tuần dự đoán vào cuối
    labels.append("Tuần tiếp theo")
    values.append(rate)

    print("Labels:", labels)
    print("Values:", values)
    print("Predicted Index:", len(values) - 1)

    return render(request, 'trend_chart.html', {
        'labels': json.dumps(labels),
        'values': json.dumps(values),  # Đây sẽ là dữ liệu kiểu float hoặc int
        'predicted_index': len(values) - 1,
        'uppercase_keyword': keyword
    })

