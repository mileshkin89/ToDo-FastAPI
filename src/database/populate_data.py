from random import choice
from typing import Tuple

TASK_TEMPLATES: list[tuple[str, str]] = [
    # Work tasks
    ("Finish project", "Complete the current project and perform testing"),
    ("Prepare report", "Create a weekly progress report"),
    ("Hold meeting", "Organize and conduct a team meeting"),
    ("Study documentation", "Review new technical documentation"),
    ("Write code", "Implement new functionality"),
    ("Fix bugs", "Fix reported issues in the system"),
    ("Test feature", "Test newly implemented functionality"),

    # Personal tasks
    ("Pay utility bills", "Pay electricity and water bills"),
    ("Go shopping", "Buy groceries for the week"),
    ("Doctor appointment", "Schedule an appointment with a doctor"),
    ("Car maintenance", "Take the car for maintenance"),
    ("Clean the house", "Do a general house cleaning"),
    ("Call parents", "Call and visit parents"),
    ("Exercise", "Go to the gym or for a run"),

    # Study tasks
    ("Learn a new language", "Practice a foreign language for 30 minutes"),
    ("Read a book", "Read a professional development book"),
    ("Take online course", "Complete the next module of an online course"),
    ("Prepare for exam", "Review materials for the upcoming exam"),

    # Creative tasks
    ("Write an article", "Write an article for a blog or magazine"),
    ("Paint a picture", "Work on an art project"),
    ("Record a podcast", "Record a new podcast episode"),
]

TITLE_PREFIXES: list[str] = [
    "Urgent ",
    "Important ",
    "",
    "High priority ",
    "Planned ",
]

DESCRIPTION_DETAILS: list[str] = [
    "Double-check all details.",
    "Deadline is by the end of the week.",
    "Requires approval from the manager.",
    "High importance for the client.",
    "Needs to be done as soon as possible.",
    "This is a high-priority task.",
]


def get_random_task_data() -> Tuple[str, str]:
    """Return random task title and description."""
    title_template, base_description = choice(TASK_TEMPLATES)
    prefix = choice(TITLE_PREFIXES)
    detail = choice(DESCRIPTION_DETAILS)

    title = f"{prefix}{title_template}"
    description = f"{base_description}. {detail}"

    return title, description
