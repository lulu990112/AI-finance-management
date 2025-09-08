from django.core.management.base import BaseCommand
from api.models import Email
from django.utils import timezone


class Command(BaseCommand):
    help = 'Update GPT processing status fields for existing emails'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mark-processed',
            action='store_true',
            help='Mark all existing emails as processed',
        )
        parser.add_argument(
            '--mark-unprocessed',
            action='store_true',
            help='Mark all existing emails as unprocessed',
        )

    def handle(self, *args, **options):
        emails = Email.objects.all()
        total_emails = emails.count()
        
        if total_emails == 0:
            self.stdout.write(
                self.style.WARNING('No email records in database')
            )
            return
        
        self.stdout.write(f'Found {total_emails} emails')
        
        if options['mark_processed']:
            # Mark all emails as processed
            updated_count = emails.update(
                is_processed=True,
                processed_at=timezone.now()
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Marked {updated_count} emails as processed'
                )
            )
            
        elif options['mark_unprocessed']:
            # Mark all emails as unprocessed
            updated_count = emails.update(
                is_processed=False,
                processed_at=None
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Marked {updated_count} emails as unprocessed'
                )
            )
            
        else:
            # Default: mark as unprocessed so GPT can reprocess
            updated_count = emails.update(
                is_processed=False,
                processed_at=None
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Marked {updated_count} emails as unprocessed; ready for GPT reprocessing'
                )
            )
            
        # Show stats
        processed_count = Email.objects.filter(is_processed=True).count()
        unprocessed_count = Email.objects.filter(is_processed=False).count()
        
        self.stdout.write('\nCurrent status:')
        self.stdout.write(f'- Processed: {processed_count}')
        self.stdout.write(f'- Unprocessed: {unprocessed_count}')