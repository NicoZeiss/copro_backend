import re
import requests

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Announcement
from .serializers import AnnouncementStatsSerializer, AnnouncementCreateSerializer
from .services import StatisticsService


class AnnouncementStatsView(APIView):

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='postal_code',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by postal code',
                required=False
            ),
            OpenApiParameter(
                name='city',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by city',
                required=False
            ),
            OpenApiParameter(
                name='department',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by department',
                required=False
            ),
        ],
        responses=AnnouncementStatsSerializer,
        description='Get announcement statistics with optional filtering by postal code or department'
    )
    def get(self, request):
        """Retrieve statistics for announcements with optional filters."""
        stats_service = StatisticsService(Announcement.objects.all(), request.query_params)
        serializer = AnnouncementStatsSerializer(data=stats_service.get_stats())
        serializer.is_valid()
        return Response(serializer.data)
    

class AnnouncementCreateFromUrlView(APIView):
    API_DOMAIN = "https://www.bienici.com/realEstateAd.json"

    @staticmethod
    def _extract_id_from_url(request):
        """Extract the announcement ID from the provided URL."""
        url = request.data.get('url')
        
        if not url:
            return None, {'error': 'URL is required'}

        id_match = re.search(r'/([^/?]+)(?:\?|$)', url.split('?')[0].rstrip('/'))

        if not id_match:
            return None, {'error': 'Could not extract ID from URL'}
        
        return id_match.group(1), None

    @classmethod
    def _build_api_url(cls, announcement_id):
        """Build the API URL for fetching announcement data."""
        return f"{cls.API_DOMAIN}?id={announcement_id}"
    
    def _fetch_api_data(self, api_url):
        """Fetch data from the external API."""
        api_response = requests.get(api_url, timeout=10)

        if api_response.status_code != 200:
            return None, {'error': 'Failed to fetch data from external API'}
        
        api_data = api_response.json()

        if api_data.get('annualCondominiumFees') == 0:
            return None, {'error': 'Condominium expenses cannot be zero'}
        
        return api_data, None
    
    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'url': {
                        'type': 'string',
                        'description': 'URL of the announcement to scrape'
                    }
                },
                'required': ['url']
            }
        },
        responses={
            201: AnnouncementCreateSerializer,
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        },
        description='Create a new announcement by scraping data from a provided URL'
    )
    def post(self, request):
        """Create a new announcement by scraping data from a provided URL."""
        url_id, url_error = self._extract_id_from_url(request)

        if url_error:
            return Response(url_error, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            api_url = self._build_api_url(url_id)
            api_data, api_error = self._fetch_api_data(api_url)

            if api_error:
                return Response(api_error, status=status.HTTP_400_BAD_REQUEST)

            serializer = AnnouncementCreateSerializer(data=dict(
                url=api_url,
                reference=api_data.get('reference'),
                postal_code=api_data.get('postalCode'),
                city=api_data.get('city'),
                department=api_data.get('departmentCode'),
                condominium_expenses=api_data.get('annualCondominiumFees')
            ))

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(
                {'error': 'Invalid data from API', 'details': serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except requests.RequestException as e:
            return Response(
                {'error': f'Network error: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Internal error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    