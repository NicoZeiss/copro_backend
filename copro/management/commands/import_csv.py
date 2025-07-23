import os
import logging

from django.conf import settings
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError

from copro.models import Announcement
from copro.utils import CSVCol, CSVService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import data from CSV file into database"

    def add_arguments(self, parser):
        """Add command line arguments for the CSV import command."""
        parser.add_argument('csv_file_name', type=str, help='CSV file name')
        parser.add_argument(
            '--chunksize',
            type=int,
            default=50_000,
            help='Number of records to process per chunk (default: 100000)'
        )

    @staticmethod
    def _get_csv_file(**kwargs):
        csv_file_name = kwargs.get('csv_file_name')
        
        resources_dir = os.path.join(settings.BASE_DIR, 'copro', 'resources')
        csv_file = os.path.join(resources_dir, csv_file_name)

        if not os.path.exists(csv_file):
            raise CommandError(f'File "{csv_file}" not found in copro/resources/')
        
        return csv_file
    
    @staticmethod
    def _convert_to_object(record, existing_refs):
        """Convert a DataFrame record to an Announcement object."""
        record_dict = record.to_dict()
        return (
            None
            if record_dict[CSVCol.REFERENCE_NUMBER.label] in existing_refs
            else Announcement(
                reference=record_dict[CSVCol.REFERENCE_NUMBER.label],
                department=record_dict[CSVCol.DEPT_CODE.label],
                city=record_dict[CSVCol.CITY.label],
                postal_code=record_dict[CSVCol.ZIP_CODE.label],
                url=record_dict[CSVCol.AD_URLS.label],
                condominium_expenses=record_dict[CSVCol.CONDOMINIUM_EXPENSES.label],
            )
        )
    
    @staticmethod
    def _get_exiting_refs(chunk):
        """Get a set of existing announcement references from the database for a chunk of data."""
        return set(
            Announcement.objects.filter(
                reference__in=chunk[CSVCol.REFERENCE_NUMBER.label].tolist()
            ).values_list('reference', flat=True)
        )
    
    def _get_announcements_to_create(self, chunk):
        """Get a list of Announcement objects to create from a chunk of data."""
        existing_refs = self._get_exiting_refs(chunk)
        return [
            announcement
            for _, record in chunk.iterrows()
            if (announcement:=self._convert_to_object(record, existing_refs))
        ]

    def _process_chunk(self, chunk):
        """Bulk create Announcement objects from a chunk of data."""
        
        logger.info(f"Processing chunk with {len(chunk)} records")
        created_count = 0
        announcements_to_create = self._get_announcements_to_create(chunk)

        try:
            with transaction.atomic():
                Announcement.objects.bulk_create(
                    announcements_to_create, 
                    ignore_conflicts=True
                )

            created_count = len(announcements_to_create)
            logger.info(f"Processed chunk: {created_count} new records created")
            return created_count

        except Exception as e:
            logger.error(f"Error preparing record: {e}")
    
    def handle(self, *args, **kwargs):
        """Handle the command execution."""
        csv_file = self._get_csv_file(**kwargs)

        try:
            csv_service = CSVService(csv_file, chunksize=kwargs.get('chunksize'))
            total_created = sum(self._process_chunk(chunk) for chunk in csv_service.get_cleaned_chunks())
            
            logger.info(f"Import completed: {total_created} total new announcements created.")

        except FileNotFoundError:
            raise CommandError(f'File "{csv_file}" not found')
        except Exception as e:
            raise CommandError(f'Error reading CSV file: {e}')
