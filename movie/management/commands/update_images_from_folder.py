import os
import unicodedata
from django.core.management.base import BaseCommand
from django.conf import settings
from movie.models import Movie

def normalize_name(s: str) -> str:
    """
    Normalize a string for matching:
     - lowercase
     - remove accents/diacritics
     - remove every non-alphanumeric character
    Example: "Castillo medieval" -> "castillomedieval"
    """
    if s is None:
        return ""
    s = s.strip().lower()
    s = unicodedata.normalize("NFKD", s)
    # drop combining characters (accents)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    # keep only alphanumeric characters
    s = "".join(ch for ch in s if ch.isalnum())
    return s

class Command(BaseCommand):
    help = "Assign images from media/movie/images/ to movies based on filenames 'm_<title>.<ext>'"

    def handle(self, *args, **kwargs):
        media_root = getattr(settings, "MEDIA_ROOT", "media")
        images_folder = os.path.join(media_root, "movie", "images")

        if not os.path.isdir(images_folder):
            self.stderr.write(self.style.ERROR(f"Images folder not found: {images_folder}"))
            return

        # Build mapping: normalized_title -> [filename, filename2, ...]
        files = [f for f in os.listdir(images_folder) if os.path.isfile(os.path.join(images_folder, f))]
        mapping = {}
        for f in files:
            # Only consider files that start with 'm_' (adjust if needed)
            if not f.lower().startswith("m_"):
                continue
            name_part = os.path.splitext(f)[0][2:]  # drop 'm_'
            key = normalize_name(name_part)
            mapping.setdefault(key, []).append(f)

        updated = 0
        not_found = 0
        multiple = 0

        for movie in Movie.objects.all():
            key = normalize_name(movie.title)
            candidates = mapping.get(key)
            if candidates:
                if len(candidates) > 1:
                    self.stdout.write(self.style.WARNING(
                        f"Multiple files for '{movie.title}': {candidates}. Using first."
                    ))
                    multiple += 1
                chosen = candidates[0]
                # Save relative path as stored by your ImageField (movie/images/...)
                movie.image = os.path.join("movie", "images", chosen)
                movie.save()
                self.stdout.write(self.style.SUCCESS(f"Updated image for: {movie.title} -> {chosen}"))
                updated += 1
            else:
                self.stderr.write(f"No image found for: {movie.title}")
                not_found += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done. Updated: {updated}. Not found: {not_found}. Multiple-file warnings: {multiple}."
        ))