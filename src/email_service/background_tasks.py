from email_service.sender import send_email
from email_service.templates import (
    activation_email,
    deactivation_email,
    registration_email,
)


def send_notification(title: str, html: str, email: str, name: str | None):
    send_email(
        subject=title,
        to_email=email,
        html_content=html,
    )

    print(f"Email sent to '{email}' with name '{name}'.")


def send_registration_email(email: str, name: str | None):
    title, html = registration_email(name)

    send_notification(title, html, email, name)


def send_deactivate_account_email(email: str, name: str | None):
    title, html = deactivation_email(name)

    send_notification(title, html, email, name)


def send_activate_account_email(email: str, name: str | None):
    title, html = activation_email(name)

    send_notification(title, html, email, name)
