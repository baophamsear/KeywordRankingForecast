from django.db import models

class TrendData(models.Model):
    keyword_name = models.CharField(max_length=255)
    value = models.FloatField()
    moving_avg_3 = models.FloatField(null=True, blank=True)
    std_3 = models.FloatField(null=True, blank=True)
    trend_3 = models.FloatField(null=True, blank=True)
    weekofyear = models.IntegerField()
    date = models.DateField()
    category = models.CharField(max_length=50, null=True, blank=True)
    detail_cat = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'processed_trend_data3'