from django.urls import path

from .views import AnnouncementStatsView, AnnouncementCreateFromUrlView


urlpatterns = [
    path('announcements/stats/', AnnouncementStatsView.as_view(), name='announcement-stats'),
    path('announcements/create-from-url/', AnnouncementCreateFromUrlView.as_view(), name='announcement-create-from-url'),
]
