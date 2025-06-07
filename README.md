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

---

# Wristband Multi-Tenant Demo App for FastAPI (Python)

This repo contains a demo app showcasing Wristband authentication integration with a FastAPI backend and Next.js frontend. When an unauthenticated user attempts to access the frontend, it will redirect to the FastAPI backend's Login Endpoint, which in turn redirects the user to Wristband to authenticate. Wristband then redirects the user back to your application's Callback Endpoint which sets a session cookie before returning the user's browser to the frontend project.

<br>
<hr />
<br>

## Requirements

This demo app requires the following prerequisites:

### Python 3
1. Visit [Python Downloads](https://www.python.org/downloads/)
2. Download and install the latest Python 3 version
3. Verify the installation by opening a terminal or command prompt and running:
```bash
python --version # Should show Python 3.x.x
```

### Node.js and NPM
1. Visit [NPM Downloads](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)
2. Download and install the appropriate version for your OS
3. Verify the installation by opening a terminal or command prompt and running:
```bash
node --version # Should show v18.x.x or higher
npm --version  # Should show v8.x.x or higher
```

<br>
<hr>
<br>

## Getting Started

You can start up the demo application in a few simple steps.

### 1) Sign up for a Wristband account

First, make sure you sign up for a Wristband account at [https://wristband.dev](https://wristband.dev).

### 2) Provision the FastAPI demo application in the Wristband Dashboard

After your Wristband account is set up, log in to the Wristband dashboard.  Once you land on the home page of the dashboard, click the button labelled "Add Demo App".  Make sure you choose the following options:

- Step 1: Subject to Authenticate - Humans
- Step 2: Application Framework - FastAPI (Python)

You can also follow the [Demo App Guide](https://docs.wristband.dev/docs/setting-up-a-demo-app) for more information.

### 3) Apply your Wristband configuration values

After completing demo app creation, you will be prompted with values that you should use to create environment variables for the Express server. You should see:

- `APPLICATION_VANITY_DOMAIN`
- `CLIENT_ID`
- `CLIENT_SECRET`

Copy those values, then create an environment variable file for the FastAPI server at: `server/.env`. Once created, paste the copied values into this file.

### 4) Install dependencies & Activate Python VENV

You can install all required dependencies with a single command:

```bash
npm run setup
```

This will set up both the frontend and backend components.

### 5) Run the application

Once everything is set up, you can start the application with:

```bash
npm start

# run in debug mode
npm run start:debug
```

<br>
<hr>
<br>

## How to interact with the demo app

### Signup Users

Now that the demo app is up and running, you can sign up your first customer on the Signup Page at the following location:

- `https://{application_vanity_domain}/signup`, where `{application_vanity_domain}` should be replaced with the value of the "Application Vanity Domain" value of the application (found in the Wristband Dashboard).

This signup page is hosted by Wristband. Completing the signup form will provision both a new tenant with the specified tenant domain name and a new user that is assigned to that tenant.

### Application-level Login (Tenant Discovery)

Users of this app can access the Application-level Login Page at the following location:

- `https://{application_vanity_domain}/login`, where `{application_vanity_domain}` should be replaced with the value of the "Application Vanity Domain" value of the application.

This login page is hosted by Wristband. Here, the user will be prompted to enter either their email or their tenant's domain name, redirecting them to the Tenant-level Login Page for their specific tenant.

### Tenant-level Login

If users wish to directly access the Tenant-level Login Page without going through the Application-level Login Page, they can do so at:

- `https://localhost:6001/api/auth/login?tenant_domain={tenant_domain}`, where `{tenant_domain}` should be replaced with the desired tenant's domain name.

This login page is hosted by Wristband. Here, the user will be prompted to enter their credentials to login to the application.

### Architecture

This demo app consists of:

- **FastAPI Backend**: A Python backend with Wristband authentication integration
- **Next.js Frontend**: A modern React-based frontend with authentication context

The backend handles all authentication flows, including:
- Storing client ID and secret
- Handling OAuth2 authorization code flow redirections
- Managing session cookies
- Token refresh
- API orchestration

<br>
<hr>
<br>

## Manual Installation Guide

If you prefer to set up components individually:

### Backend Setup 🐍
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

### Frontend Setup 📦
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```


<br>
<hr>
<br>

## Questions

Reach out to the Wristband team at <support@wristband.dev> for any questions regarding this demo app.

<br/>
