from typing import Optional


def registration_email(name: Optional[str] = None) -> tuple[str, str]:
    title = "Welcome to ToDo App"
    appeal = f"Welcome, {name} 👋" if name else "Welcome 👋"

    content = f"""
    <h2>{appeal}</h2>
    <p>Your account has been successfully created.</p>
    <p>You can now start managing your tasks and stay organized.</p>
    <p>We’re glad to have you on board.</p>
    """

    return title, content


def deactivation_email(name: Optional[str] = None) -> tuple[str, str]:
    title = "Your ToDo App Account Has Been Deactivated"

    appeal = f"Hello, {name}" if name else "Hello"

    content = f"""
    <h2>{appeal}</h2>
    <p>Your account has been deactivated.</p>
    <p>Access to your tasks and application features is currently restricted.</p>
    <p>If you believe this is a mistake or need further assistance, please contact the administrator.</p>
    """

    return title, content


def activation_email(name: Optional[str] = None) -> tuple[str, str]:
    title = "Your ToDo App Account Has Been Reactivated"

    appeal = f"Hello, {name}" if name else "Hello"

    content = f"""
    <h2>{appeal}</h2>
    <p>Your account has been successfully reactivated.</p>
    <p>All features and access to your tasks have been fully restored.</p>
    <p>You can continue managing your tasks as usual.</p>
    """

    return title, content


def change_password_email(name: Optional[str] = None) -> tuple[str, str]:
    title = "ToDo App — Password Changed Successfully"

    appeal = f"Hello, {name}" if name else "Hello"

    content = f"""
    <h2>{appeal}</h2>
    <p>This is a confirmation that your account password has been successfully changed.</p>
    <p>If you made this change, no further action is required.</p>
    <p>If you did <strong>not</strong> change your password, please contact our support team immediately.</p>
    """

    return title, content


def reset_password_email(link: str) -> tuple[str, str]:
    title = "ToDo App — Reset Password Request"

    content = f"""
    <h2>Hello</h2>
    <p>We received a request to reset the password for your ToDo App account.</p>
    <p>To proceed, please click the link below and follow the instructions:</p>

    <p>
        <a href="{link}" target="_blank">
            Reset your password
        </a>
    </p>

    <p>This link is valid for 15 minutes and can be used only once.</p>
    <p>If you did not request a password reset, you can safely ignore this email.</p>

    <br>
    <p>Best regards,<br>The ToDo App Team</p>
    """

    return title, content