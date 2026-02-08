# Frontend for Smart ToDo FastAPI

This directory contains frontend files for the Smart ToDo application.

## Structure

```
frontend/
├── reset-password.html # HTML form for password reset
├── css/
│ └── reset-password.css # Styles for the password reset form
└──js/
  └── reset-password.js # JavaScript logic for the password reset form
```

## Usage

Frontend files are served by FastAPI as static files under the `/static/` path.

The password reset form is available at:

```
<BASE_URL>/api/v1/auth/reset_password?token=<token_from_email>
```
Note: In a production environment, this URL should be replaced with a frontend application URL.

## Development

All files are automatically mounted into the Docker container via `docker-compose.yml`.

Static assets (CSS, JS) are available at:

- `/static/css/reset-password.css`
- `/static/js/reset-password.js`
