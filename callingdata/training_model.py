def predict_next_week(detail_cat):
    import mysql.connector
    import pandas as pd
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

    # Kết nối MySQL
    conn = mysql.connector.connect(
        host='127.0.0.1',
        user='baopham',
        password='Bao1808...',
        database='baopham$test',
        port=3307
    )

    cursor = conn.cursor(dictionary=True)

    # Câu SQL với placeholder và truyền biến vào tuple
    query = """
        SELECT ID, keyword_name, value, moving_avg_3, std_3, trend_3, month, weekofyear, pct_change, date
        FROM processed_trend_data3
        WHERE detail_cat LIKE %s
    """
    cursor.execute(query, (detail_cat,))
    rows = cursor.fetchall()

    if not rows:
        print("Không có dữ liệu cho detail_cat:", detail_cat)
        return None

    df = pd.DataFrame(rows)
    df = df.dropna(subset=['moving_avg_3', 'std_3', 'trend_3'])

    if len(df) < 5:
        print("Dữ liệu không đủ để dự đoán (ít hơn 5 dòng).")
        return None

    # Xây dựng X và y
    X = df[['weekofyear', 'moving_avg_3', 'std_3', 'trend_3']]
    y = df['value']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # print("MAE:", mean_absolute_error(y_test, y_pred))
    # print("RMSE:", mean_squared_error(y_test, y_pred, squared=False))
    # print("R² Score:", r2_score(y_test, y_pred))

    recent_data = df.iloc[-5:-2]
    moving_avg_3 = recent_data['value'].mean()
    std_3 = recent_data['value'].std()
    trend_3 = recent_data['value'].iloc[-1] - recent_data['value'].iloc[0]

    input_data = pd.DataFrame([{
        'weekofyear': 51,
        'moving_avg_3': moving_avg_3,
        'std_3': std_3,
        'trend_3': trend_3
    }])

    predicted_value = model.predict(input_data)
    return predicted_value[0]
