from django.core.management.base import BaseCommand
from django.db.models import Q
from django.conf import settings
from decouple import config
import requests

from students.models import Student


class Command(BaseCommand):
    help = "Backfill pending/missing face embeddings to FAISS via AI service."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Max number of students to process (0 means no limit)",
        )
        parser.add_argument(
            "--timeout",
            type=int,
            default=15,
            help="HTTP timeout in seconds for AI service calls",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        timeout = options["timeout"]

        ai_url = config("AI_SERVICE_URL", default="http://localhost:8001").rstrip("/")
        register_endpoint = f"{ai_url}/api/face/register"

        qs = Student.objects.filter(
            Q(face_embedding_id__isnull=True)
            | Q(face_embedding_id__startswith="pending_")
            | Q(face_embedding_id__exact="")
        ).exclude(face_image="")

        if limit > 0:
            qs = qs[:limit]

        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS("No pending students to backfill."))
            return

        self.stdout.write(
            f"Processing {total} student(s) -> AI register endpoint: {register_endpoint}"
        )

        processed = 0
        succeeded = 0
        failed = 0

        for student in qs.iterator():
            processed += 1
            if not student.face_image:
                failed += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"[{processed}/{total}] {student.roll_number}: No face image present, skipping"
                    )
                )
                continue

            try:
                with student.face_image.open("rb") as f:
                    files = {
                        "file": (student.face_image.name.split("/")[-1], f, "image/jpeg"),
                    }
                    data = {"student_id": str(student.id)}
                    resp = requests.post(register_endpoint, files=files, data=data, timeout=timeout)

                if resp.status_code == 200:
                    payload = resp.json()
                    embedding_id = payload.get("embedding_id") or str(student.id)
                    student.face_embedding_id = embedding_id
                    student.save(update_fields=["face_embedding_id"])
                    succeeded += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"[{processed}/{total}] {student.roll_number}: Embedding saved -> {embedding_id}"
                        )
                    )
                else:
                    failed += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f"[{processed}/{total}] {student.roll_number}: AI service HTTP {resp.status_code}"
                        )
                    )
            except requests.RequestException as e:
                failed += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"[{processed}/{total}] {student.roll_number}: Network error -> {e}"
                    )
                )
            except Exception as e:
                failed += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"[{processed}/{total}] {student.roll_number}: Unexpected error -> {e}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. processed={processed} succeeded={succeeded} failed={failed}"
            )
        )
