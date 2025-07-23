from rest_framework import serializers
from .models import Announcement


class AnnouncementStatsSerializer(serializers.Serializer):
    filter_criteria = serializers.CharField()
    nb_announcements = serializers.IntegerField()
    average_condominium_expenses = serializers.DecimalField(max_digits=10, decimal_places=2)
    percentile_10 = serializers.DecimalField(max_digits=10, decimal_places=2)
    percentile_90 = serializers.DecimalField(max_digits=10, decimal_places=2)


class AnnouncementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'
        