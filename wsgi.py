from website import create_app

# Create the WSGI app at import time for Gunicorn/Heroku
app = create_app()