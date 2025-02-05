# Setup

## Wristband Setup
1. Add Application
    - Create "Domain Name"
    - Create "Application Login URL"
        - https://localhost:8080/api/auth/login (local testing)
2. Add Oauth2 Client
    - backend server -> python
        - https://localhost:8080/api/auth/callback (local testing)

2.a. Create tenant


## Frontend 
- install axios
```
npm install axios
```

## Backend
- install poetry





# Outline
## Front End
**NEXT JS**


## Back End
**PYTHON**
- flask app
    - conainerized via dockerfile into google cloud run
- using wristband-firestore package to save documents to firestore with wristband authentication and tenant seperation
- firebase to store cookies for a users session


utils
- dynamically spin up a gcp instance
- user info endpoint with an access token to get tenant id


auth flow
- login endpoint in python server
- redirect to wristband url
- a cookie is set for wristband for the authentication
- callback endpoint 
- call to wristband oauth2 to get token and refresh




steps
- log in to readme
- read integration pattern docs

- first step hit the login endpoint and redirect