from flask import Blueprint, request, jsonify, current_app
import os
import uuid
from werkzeug.utils import secure_filename

from services.invoice_processor import InvoiceProcessor
from services.ocr_service import OCRService
from services.llm_service import LLMService
from models.invoice import Invoice

api_bp = Blueprint('api', __name__)
invoice_processor = InvoiceProcessor()

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@api_bp.route('/upload', methods=['POST'])
def upload_invoice():
    """
    Upload and process an energy invoice
    Returns processed invoice data with extracted information
    """
    # Check if file is in request
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    # Check if file is selected
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Check if file type is allowed
    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400
    
    # Generate unique filename
    filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    # Save file
    file.save(file_path)
    
    try:
        # Process invoice
        invoice_data = invoice_processor.process_invoice(file_path)
        return jsonify(invoice_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/invoices', methods=['GET'])
def get_invoices():
    """Get list of all processed invoices"""
    try:
        invoices = invoice_processor.get_all_invoices()
        return jsonify(invoices), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/invoices/<invoice_id>', methods=['GET'])
def get_invoice(invoice_id):
    """Get details for a specific invoice"""
    try:
        invoice = invoice_processor.get_invoice(invoice_id)
        if not invoice:
            return jsonify({"error": "Invoice not found"}), 404
        return jsonify(invoice), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/recommendations/<invoice_id>', methods=['GET'])
def get_recommendations(invoice_id):
    """Get recommendations for a specific invoice"""
    try:
        recommendations = invoice_processor.get_recommendations(invoice_id)
        if not recommendations:
            return jsonify({"error": "Recommendations not found"}), 404
        return jsonify(recommendations), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/analysis/<invoice_id>', methods=['GET'])
def get_analysis(invoice_id):
    """Get analysis for a specific invoice"""
    try:
        analysis = invoice_processor.get_analysis(invoice_id)
        if not analysis:
            return jsonify({"error": "Analysis not found"}), 404
        return jsonify(analysis), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
