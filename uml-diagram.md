classDiagram
    class Task {
        +String description
        +int duration
        +String frequency
        +String time
        +String priority
        +bool completed
        +date date
        +mark_complete() Task|None
        +__str__() String
    }

    class Pet {
        +String name
        +int age
        +Owner owner
        +Task[] tasks
        +add_task(task: Task)
        +get_pending_tasks() Task[]
        +__str__() String
    }

    class Owner {
        +String name
        +Pet[] pets
        +add_pet(pet: Pet)
        +schedule_task(pet: Pet, task: Task)
        +view_all_tasks() Task[]
        +__str__() String
    }

    class Scheduler {
        +get_all_tasks(owner: Owner) Task[]
        +get_pending_tasks(owner: Owner) Task[]
        +get_tasks_by_pet(owner: Owner) dict
        +get_tasks_by_frequency(owner: Owner, frequency: String) Task[]
        +sort_by_time(tasks: Task[]) Task[]
        +filter_by_status(tasks: Task[], completed: bool) Task[]
        +detect_conflicts(owner: Owner) String[]
    }

    Owner "1" *-- "0..*" Pet : owns
    Pet "0..*" --> "1" Owner : back-reference
    Pet "1" *-- "0..*" Task : has
    Task ..> Task : mark_complete() creates next Task
    Scheduler ..> Owner : uses

