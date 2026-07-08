from pawpal_system import Pet, Task


def test_task_completion_marks_task_completed() -> None:
    task = Task(title="Feed", duration_minutes=10, priority="high")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_to_pet_increases_task_count() -> None:
    pet = Pet(name="Mochi", species="cat")
    assert len(pet.tasks) == 0

    task = Task(title="Play", duration_minutes=20, priority="medium")
    pet.add_task(task)

    assert len(pet.tasks) == 1
    assert pet.tasks[0] is task
