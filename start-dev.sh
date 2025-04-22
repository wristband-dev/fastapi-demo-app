#!/bin/bash

# ANSI color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Wristband Python FastAPI Accelerator ===${NC}"
echo -e "${BLUE}=== Interactive Development Setup ===${NC}"

# Check if .env files exist
if [ ! -f ./backend/.env ]; then
  echo -e "${RED}Error: No .env file found in backend directory.${NC}"
  echo -e "${YELLOW}Please create backend/.env with required variables:${NC}"
  echo "CLIENT_ID=your_wristband_client_id"
  echo "CLIENT_SECRET=your_wristband_client_secret"
  echo "LOGIN_STATE_SECRET=your_secure_random_string"
  echo "LOGIN_URL=your_wristband_login_url"
  echo "REDIRECT_URI=https://localhost:8080/api/auth/callback"
  echo "APP_HOME_URL=http://localhost:3000"
  echo "SESSION_COOKIE_SECRET=your_secure_random_string"
  echo "SCOPES=['openid', 'offline_access', 'email']"
  exit 1
fi

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check Python
if command_exists python3; then
  PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
  echo -e "${GREEN}✓ Python found: ${PYTHON_VERSION}${NC}"
else
  echo -e "${RED}✗ Python 3 not found. Please install Python 3.11 or higher.${NC}"
  exit 1
fi

# Check Poetry
if command_exists poetry; then
  POETRY_VERSION=$(poetry --version 2>&1 | awk '{print $3}')
  echo -e "${GREEN}✓ Poetry found: ${POETRY_VERSION}${NC}"
else
  echo -e "${RED}✗ Poetry not found. Please install Poetry.${NC}"
  echo -e "${YELLOW}You can install it with: curl -sSL https://install.python-poetry.org | python3 -${NC}"
  exit 1
fi

# Check Node.js
if command_exists node; then
  NODE_VERSION=$(node --version)
  echo -e "${GREEN}✓ Node.js found: ${NODE_VERSION}${NC}"
else
  echo -e "${RED}✗ Node.js not found. Please install Node.js 16 or higher.${NC}"
  exit 1
fi

# Check npm
if command_exists npm; then
  NPM_VERSION=$(npm --version)
  echo -e "${GREEN}✓ npm found: ${NPM_VERSION}${NC}"
else
  echo -e "${RED}✗ npm not found. Please install npm.${NC}"
  exit 1
fi

echo -e "${GREEN}All prerequisites met!${NC}"

# Ask how to start the application
echo -e "${YELLOW}How would you like to start the application?${NC}"
echo "1) Start backend and frontend in separate terminals (recommended)"
echo "2) Start backend in the background and frontend in this terminal"
echo "3) Install dependencies only (don't start services)"
read -p "Enter your choice (1-3): " CHOICE

case $CHOICE in
  1)
    echo -e "${YELLOW}Starting backend in a new terminal window...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
      # macOS
      osascript -e 'tell application "Terminal" to do script "cd '$PWD'/backend && poetry install && poetry shell && uvicorn app:app --host 0.0.0.0 --port 8080 --reload"'
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
      # Linux
      if command_exists gnome-terminal; then
        gnome-terminal -- bash -c "cd '$PWD'/backend && poetry install && poetry shell && uvicorn app:app --host 0.0.0.0 --port 8080 --reload; exec bash"
      elif command_exists xterm; then
        xterm -e "cd '$PWD'/backend && poetry install && poetry shell && uvicorn app:app --host 0.0.0.0 --port 8080 --reload" &
      else
        echo -e "${RED}Cannot open a new terminal window. Please start the backend manually in a new terminal.${NC}"
        echo -e "${YELLOW}Run these commands in a new terminal:${NC}"
        echo "cd '$PWD'/backend"
        echo "poetry install"
        echo "poetry shell"
        echo "uvicorn app:app --host 0.0.0.0 --port 8080 --reload"
      fi
    else
      # Windows or other
      echo -e "${RED}Cannot open a new terminal window on this OS. Please start the backend manually in a new terminal.${NC}"
      echo -e "${YELLOW}Run these commands in a new terminal:${NC}"
      echo "cd '$PWD'/backend"
      echo "poetry install"
      echo "poetry shell"
      echo "uvicorn app:app --host 0.0.0.0 --port 8080 --reload"
    fi
    
    echo -e "${YELLOW}Starting frontend...${NC}"
    cd frontend
    npm install
    npm run dev
    ;;
    
  2)
    echo -e "${YELLOW}Starting backend in the background...${NC}"
    cd backend
    poetry install
    poetry run uvicorn app:app --host 0.0.0.0 --port 8080 --reload &
    BACKEND_PID=$!
    echo -e "${GREEN}Backend started with PID: ${BACKEND_PID}${NC}"
    
    echo -e "${YELLOW}Starting frontend...${NC}"
    cd ../frontend
    npm install
    npm run dev
    
    # Cleanup when script is terminated
    trap "kill $BACKEND_PID; echo -e '${YELLOW}Shutting down backend server...${NC}'" EXIT
    ;;
    
  3)
    echo -e "${YELLOW}Installing backend dependencies...${NC}"
    cd backend
    poetry install
    echo -e "${GREEN}Backend dependencies installed.${NC}"
    
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    cd ../frontend
    npm install
    echo -e "${GREEN}Frontend dependencies installed.${NC}"
    
    echo -e "${GREEN}All dependencies installed. You can now start the services manually:${NC}"
    echo -e "${YELLOW}Backend:${NC}"
    echo "cd backend"
    echo "poetry shell"
    echo "uvicorn app:app --host 0.0.0.0 --port 8080 --reload"
    echo -e "${YELLOW}Frontend:${NC}"
    echo "cd frontend"
    echo "npm run dev"
    ;;
    
  *)
    echo -e "${RED}Invalid choice.${NC}"
    exit 1
    ;;
esac

echo -e "${GREEN}Setup complete!${NC}"
echo -e "${BLUE}=== Testing Instructions ====${NC}"
echo -e "${YELLOW}1. Backend should be running at:${NC} http://localhost:8080"
echo -e "${YELLOW}   - Verify by visiting FastAPI docs:${NC} http://localhost:8080/docs"
echo -e "${YELLOW}2. Frontend should be running at:${NC} http://localhost:3000"
echo -e "${YELLOW}3. Test authentication by clicking login on the frontend${NC}"
echo -e "${YELLOW}   - This will redirect to Wristband${NC}"
echo -e "${YELLOW}   - After authentication, you should be redirected back to the app${NC}" 