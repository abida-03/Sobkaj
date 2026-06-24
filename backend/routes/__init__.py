# routes/__init__.py - collects all route modules and registers them on the app
# Each feature area (auth, worker, customer, admin) has its own file.

from backend.routes.auth import register_auth_routes
from backend.routes.worker import register_worker_routes
from backend.routes.customer import register_customer_routes
from backend.routes.admin import register_admin_routes


def register_all_routes(app):
    """Hooks up every route module to the Flask app instance."""
    register_auth_routes(app)
    register_worker_routes(app)
    register_customer_routes(app)
    register_admin_routes(app)
