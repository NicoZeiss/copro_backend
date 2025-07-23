from django.contrib import admin
from .models import Announcement

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['reference', 'postal_code', 'city', 'department', 'condominium_expenses']
    list_filter = ['department']
    search_fields = ['reference', 'postal_code', 'city', 'department']
    list_per_page = 100
    ordering = ['department', 'city']
    