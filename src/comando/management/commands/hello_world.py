from typing import Any

from django.core.management import BaseCommand

class Command(BaseCommand):
    help=' writes hello word'
    def handle(self, *args: Any, **options: Any) :
       print("hello world")
