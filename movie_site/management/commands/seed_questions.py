import json
from pathlib import Path
from django.core.management.base import BaseCommand
from movie_site.models import Question

class Command(BaseCommand):
    help = "Seed quiz questions into the database"

    def handle(self, *args, **kwargs):
        path = Path("movie_site/static/movie_site/data/questions.json")

        if not path.exists():
            self.stdout.write(self.style.ERROR("questions.json not found"))
            return

        with open(path, "r", encoding="utf-8") as f:
            questions = json.load(f)

        created = 0

        for q in questions:
            _, is_created = Question.objects.get_or_create(
                text=q["text"],
                defaults={
                    "option_a": q["option_a"],
                    "option_b": q["option_b"],
                    "option_c": q["option_c"],
                    "option_d": q["option_d"],
                    "correct_option": q["correct_option"],
                }
            )
            if is_created:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(f"{created} questions added 🎉")
        )
