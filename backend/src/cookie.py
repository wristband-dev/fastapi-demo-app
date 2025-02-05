from http import cookies

# Create a SimpleCookie instance
my_cookies = cookies.SimpleCookie()

# Set a cookie value
my_cookies["user_id"] = "12345"
my_cookies["user_id"]["path"] = "/"  # set cookie attributes
my_cookies["user_id"]["domain"] = "example.com"

# Generate the HTTP header string for the Set-Cookie header
set_cookie_header = my_cookies.output(header="Set-Cookie")
print(set_cookie_header)