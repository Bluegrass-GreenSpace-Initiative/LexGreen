# Installation Guide

## Prerequisites
- Python 3.10+
- Node.js 18+
- Git

## Detailed Setup Instructions

### 1. Initial Setup
```bash
# Clone repository
git clone https://github.com/Bluegrass-GreenSpace-Initiative/LexGreen.git
cd LexGreen

# Create and activate virtual environment
python -m venv venv

# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env  # Then edit .env with your settings

# Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 3. Frontend Setup
```bash
# Navigate to React directory
cd static/js/react

# Install dependencies
npm install

# Build frontend
npm run build
```

### 4. Running the Application
```bash
# Start Flask server (from project root)
flask run
```
Visit `http://localhost:5000` in your browser.

## Development Mode

Run backend and frontend development servers:

1. Backend (Terminal 1):
```bash
flask run --debug
```

2. Frontend (Terminal 2):
```bash
cd static/js/react
npm run dev
```

## Common Issues

### Backend Issues
- **"No module found"**: Ensure virtual environment is activated
- **Database errors**: Remove `migrations` folder and reinitialize

### Frontend Issues
- **Build fails**: Clear npm cache and node_modules
```bash
rm -rf node_modules
npm cache clean --force
npm install
```

## Verification Steps
1. Check `http://localhost:5000` loads
2. Verify map displays correctly
3. Confirm tree data appears

## Need Help?
- Open an issue on GitHub
- Contact team members listed in README.md

## Next Steps
- Read [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
