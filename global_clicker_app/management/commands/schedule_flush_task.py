from background_task.models import Task
from django.core.management.base import BaseCommand

from global_clicker_app.tasks import FLUSH_INTERVAL_SECONDS, flush_pending_clicks

TASK_NAME = "global_clicker_app.tasks.flush_pending_clicks"


class Command(BaseCommand):
    help = "Schedules the recurring pending-click flush task, if it isn't already scheduled."

    def handle(self, *args, **options):
        if Task.objects.filter(task_name=TASK_NAME).exists():
            self.stdout.write("Flush task already scheduled, skipping.")
            return

        flush_pending_clicks(schedule=FLUSH_INTERVAL_SECONDS, repeat=FLUSH_INTERVAL_SECONDS)
        self.stdout.write(f"Scheduled flush task to run every {FLUSH_INTERVAL_SECONDS}s.")
