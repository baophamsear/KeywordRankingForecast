from django.urls import path
from .views import trend_chart_view

urlpatterns = [
    path('chart/', trend_chart_view, name='trend-chart'),
]