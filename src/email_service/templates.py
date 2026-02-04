from typing import Optional


def registration_email(name: Optional[str] = None) -> tuple[str, str]:
    title = "Welcome to ToDo App"
    appeal = f"Welcome, {name} 👋" if name else "Welcome 👋"

    html = f"""
    <h2>{appeal}</h2>
    <p>Your account has been successfully created.</p>
    <p>You can now start managing your tasks and stay organized.</p>
    <p>We’re glad to have you on board.</p>
    """

    return title, html


def deactivation_email(name: Optional[str] = None) -> tuple[str, str]:
    title = "Your ToDo App Account Has Been Deactivated"

    appeal = f"Hello, {name}" if name else "Hello"

    html = f"""
    <h2>{appeal}</h2>
    <p>Your account has been deactivated.</p>
    <p>Access to your tasks and application features is currently restricted.</p>
    <p>If you believe this is a mistake or need further assistance, please contact the administrator.</p>
    """

    return title, html


def activation_email(name: Optional[str] = None) -> tuple[str, str]:
    title = "Your ToDo App Account Has Been Reactivated"

    appeal = f"Hello, {name}" if name else "Hello"

    html = f"""
    <h2>{appeal}</h2>
    <p>Your account has been successfully reactivated.</p>
    <p>All features and access to your tasks have been fully restored.</p>
    <p>You can continue managing your tasks as usual.</p>
    """

    return title, html
