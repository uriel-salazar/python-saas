from typing import Any
from django.conf import settings
from django.core.management import BaseCommand
from helpers.downloader import download_to_local

VENDOR_STATICFILES = {
    "flowbite.min.css": "https://cdnjs.cloudflare.com/ajax/libs/flowbite/2.3.0/flowbite.min.css",
    "flowbite.min.js": "https://cdnjs.cloudflare.com/ajax/libs/flowbite/2.3.0/flowbite.min.js"
}

STATICFILES_VENDOR_DIR = getattr(settings, 'STATICFILES_VENDOR_DIR')

class Command(BaseCommand):
    help = 'Downloads vendor static files from CDN'
    
    def handle(self, *args: Any, **options: Any):
        print("Downloading vendor static files")
        completed_urls = []
        for name, url in VENDOR_STATICFILES.items():
            out_path = STATICFILES_VENDOR_DIR / name
            dl_success = download_to_local(url, out_path)
            self.stdout.write(f"Downloading {name} from {url} to {str(out_path)}")
            if dl_success:
                completed_urls.append(url)
            else:
                self.stdout.write(
                    f"Failed to download {url}"
                )
        if set(completed_urls) == set(VENDOR_STATICFILES.values()):
            self.stdout.write(
                self.style.SUCCESS("Successfully updated your static files")
            )
        else:
            self.stdout.write(
                self.style.WARNING("We couldn't updated your static files.")
            )
