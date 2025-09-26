from django.core.management.base import BaseCommand
from incidents.models import IncidentType


class Command(BaseCommand):
    help = 'Create initial incident types for the system'

    def handle(self, *args, **options):
        incident_types = [
            {
                'name': 'Safety Incident',
                'description': 'Workplace accidents, injuries, near misses',
                'color_code': '#dc3545'
            },
            {
                'name': 'Security Breach',
                'description': 'Unauthorized access, theft, security violations',
                'color_code': '#fd7e14'
            },
            {
                'name': 'Equipment Failure',
                'description': 'Machinery breakdown, equipment malfunction',
                'color_code': '#ffc107'
            },
            {
                'name': 'Environmental Issue',
                'description': 'Spills, contamination, environmental hazards',
                'color_code': '#28a745'
            },
            {
                'name': 'HR Incident',
                'description': 'Workplace harassment, discrimination, misconduct',
                'color_code': '#17a2b8'
            },
            {
                'name': 'IT Security',
                'description': 'Cyber attacks, data breaches, system compromises',
                'color_code': '#6f42c1'
            },
            {
                'name': 'Other',
                'description': 'General incidents not covered by other categories',
                'color_code': '#6c757d'
            }
        ]
        
        created_count = 0
        for incident_data in incident_types:
            incident_type, created = IncidentType.objects.get_or_create(
                name=incident_data['name'],
                defaults={
                    'description': incident_data['description'],
                    'color_code': incident_data['color_code']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created incident type: {incident_type.name}'
                    )
                )
            else:
                self.stdout.write(
                    f'Incident type already exists: {incident_type.name}'
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} incident types'
            )
        )