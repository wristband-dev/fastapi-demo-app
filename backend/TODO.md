- log out
    - save refresh token and tenant domain name from session
    - clear session in the backend
    
    - revoke refresh token api (if fails -> it keeps going -> set a timeout)
    - redirect to the wristband logout endpoint


- refresh logic 
    - create auth middleware (sits on top of app to check before every api call)
        - makes sure you have a session cookie
            - check that is authenticated
            - return 401 if fails
        - refresh check 
            - if expired get another token from refresh token (token endpoint)
                - specify the grant type to get refresh token https://docs.wristband.dev/reference/tokenv1