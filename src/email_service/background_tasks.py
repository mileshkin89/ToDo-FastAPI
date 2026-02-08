from email_service.sender import send_email
from email_service.templates import (
    activation_email,
    change_password_email,
    deactivation_email,
    registration_email,
    reset_password_email,
)


def send_notification(title: str, content: str, email: str):
    send_email(
        subject=title,
        to_email=email,
        html_content=content,
    )


def send_registration_email(email: str, name: str | None = None):
    title, content = registration_email(name)
    send_notification(title, content, email)


def send_deactivate_account_email(email: str, name: str | None = None):
    title, content = deactivation_email(name)
    send_notification(title,content, email)


def send_activate_account_email(email: str, name: str | None = None):
    title, content = activation_email(name)
    send_notification(title, content, email)


def send_change_password_email(email: str, name: str | None = None):
    title, content = change_password_email(name)
    send_notification(title, content, email)


def send_reset_password_email(email: str, link: str):
    title, content = reset_password_email(link)
    send_notification(title, content, email)