# app.py - main entry point
# We import the factory function and use it to build our Flask app.
# In production (on Azure), gunicorn picks up the 'app' object directly.

from backend import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
