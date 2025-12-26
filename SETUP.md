# Backend Setup Guide

## Step-by-Step Instructions

### 1. Install Python
- Download Python 3.8+ from python.org
- During installation, check "Add Python to PATH"

### 2. Setup Virtual Environment

Open PowerShell and run:

```powershell
cd C:\Users\sazna\6th_sem\Backend
python -m venv venv
.\venv\Scripts\activate
```

Your prompt should change to show `(venv)`.

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

This installs:
- Django 4.2.8
- Django REST Framework
- Channels (for WebSockets)
- And other required packages

### 4. Environment Configuration

Create `.env` file:

```powershell
cp .env.example .env
```

Edit `.env` with these values:
```
SECRET_KEY=django-insecure-your-secret-key-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=192.168.1.8,localhost,127.0.0.1
WEATHER_API_KEY=
```

**Note**: WEATHER_API_KEY is optional. Without it, the app uses dummy weather data.

To get a free weather API key (optional):
1. Visit https://openweathermap.org/api
2. Sign up for free account
3. Copy API key to .env file

### 5. Database Setup

```powershell
# Create database tables
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Admin Account

```powershell
python manage.py createsuperuser
```

Enter:
- Username: admin (or your choice)
- Email: your@email.com
- Password: (minimum 8 characters)

### 7. Load Sample Data

```powershell
python manage.py load_sample_data
```

This creates:
- 4 trekking destinations
- Route coordinates for each trek
- Chat rooms for each destination

### 8. Start the Server

For local network access (so your phone can connect):

```powershell
python manage.py runserver 192.168.1.8:8000
```

**IMPORTANT**: Replace `192.168.1.8` with your actual PC IP if different.

To find your IP:
```powershell
ipconfig
```

Look for "IPv4 Address" under your active network adapter.

### 9. Test the Backend

Open your browser and visit:

**Admin Panel**:
- URL: http://192.168.1.8:8000/admin
- Login with superuser credentials
- You can view/edit all data here

**API Endpoints**:
- http://192.168.1.8:8000/api/destinations/
- http://192.168.1.8:8000/api/auth/login/

You should see JSON data.

### 10. Configure Windows Firewall

To allow your phone to connect:

```powershell
# Run as Administrator
netsh advfirewall firewall add rule name="Django Dev Server" dir=in action=allow protocol=TCP localport=8000
```

Or manually:
1. Open Windows Defender Firewall
2. Advanced Settings → Inbound Rules → New Rule
3. Port → TCP → 8000 → Allow

## Common Issues

### Port Already in Use
If you see "Address already in use":
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F
```

### Cannot Connect from Phone
1. Verify PC and phone are on same WiFi
2. Check Windows Firewall allows port 8000
3. Verify IP address is correct: `ipconfig`
4. Try accessing from PC browser first

### Import Errors
Make sure virtual environment is activated:
```powershell
.\venv\Scripts\activate
```

You should see `(venv)` in your prompt.

### Database Errors
Reset database:
```powershell
del db.sqlite3
python manage.py migrate
python manage.py createsuperuser
python manage.py load_sample_data
```

## Development Tips

### View Database
You can use SQLite browser to view database:
- Download: https://sqlitebrowser.org/
- Open: `db.sqlite3`

### API Testing
Use Postman or Thunder Client (VS Code extension):
1. Import endpoints
2. Test authentication
3. Create test users

### Django Shell
Interactive Python shell with Django:
```powershell
python manage.py shell
```

Example:
```python
from api.models import Destination
destinations = Destination.objects.all()
print(destinations)
```

### View Logs
Django shows logs in the terminal where you ran `runserver`.
Watch for errors and API calls.

## Project Structure Explained

```
Backend/
├── trekking_app/          # Main project config
│   ├── settings.py        # App configuration
│   ├── urls.py            # Main URL routing
│   ├── asgi.py            # WebSocket config
│   └── wsgi.py            # Web server config
│
├── api/                   # Main application
│   ├── models.py          # Database models
│   ├── serializers.py     # JSON conversion
│   ├── views.py           # API logic
│   ├── urls.py            # API routes
│   ├── admin.py           # Admin interface
│   ├── consumers.py       # WebSocket handlers
│   └── management/        # Custom commands
│       └── commands/
│           └── load_sample_data.py
│
├── media/                 # Uploaded images (auto-created)
├── staticfiles/           # Static files (auto-created)
├── db.sqlite3             # Database file
├── manage.py              # Django CLI
└── requirements.txt       # Python packages
```

## Next Steps

After backend is running:
1. Keep this terminal open
2. Open new terminal for Flutter frontend
3. Follow Frontend Setup Guide

## Useful Commands

```powershell
# Activate environment
.\venv\Scripts\activate

# Deactivate environment
deactivate

# Run server
python manage.py runserver 192.168.1.8:8000

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic

# Load sample data
python manage.py load_sample_data
```

## API Documentation

### Authentication
```http
POST /api/auth/register/
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123",
  "password_confirm": "password123"
}

Response: {
  "user": {...},
  "token": "abc123..."
}
```

```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "testuser",
  "password": "password123"
}

Response: {
  "user": {...},
  "token": "abc123..."
}
```

### Destinations
```http
GET /api/destinations/

Response: {
  "results": [
    {
      "id": 1,
      "name": "Annapurna Base Camp Trek",
      "location": "Annapurna Region, Nepal",
      "altitude": 4130,
      "price": "750.00",
      ...
    }
  ]
}
```

All API requests (except login/register) require authentication:
```http
Authorization: Token <your-token-here>
```
