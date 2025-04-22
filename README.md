# Wristband Python FastAPI Accelerator

A full-stack application accelerator showcasing Wristband authentication integration with a FastAPI backend and Next.js frontend. This repository provides a production-ready foundation for building secure, multi-tenant web applications with enterprise-grade authentication.

## Overview

This accelerator provides:

- **FastAPI Backend**: A Python backend with Wristband authentication integration
- **Next.js Frontend**: A modern React-based frontend with authentication context
- **Multi-Tenant Support**: Full support for Wristband's multi-tenant capabilities
- **OAuth 2.0 Flow**: Complete implementation of the OAuth 2.0 authentication flow

## Architecture

The application follows a modern microservice architecture:

- **Frontend**: Next.js (React) application with authentication context
- **Backend**: FastAPI server handling authentication and business logic
- **Authentication**: Integration with Wristband for secure, multi-tenant authentication


## Setup Instructions

### Wristband Configuration

1. Create an application in Wristband:
   - Configure Application Domain Name
   - Set Application Login URL: `https://localhost:8080/api/auth/login` (for local testing)

2. Add OAuth2 Client:
   - Set platform to "Python"
   - Set callback URL: `https://localhost:8080/api/auth/callback` (for local testing)

3. Create a tenant in Wristband

### Environment Variables

Create `.env` files in both frontend and backend directories with the following configurations:

#### Backend `.env` Variables:
```
CLIENT_ID=your_wristband_client_id
CLIENT_SECRET=your_wristband_client_secret
LOGIN_STATE_SECRET=your_secure_random_string
LOGIN_URL=your_wristband_login_url
REDIRECT_URI=https://localhost:8080/api/auth/callback
APP_HOME_URL=http://localhost:3000
SESSION_COOKIE_SECRET=your_secure_random_string
SCOPES=['openid', 'offline_access', 'email']
```

### Backend Setup

1. Navigate to the backend directory:
```
cd backend
```

2. Install dependencies:
```
pip install poetry
poetry install
```

3. Start the FastAPI server:
```
uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

### Frontend Setup

1. Navigate to the frontend directory:
```
cd frontend
```

2. Install dependencies:
```
npm install
```

3. Start the development server:
```
npm run dev
```

4. Access the application at [http://localhost:3000](http://localhost:3000)

## Boot Up

To get the entire application running, you have several options:

### Quick Start Command

Simply run this command from the project root:

```bash
./run
```

This simple command will launch the interactive startup script that helps you set up both the backend and frontend.

### Manual Options

If you prefer to start the services manually:

#### Option 1: Using Multiple Terminal Windows

#### Terminal 1 - Backend
```bash
cd backend
poetry shell
uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

#### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

#### Option 2: Using a Single Terminal with Background Processes

```bash
# Start the backend
cd backend
poetry shell
uvicorn app:app --host 0.0.0.0 --port 8080 --reload &

# Start the frontend
cd ../frontend
npm run dev
```

### Verifying the Setup

1. Backend should be running at: http://localhost:8080
   - You can verify by visiting http://localhost:8080/docs to see the FastAPI documentation

2. Frontend should be running at: http://localhost:3000
   - You should see the application's home page

3. Test authentication by clicking the login button on the frontend
   - This should redirect you to Wristband for authentication
   - After successful authentication, you should be redirected back to the application

## Prerequisites

- Python 3.11+
- Node.js 16+
- Poetry (Python package manager)
- npm or yarn
- Wristband account and configuration

## Prerequisite Installation

### Python 3.11+
#### macOS
```bash
brew install python@3.11
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

#### Windows
Download and install from [python.org](https://www.python.org/downloads/)

### Node.js 16+
#### macOS
```bash
brew install node
```

#### Ubuntu/Debian
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs
```

#### Windows
Download and install from [nodejs.org](https://nodejs.org/)

### Poetry
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
or
```bash
pip install poetry
```

## Authentication Flow

1. User clicks login on the frontend
2. Frontend redirects to backend login endpoint
3. Backend redirects to Wristband authentication
4. User authenticates with Wristband
5. Wristband redirects to callback endpoint with auth code
6. Backend exchanges auth code for tokens
7. Session cookie is created and returned to frontend
8. Frontend uses session cookie for authenticated requests

## Development Guidelines

- **Backend**: Extend the FastAPI application in the `backend/src` directory
- **Frontend**: Build new pages in the `frontend/src/pages` directory
- **Authentication**: The authentication flow is handled by the Wristband SDK

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the terms of the MIT license.

## Resources

- [Wristband Documentation](https://docs.wristband.dev)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Next.js Documentation](https://nextjs.org/docs)