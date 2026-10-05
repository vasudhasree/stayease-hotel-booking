# StayEase — Hotel Room Booking Web Application

A production-style full-stack mini project with separate Customer and Admin portals.

## Stack

- Frontend: React 18 + Vite + React Router + Axios + Tailwind CSS + Recharts
- Backend: Python 3.10+ + FastAPI + SQLAlchemy + Pydantic + python-jose JWT + passlib/bcrypt + Uvicorn
- Database: SQLite (`backend/hotel.db`), automatically created and seeded on first backend start

## Features

- Customer and Admin role-based portals with frontend `ProtectedRoute` and backend 403 role checks
- JWT authentication stored in `sessionStorage`
- Customer registration and profile/password management
- 20 seeded hotels, exactly 20 rooms per hotel (10 BIG, 5 MEDIUM, 5 SMALL)
- 8 seeded reviews per hotel across Good / Medium / Bad categories
- Room availability by date and backend overlap protection against double booking
- Booking lifecycle: Confirmed → Checked-in → Checked-out, or Cancelled
- Reviews allowed only after Checked-out; one review per booking
- Admin dashboard with statistics, charts, occupancy and top-rated hotels
- Live admin/customer updates using WebSockets plus 5-second polling fallback
- In-app notification bell and unread counts
- Booking reference numbers and printable confirmation page
- Hotel search, city filtering, sorting, review filtering, dark mode, responsive UI and 404 page
- Admin hotel/room APIs, customer list, review replies and booking management

## Windows 10/11 — exact setup

### 1. Install Python

Install Python 3.10 or newer from the official Python website. During installation, enable **Add Python to PATH**.

Verify in PowerShell:

```powershell
python --version
```

### 2. Install Node.js

Install the current Node.js LTS release. Verify:

```powershell
node --version
npm --version
```

### 3. Open the project in VS Code

Extract `hotel-booking.zip`, then open the extracted `hotel-booking` folder in VS Code.

### 4. Backend setup

Open a PowerShell terminal in VS Code:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run PowerShell as your normal user and execute:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate again:

```powershell
.\venv\Scripts\Activate.ps1
```

Optional: copy `.env.example` to `.env` and change `SECRET_KEY`.

Start the backend:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend URLs:

- API: http://127.0.0.1:8000
- Swagger docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/api/health

The first startup creates `backend/hotel.db` and seeds all demo data automatically.

### 5. Frontend setup

Keep the backend terminal running. Open a **second** PowerShell terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open:

- Frontend: http://localhost:5173

### 6. Demo credentials

Admin:

```text
Email: admin@stayease.com
Password: Admin@123
```

Customer:

```text
Email: customer@stayease.com
Password: Customer@123
```

Four extra sample customers are also seeded:

```text
sample1@stayease.com / Sample@123
sample2@stayease.com / Sample@223
sample3@stayease.com / Sample@323
sample4@stayease.com / Sample@423
```

### 7. Two browser tabs

Because the JWT is stored in `sessionStorage`, you can keep separate login sessions in separate browser tabs. For example, log in as Admin in one tab and Customer in another.

## Troubleshooting

### `python is not recognized`
Reinstall Python and enable **Add Python to PATH**, then restart VS Code/PowerShell.

### `node is not recognized`
Install Node.js LTS and restart the terminal.

### PowerShell says scripts are disabled
Run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port 8000 is already in use
Run the backend on another port:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

Then set `VITE_API_URL=http://localhost:8001` in `frontend/.env` and restart Vite.

### Port 5173 is already in use
Vite will normally offer another port. If you want a fixed port, stop the other Vite process or change `server.port` in `frontend/vite.config.js`.

### Database needs a fresh seed
Stop the backend and delete `backend/hotel.db`, then start the backend again. It will recreate and reseed the database.

### `ModuleNotFoundError`
Make sure the backend virtual environment is activated and run:

```powershell
pip install -r requirements.txt
```

### Frontend dependency errors
From `frontend` run:

```powershell
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json -ErrorAction SilentlyContinue
npm install
npm run dev
```

### Images do not load
Hotel cards use external Unsplash URLs and hide the image element if an image request fails, leaving the gradient placeholder visible. The booking system itself does not depend on remote images.

## Project structure

```text
hotel-booking/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── seed.py
│   │   └── utils.py
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── pages/
│   │   └── utils/
│   ├── package.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── vite.config.js
└── README.md
```

## Important implementation note

The project uses a real SQLite database and real REST/WebSocket endpoints rather than mocked frontend data. The only external dependency for seeded hotel photography is the free image-hosting URLs; the UI has a fallback gradient so image availability cannot stop the app from working.
