from typing import Any
import helpers
from django.core.management import BaseCommand

class Command(BaseCommand):
    
    def handle(self, *args: Any, **options: Any) :
       print("hello word")