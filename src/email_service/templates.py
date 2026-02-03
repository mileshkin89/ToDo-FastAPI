from typing import Optional


def registration_email(name: Optional[str] = None) -> str:
    title = f"Welcome, {name} 👋" if name else "Welcome 👋"

    return f"""
    <h2>{title}</h2>
    <p>Your account has been successfully created.</p>
    <p>Happy task managing!</p>
    """