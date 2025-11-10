from __future__ import annotations

import os
from datetime import datetime
from flask import Flask
from flask_cors import CORS
from flask_compress import Compress


def create_app(config_object: object | None = None) -> Flask:
    """Application factory with scoped CORS and blueprint registration."""
    # Ensure templates/static resolve to project root folders
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder=os.path.join(root, 'templates'),
        static_folder=os.path.join(root, 'static'),
    )

    # Base configuration
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        SEND_FILE_MAX_AGE_DEFAULT=0,
        UPLOAD_FOLDER=os.path.join(app.instance_path, 'uploads'),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB
    )

    # Allow external config object (e.g., ProductionConfig)
    if config_object is not None:
        app.config.from_object(config_object)

    # Ensure instance and uploads directories exist
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Performance and CORS (scope to public API only)
    Compress(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    from routes.tree_routes import tree_routes
    from routes.admin_routes import admin_bp
    from .pages import pages_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(tree_routes)
    app.register_blueprint(admin_bp)

    # CLI commands
    _wire_cli(app)

    # Template globals/context
    _wire_template_context(app)

    return app


def _wire_template_context(app: Flask) -> None:
    from services.images import image_url_for_tree

    @app.context_processor
    def _globals():
        return {
            'current_year': datetime.now().year,
            'image_url_for_tree': image_url_for_tree,
        }


def _wire_cli(app: Flask) -> None:
    from services.database import Database
    from services.uk_tree_service import UKTreeService
    from services.photo_service import PhotoService
    from services.staff_service import StaffService
    from services.work_order_service import WorkOrderService
    import os

    @app.cli.command('init-db')
    def init_db_command():
        """Clear existing data and create new tables."""
        db = Database()
        conn = db.get_connection()
        with conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS trees (
                    tree_id INTEGER PRIMARY KEY,
                    common_name TEXT,
                    latin_name TEXT,
                    dbh REAL,
                    latitude REAL,
                    longitude REAL
                )
                """
            )
        PhotoService().ensure_tables()
        print('Initialized the database.')

    @app.cli.command('import-trees')
    def import_trees_command():
        """Import trees from CSV."""
        uk_service = UKTreeService()
        csv_path = os.path.join('data', 'UKTrees.csv')
        success, message = uk_service.import_uk_trees(csv_path)
        print(message)

    @app.cli.command('create-staff')
    def create_staff_command():
        """Create a staff user: supply EMAIL and PASSWORD env vars or be prompted."""
        import getpass
        email = os.environ.get('EMAIL') or input('Email: ').strip()
        name = os.environ.get('NAME') or ''
        password = os.environ.get('PASSWORD') or getpass.getpass('Password: ')
        ok, msg, sid = StaffService().create_staff(email, password, name=name)
        print(msg)

    @app.cli.command('export-work-orders')
    def export_work_orders_command():
        """Export work orders to CSV. Use SINCE (YYYY-MM-DD) and OUT path via env vars."""
        since = os.environ.get('SINCE')
        out = os.environ.get('OUT') or os.path.join(app.instance_path, 'exports', 'work_orders.csv')
        os.makedirs(os.path.dirname(out), exist_ok=True)
        csv_text = WorkOrderService().export_csv(since)
        with open(out, 'w', encoding='utf-8') as f:
            f.write(csv_text)
        print(f'Wrote {out}')

