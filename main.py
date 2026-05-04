from pawpal_system import Task, Pet, Owner, Scheduler


def main():
    # Create owner
    owner = Owner(name="Alex")

    # Create pets
    buddy = Pet(name="Buddy", age=3, owner=owner)
    luna = Pet(name="Luna", age=5, owner=owner)

    # Add pets to owner
    owner.add_pet(buddy)
    owner.add_pet(luna)

    # Assign tasks to Buddy
    # ADDED: priority argument on each Task to reflect how urgent the task is
    owner.schedule_task(buddy, Task(description="Morning walk", duration=30, frequency="daily", time="07:00 AM", priority="high"))
    owner.schedule_task(buddy, Task(description="Feed breakfast", duration=10, frequency="daily", time="08:00 AM", priority="high"))

    # Assign tasks to Luna
    # ADDED: priority argument on each Task to reflect how urgent the task is
    owner.schedule_task(luna, Task(description="Vet checkup", duration=60, frequency="monthly", time="10:00 AM", priority="high"))
    owner.schedule_task(luna, Task(description="Evening walk", duration=20, frequency="daily", time="06:00 PM", priority="medium"))
    owner.schedule_task(luna, Task(description="Bath time", duration=45, frequency="weekly", time="02:00 PM", priority="low"))
    # Intentional conflict: overlaps Buddy's "Morning walk" (07:00 AM, 30 mins)
    owner.schedule_task(luna, Task(description="Morning grooming", duration=15, frequency="daily", time="07:15 AM", priority="medium"))

    # Use Scheduler to retrieve and display tasks
    scheduler = Scheduler()

    print("=" * 40)
    print("        TODAY'S SCHEDULE")
    print("=" * 40)

    tasks_by_pet = scheduler.get_tasks_by_pet(owner)
    for pet_name, tasks in tasks_by_pet.items():
        print(f"\n{pet_name}:")
        for task in tasks:
            print(f"  - {task}")

    print("\n" + "=" * 40)
    print(f"Total tasks:   {len(scheduler.get_all_tasks(owner))}")
    print(f"Pending tasks: {len(scheduler.get_pending_tasks(owner))}")
    print("=" * 40)

    print("\n" + "=" * 40)
    print("      CONFLICT DETECTION")
    print("=" * 40)
    conflicts = scheduler.detect_conflicts(owner)
    if conflicts:
        for warning in conflicts:
            print(f"\n{warning}")
    else:
        print("\nNo scheduling conflicts found.")
    print("=" * 40)

    # Demonstrate mark_complete() auto-scheduling the next occurrence
    print("\n" + "=" * 40)
    print("     COMPLETING A TASK DEMO")
    print("=" * 40)

    morning_walk = buddy.tasks[0]
    print(f"\nCompleting: {morning_walk}")
    next_task = morning_walk.mark_complete()
    if next_task:
        buddy.add_task(next_task)
        print(f"Next occurrence scheduled: {next_task.description} on {next_task.date}")

    bath_time = luna.tasks[2]
    print(f"\nCompleting: {bath_time}")
    next_task = bath_time.mark_complete()
    if next_task:
        luna.add_task(next_task)
        print(f"Next occurrence scheduled: {next_task.description} on {next_task.date}")

    vet_checkup = luna.tasks[0]
    print(f"\nCompleting: {vet_checkup}")
    next_task = vet_checkup.mark_complete()
    if next_task:
        luna.add_task(next_task)
    else:
        print(f"Monthly task — no auto-scheduling. Book next appointment manually.")

    print("\n" + "=" * 40)
    print(f"Pending tasks after completions: {len(scheduler.get_pending_tasks(owner))}")
    print("=" * 40)


if __name__ == "__main__":
    main()
