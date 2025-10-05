"""
Climate and Social Justice Map - Backend API
Flask application that provides RESTful endpoints for environmental,
socioeconomic, and democratic data integration.

Modular architecture with proper separation of concerns:
- api/: Route handlers
- services/: Business logic
- config/: Application configuration
- tests/: Test suite
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import os

# Import configuration
from config.settings import config

# Import blueprints (solo los que existen)
from api.routes import main_bp
from api.socioeconomic_routes import socioeconomic_bp
from api.country_routes import country_bp


def create_app(config_name='default'):
    """
    Application factory pattern
    
    Args:
        config_name (str): Configuration to use (development, production, testing)
        
    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    CORS(app)  # Enable CORS for frontend integration
    
    # Initialize cache
    cache = Cache(app)
    
    # Initialize rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        storage_uri=app.config['RATELIMIT_STORAGE_URL'],
        default_limits=[app.config['RATELIMIT_DEFAULT']]
    )
    
    # Apply rate limiting to blueprints
    limiter.limit("100 per hour")(socioeconomic_bp)
    limiter.exempt(main_bp)  # No rate limit for main routes
    limiter.exempt(country_bp)  # No rate limit for pre-calculated data
    
    # Apply caching to blueprints (1 hour)
    cache.cached(timeout=3600, query_string=True)(socioeconomic_bp)
    # No cache for country_bp - data is already cached in SQLite
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(socioeconomic_bp)
    app.register_blueprint(country_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return jsonify({
            "error": "Endpoint not found",
            "message": "The requested endpoint does not exist"
        }), 404
    
    @app.errorhandler(429)
    def ratelimit_exceeded(error):
        """Handle rate limit exceeded"""
        return jsonify({
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later."
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        return jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }), 500
    
    return app


if __name__ == '__main__':
    # Determine environment
    env = os.getenv('FLASK_ENV', 'development')
    
    # Create app
    app = create_app(env)
    
    # Get configuration
    port = app.config['PORT']
    host = app.config['HOST']
    debug = app.config['DEBUG']
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║  Climate and Social Justice Map API                       ║
    ║  Backend Server Starting...                               ║
    ║                                                           ║
    ║  Environment: {env:<43}                                   ║
    ║  Running on: http://{host}:{port:<31}                     ║
    ║  Debug mode: {str(debug):<43}                             ║
    ║                                                           ║
    ║  Features:                                                ║
    ║  ✓ Modular architecture                                   ║
    ║  ✓ Rate limiting (200/day, 50/hour)                       ║
    ║  ✓ Caching (1 hour)                                      ║
    ║  ✓ OpenStreetMap ready                                    ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    app.run(host=host, port=port, debug=debug)
