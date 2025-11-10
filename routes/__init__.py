# routes/__init__.py
from flask import Flask, jsonify
from flask_cors import CORS
import os
from services.database import Database
from services.uk_tree_service import UKTreeService
from services.custom_tree_service import CustomTreeService
from services.images import image_url_for_tree

def create_app(test_config=None):
    # Create Flask app instance
    app = Flask(__name__, instance_relative_config=True)
    
    # Enable CORS
    CORS(app)
    
    # Default configuration
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'UKTrees.db'),
    )
        
    # Make image_url_for_tree available in Jinja2 templates
    # Duplicate routes, clean up leaf imge handling
    # app.jinja_env.globals["image_url_for_tree"] = image_url_for_tree

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.update(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize database
    @app.before_first_request
    def init_db():
        db = Database()
        if not os.path.exists(app.config['DATABASE']):
            with app.app_context():
                db.get_connection()

    # Register blueprints
    from .tree_routes import tree_routes
    app.register_blueprint(tree_routes)

    # Basic health check route
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy'})

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'error': 'Internal server error'}), 500

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'error': 'Bad request'}), 400

    # CLI commands for database management
    @app.cli.command('init-db')
    def init_db_command():
        """Clear existing data and create new tables."""
        db = Database()
        db.get_connection()
        print('Initialized the database.')

    @app.cli.command('import-trees')
    def import_trees_command():
        """Import trees from CSV."""
        uk_service = UKTreeService()
        csv_path = os.path.join('data', 'UKTrees.csv')
        success, message = uk_service.import_uk_trees(csv_path)
        print(message)

    return app
