import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from api.routes import api_bp
from utils.config import Config

import logging
from services.invoice_processor import InvoiceProcessor

logging.basicConfig(
    level=logging.INFO,  # or logging.DEBUG for more details
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
# Load environment variables
load_dotenv(override=True)

def create_app(config_class=Config):
    """Create and configure the Flask application"""
    app = Flask(__name__, static_folder='static')
    invoice_processor = InvoiceProcessor()
    app.config.from_object(config_class)
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    @app.route('/api/invoices_all', methods=['GET'])
    def get_invoices_all():
        results = invoice_processor.get_all_full_results()
        return jsonify(results)
    
    @app.route('/api/invoice_full/<invoice_id>', methods=['GET'])
    def get_invoice_full(invoice_id):
        # Get a single full invoice result by ID
        result = invoice_processor.get_full_result_by_id(invoice_id)
        if result:
            return jsonify(result)
        return jsonify({'error': 'Invoice not found'}), 404
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({"status": "ok"})
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"error": "Internal server error"}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
