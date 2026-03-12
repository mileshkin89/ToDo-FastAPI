# Smart ToDo — Frontend

React SPA for the Smart ToDo application. Built with Vite, TypeScript, and React Router. Uses the backend API described in the project's OpenAPI spec.

## Structure

```
frontend/
├── public/
│   ├── favicon.svg
│   └── legacy/              # Legacy reset-password (HTML/CSS/JS) for email links
│       ├── reset-password.html
│       ├── css/
│       └── js/
├── src/
│   ├── api/                 # API client, types, auth/tasks/admin/analytics
│   ├── components/          # Button, Input, Card, Modal, Sidebar, Header
│   ├── context/             # AuthContext
│   ├── layouts/             # AuthLayout, MainLayout
│   ├── pages/               # Login, Register, Tasks, Analytics, Settings, Admin, Reset password
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── index.html
├── vite.config.ts
├── package.json
├── tsconfig.json
└── .env.example
```

## Commands

```bash
npm install
npm run dev      # Dev server (proxy to API)
npm run build    # Output to dist/
npm run preview  # Preview production build
```

## Configuration

- **`VITE_API_BASE_URL`** — Base URL of the backend API (no trailing slash).  
  Example: `http://localhost:8000`  
  If unset, the app uses relative URLs (same origin). For local dev with Vite, the dev server proxies `/api` to the value of `VITE_API_BASE_URL` when set; you can leave it unset and run the backend on the same host, or set it to the backend URL.

Copy `.env.example` to `.env` and adjust:

```bash
cp .env.example .env
```

## Deploying separately

The frontend can be run as a separate project or server:

1. Copy this `frontend/` directory (without `node_modules` and `dist`).
2. Set `VITE_API_BASE_URL` to your backend URL (e.g. `https://api.example.com`).
3. Run `npm install` and `npm run build`.
4. Serve the `dist/` folder with any static server (Nginx, Netlify, Vercel, etc.).
5. Ensure the backend allows CORS from the frontend origin.

Legacy reset-password (from email links) is in `public/legacy/`. When built, it is available at `/legacy/reset-password.html`. For production, you can either keep using the SPA route `/reset-password?token=...` in emails or point users to the legacy page if needed.
