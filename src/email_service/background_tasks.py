from email_service.sender import send_email
from email_service.templates import registration_email


def send_notification(email: str, name: str):
    html = registration_email(name)

    send_email(
        subject="Welcome to ToDo App",
        to_email=email,
        html_content=html,
    )

    print(f"Email sent to '{email}' with name '{name}'.")