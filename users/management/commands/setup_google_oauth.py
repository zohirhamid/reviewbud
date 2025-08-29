import os
from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Creates Google Social Application for OAuth'

    def handle(self, *args, **options):
        client_id = os.environ.get('OAUTH_GOOGLE_CLIENT_ID')
        secret = os.environ.get('OAUTH_GOOGLE_SECRET')
        
        if not client_id or not secret:
            self.stdout.write(
                self.style.ERROR('OAUTH_GOOGLE_CLIENT_ID and OAUTH_GOOGLE_SECRET must be set in environment variables')
            )
            return

        # Check if Google app already exists
        if SocialApp.objects.filter(provider='google').exists():
            self.stdout.write(
                self.style.WARNING('Google Social App already exists')
            )
            return

        # Create the social app
        app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id=client_id,
            secret=secret,
        )

        # Add all sites to the app
        sites = Site.objects.all()
        app.sites.set(sites)
        app.save()

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created Google Social App for sites: {[site.domain for site in sites]}')
        )