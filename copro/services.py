import numpy as np

from django.db.models import Avg, Count
from django.db.models.functions import Round


class StatisticsService:
    """Service to calculate statistics for Announcement model."""

    def __init__(self, queryset, filter_params=None):
        self.queryset = self._clean_queryset(queryset, filter_params)
        self._calc_aggr_stats()
        self._calc_percentiles()
    
    def _filter_queryset(self, queryset, params):
        """Filter the queryset based on provided parameters."""
        if postal_code := params.get('postal_code'):
            self._set_filter_criteria('POSTAL_CODE', postal_code.zfill(5))
            return queryset.filter(postal_code=postal_code.zfill(5))
        if city := params.get('city'):
            self._set_filter_criteria('CITY', city.capitalize())
            return queryset.filter(city__iexact=city)
        if department := params.get('department'):
            self._set_filter_criteria('DEPARTMENT', department.zfill(2))
            return queryset.filter(department=department.zfill(2))
        return queryset
    
    def _clean_queryset(self, queryset, params):
        """Clean the queryset by applying filters and excluding null condominium expenses."""
        qs = self._filter_queryset(queryset, params) if params else queryset
        return qs.exclude(condominium_expenses__isnull=True)

    def _set_filter_criteria(self, field=None, value=None):
        """Set filter criteria for the queryset."""
        if field:
            self._filter_criteria = f"Filtered by {field}: {value}"
        else:
            self._filter_criteria = "No filter applied"
    
    def _calc_aggr_stats(self):
        """Calculate aggregate statistics for the queryset."""
        return self.queryset.aggregate(
            nb_announcements=Count('id'),
            average_condominium_expenses=Round(Avg('condominium_expenses'), 2),
        )

    def _calc_percentiles(self):
        """Calculate 10th and 90th percentiles of condominium expenses."""
        percentile_10 = percentile_90 = None
        expenses_values = list(self.queryset.values_list('condominium_expenses', flat=True))

        if expenses_values:
            expenses_array = np.array(expenses_values, dtype=float)
            percentile_10 = round(float(np.percentile(expenses_array, 10)), 2)
            percentile_90 = round(float(np.percentile(expenses_array, 90)), 2)
        
        return percentile_10, percentile_90
    
    def get_stats(self):
        """Get all calculated statistics as a dictionary."""
        p_10, p_90 = self._calc_percentiles()
        return {
            **self._calc_aggr_stats(),
            **dict(
                percentile_10=p_10, 
                percentile_90=p_90,
                filter_criteria=self._filter_criteria,
            )
        }
    