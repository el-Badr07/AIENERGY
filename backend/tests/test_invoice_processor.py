import os
import unittest
import json
from unittest.mock import patch, MagicMock

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.invoice_processor import InvoiceProcessor
from services.ocr_service import OCRService
from services.llm_service import LLMService

class TestInvoiceProcessor(unittest.TestCase):
    """Test cases for the InvoiceProcessor service"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock OCR service
        self.mock_ocr = MagicMock(spec=OCRService)
        self.mock_ocr.process_file.return_value = "Sample OCR text from an energy invoice"
        
        # Create a mock LLM service
        self.mock_llm = MagicMock(spec=LLMService)
        self.mock_llm.extract_invoice_data.return_value = {
            "provider": "Energy Co",
            "invoice_number": "INV-12345",
            "issue_date": "2025-05-01",
            "due_date": "2025-05-31",
            "customer_name": "John Doe",
            "customer_id": "CUST-6789",
            "total_amount": 150.75,
            "period_start": "2025-04-01",
            "period_end": "2025-04-30",
            "total_kwh": 500,
            "rate_per_kwh": 0.25,
            "peak_kwh": 300,
            "off_peak_kwh": 200,
            "items": [
                {"description": "Energy usage", "quantity": 500, "unit_price": 0.25, "total": 125.00},
                {"description": "Service fee", "quantity": 1, "unit_price": 15.00, "total": 15.00}
            ],
            "taxes": {"VAT": 10.75}
        }
        
        self.mock_llm.analyze_invoice.return_value = {
            "issues": ["High energy consumption compared to average"],
            "severity": ["medium"]
        }
        
        self.mock_llm.generate_recommendations.return_value = {
            "recommendations": [
                "Switch to energy-efficient appliances",
                "Consider installing solar panels"
            ],
            "potential_savings": 45.25,
            "efficiency_score": 70
        }
        
        # Create a temporary data directory
        self.test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        os.makedirs(self.test_data_dir, exist_ok=True)
        
        # Create the invoice processor with mocked services
        with patch('services.invoice_processor.OCRService', return_value=self.mock_ocr), \
             patch('services.invoice_processor.LLMService', return_value=self.mock_llm):
            #  patch.object(InvoiceProcessor, 'data_dir', self.test_data_dir):
            self.processor = InvoiceProcessor()
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Remove test files
        for filename in os.listdir(self.test_data_dir):
            os.remove(os.path.join(self.test_data_dir, filename))
        
        # Remove test directory
        os.rmdir(self.test_data_dir)
    
    def test_process_invoice(self):
        """Test processing an invoice"""
        # Create a mock file path
        file_path = "test_invoice.pdf"
        
        # Process the invoice
        result = self.processor.process_invoice(file_path)
        
        # Check that the OCR service was called
        self.mock_ocr.process_file.assert_called_once_with(file_path)
        
        # Check that the LLM service was called for extraction
        self.mock_llm.extract_invoice_data.assert_called_once()
        
        # Check that the result contains the expected keys
        self.assertIn("invoice", result)
        self.assertIn("analysis", result)
        self.assertIn("recommendations", result)
        
        # Check that the invoice data is correct
        self.assertEqual(result["invoice"]["provider"], "Energy Co")
        self.assertEqual(result["invoice"]["total_amount"], 150.75)
        
        # Check that the invoice was saved
        invoice_id = result["invoice"]["id"]
        invoice_file = os.path.join(self.test_data_dir, f"invoice_{invoice_id}.json")
        self.assertTrue(os.path.exists(invoice_file))
        
        # Check that the recommendations were saved
        recommendations_file = os.path.join(self.test_data_dir, f"recommendations_{invoice_id}.json")
        self.assertTrue(os.path.exists(recommendations_file))
    
    def test_get_invoice(self):
        """Test retrieving an invoice"""
        # Process a mock invoice first
        file_path = "test_invoice.pdf"
        result = self.processor.process_invoice(file_path)
        invoice_id = result["invoice"]["id"]
        
        # Get the invoice
        invoice = self.processor.get_invoice(invoice_id)
        
        # Check that the invoice data is correct
        self.assertEqual(invoice["provider"], "Energy Co")
        self.assertEqual(invoice["total_amount"], 150.75)
    
    def test_get_recommendations(self):
        """Test retrieving recommendations"""
        # Process a mock invoice first
        file_path = "test_invoice.pdf"
        result = self.processor.process_invoice(file_path)
        invoice_id = result["invoice"]["id"]
        
        # Get the recommendations
        recommendations = self.processor.get_recommendations(invoice_id)
        
        # Check that the recommendations data is correct
        self.assertIn("Switch to energy-efficient appliances", recommendations["recommendations"])
        self.assertEqual(recommendations["potential_savings"], 45.25)
        self.assertEqual(recommendations["efficiency_score"], 70)

if __name__ == '__main__':
    unittest.main()
