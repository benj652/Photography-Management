web: gunicorn --pythonpath . wsgi:app
release: python -c 'from website import create_app; app=create_app(); from website import db; with app.app_context(): db.create_all()'