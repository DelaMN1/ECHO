from flask import Flask
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
import os
from config import config

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    bcrypt = Bcrypt(app)
    csrf = CSRFProtect(app)
    
    # Register blueprints
    from auth.routes import auth_bp
    from blog.routes import blog_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(blog_bp)
    
    # Initialize database
    from models import init_db
    init_db()
    
    return app

# Create the app instance for production
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)