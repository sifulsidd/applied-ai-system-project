from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from itertools import combinations


@dataclass
class Task:
    description: str
    duration: int
    frequency: str
    time: str
    # ADDED: priority field to indicate task importance — "low", "medium", or "high" (defaults to "medium")
    priority: str = "medium"
    completed: bool = False
    date: date = field(default_factory=date.today)

    def mark_complete(self) -> "Task | None":
        """Mark this task as completed.

        For daily and weekly tasks, returns a new Task scheduled for the next
        occurrence (today + 1 day or today + 7 days). Returns None for monthly
        tasks or any other frequency.
        """
        self.completed = True
        if self.frequency == "daily":
            return Task(
                description=self.description,
                duration=self.duration,
                frequency=self.frequency,
                time=self.time,
                priority=self.priority,
                date=self.date + timedelta(days=1),
            )
        elif self.frequency == "weekly":
            return Task(
                description=self.description,
                duration=self.duration,
                frequency=self.frequency,
                time=self.time,
                priority=self.priority,
                date=self.date + timedelta(weeks=1),
            )
        return None

    def __str__(self) -> str:
        """Return a formatted string summary of the task."""
        status = "Done" if self.completed else "Pending"
        # ADDED: priority label included in the string output so it appears when tasks are printed
        return f"[{status}] [{self.priority.upper()}] {self.description} at {self.time} ({self.duration} mins, {self.frequency})"


@dataclass
class Pet:
    name: str
    age: int
    owner: Owner
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def get_pending_tasks(self) -> list[Task]:
        """Return all incomplete tasks for this pet."""
        return [task for task in self.tasks if not task.completed]

    def __str__(self) -> str:
        """Return the pet's name and age as a string."""
        return f"{self.name} (age {self.age})"


@dataclass
class Owner:
    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet):
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def schedule_task(self, pet: Pet, task: Task):
        """Assign a task to a specific pet."""
        pet.add_task(task)

    def view_all_tasks(self) -> list[Task]:
        """Return a flat list of all tasks across all owned pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def __str__(self) -> str:
        """Return the owner's name and number of pets as a string."""
        return f"Owner: {self.name} ({len(self.pets)} pets)"


@dataclass
class Scheduler:
    def get_all_tasks(self, owner: Owner) -> list[Task]:
        """Retrieve every task across all of the owner's pets."""
        return owner.view_all_tasks()

    def get_pending_tasks(self, owner: Owner) -> list[Task]:
        """Return only incomplete tasks across all of the owner's pets."""
        return [task for task in self.get_all_tasks(owner) if not task.completed]

    def get_tasks_by_pet(self, owner: Owner) -> dict[str, list[Task]]:
        """Return tasks grouped by pet name."""
        return {pet.name: pet.tasks for pet in owner.pets}

    def get_tasks_by_frequency(self, owner: Owner, frequency: str) -> list[Task]:
        """Return all tasks matching the given frequency across all pets."""
        return [task for task in self.get_all_tasks(owner) if task.frequency == frequency]

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted chronologically by their time attribute."""
        return sorted(tasks, key=lambda t: datetime.strptime(t.time, "%I:%M %p"))

    def filter_by_status(self, tasks: list[Task], completed: bool) -> list[Task]:
        """Return tasks matching the given completion status."""
        return [task for task in tasks if task.completed == completed]

    def detect_conflicts(self, owner: Owner) -> list[str]:
        """Check all tasks across all pets for scheduling overlaps.

        Two tasks conflict when their time windows overlap:
            start_a < end_b  and  start_b < end_a

        Returns a list of human-readable warning strings, one per conflict.
        Returns an empty list when no conflicts are found.
        """
        # Build a flat list of (pet_name, task) pairs so each task keeps its owner label
        labeled = [
            (pet.name, task)
            for pet in owner.pets
            for task in pet.tasks
        ]

        warnings = []
        for (pet_a, task_a), (pet_b, task_b) in combinations(labeled, 2):
            try:
                start_a = datetime.strptime(task_a.time, "%I:%M %p")
                start_b = datetime.strptime(task_b.time, "%I:%M %p")
            except ValueError:
                continue  # skip tasks with unparseable times rather than crashing

            end_a = start_a + timedelta(minutes=task_a.duration)
            end_b = start_b + timedelta(minutes=task_b.duration)

            if start_a < end_b and start_b < end_a:
                warnings.append(
                    f"WARNING: '{task_a.description}' ({pet_a}, {task_a.time}, {task_a.duration} mins) "
                    f"overlaps with '{task_b.description}' ({pet_b}, {task_b.time}, {task_b.duration} mins)."
                )

        return warnings
