<div align="center">
  <a href="https://wristband.dev">
    <picture>
      <img src="https://assets.wristband.dev/images/email_branding_logo_v1.png" alt="Github" width="297" height="64">
    </picture>
  </a>
  <p align="center">
    Enterprise-ready auth that is secure by default, truly multi-tenant, and ungated for small businesses.
  </p>
  <p align="center">
    <b>
      <a href="https://wristband.dev">Website</a> •
      <a href="https://docs.wristband.dev">Documentation</a>
    </b>
  </p>
</div>

<br/>


# Wristband Python FastAPI Accelerator


A full-stack application accelerator showcasing Wristband authentication integration with a FastAPI backend and Next.js frontend. This repository provides a production-ready foundation for building secure, multi-tenant web applications with enterprise-grade authentication.


## Architecture

- **FastAPI Backend**: A Python backend with Wristband authentication integration
- **Next.js Frontend**: A modern React-based frontend with authentication context
- **Firestore Database**: A NoSQL document database for storing application data with flexible schema support
- **(OPTIONAL) Google Cloud Provider**: Integration with Google Cloud Platform for hosting and additional services


## Setup

### 1. Fork the Repository

1. Click the "Fork" button at the top right of this GitHub repository.
2. This will create a copy of the repository in your GitHub account.
3. Clone your forked repository to your local machine:
   ```bash
   git clone https://github.com/wristband-dev/python-accelerator.git
   cd wristband-python-fastapi-accelerator
   ```
4. (Optional) Keep your fork in sync with the original repository:
   ```bash
   # Add the original repository as a remote called "upstream"
   git remote add upstream https://github.com/wristband-dev/python-accelerator.git
   
   # Fetch changes from the upstream repository
   git fetch upstream
   
   # Merge changes from upstream into your local main branch
   git checkout main
   git merge upstream/main
   ```


### 2. Wristband Configuration (TODO - JIM TO ADD WRISTBAD DEMO APP TO DASHBOARD)
1. Create an application in Wristband:
   - Configure Application Domain Name
   - Set Application Login URL: `https://localhost:8080/api/auth/login` (for local testing)
2. Add OAuth2 Client:
   - Set platform to "Python"
   - Set callback URL: `https://localhost:8080/api/auth/callback` (for local testing)
3. Create a tenant in Wristband


### 3. Environment Variables
1. Create environemnt varirable file
   ```bash
   cp .env.example .env
   ```
2. Add in the following required variables
   ```
   CLIENT_ID="CLIENT_ID"
   CLIENT_SECRET="CLIENT_SECRET"
   LOGIN_STATE_SECRET="LOGIN_STATE_SECRET"
   WRISTBAND_APPLICATION_DOMAIN="WRISTBAND_APPLICATION_DOMAIN"
   ```

   
TODO - OR just get from export file

### 4. Install Local Packages
```bash
npm install
```
[Manual Local Package Installation](#install-local-packages)



## Local Start Up
```bash
npm start
```
[Manual Start Up](#local-start-up)



## Deployment
   1. Publish Fast Api app to google cloud run
      - dockerize python env
      - build
      ```bash
      docker build -t wristband-backend -f backend/Dockerfile .
      ```
      - run 
      ```bash
      docker run --env-file .env -p 8080:8080 wristband-backend
      ```
   2. Host firestore database in firebase
   3. Publish the frontend (next js) to vercel


---


## Manual Installation
### Install Local Packages
#### Backend Setup 🐍
```bash
# Navigate to backend directory
cd backend

# Option A: Pip Installation
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Option B: Poetry Installation (Optional)
poetry install
```
#### Database Setup 📀
```bash
# install firebase cli globally
npm install -g firebase-tools

# login
firebase login
```
#### Frontend Setup 📦
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```
### Local Start Up
#### Start Backend API 🐍
```
cd backend
python3 run.py
```
#### Start Backend Database 📀
```
cd backend
# dynamic config file vars
node ./scripts/run-database.js

# hardcoded values (need to assign env vars to be able to access the database in the py env)
firebase emulators:start --only firestore --project wristband-fastapi-demo
```
#### Start Frontend 📦
```
cd frontend
npm run dev
```