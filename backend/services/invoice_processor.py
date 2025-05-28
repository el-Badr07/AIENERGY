import os
import json
import logging
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import pandas as pd

import os
import json
from services.ocr_service import OCRService
from services.llm_service import LLMService
from models.invoice import Invoice, InvoiceRecommendation
from utils.file_utils import extract_json_from_response

logger = logging.getLogger(__name__)

class InvoiceProcessor:
    """Service for processing energy invoices"""
    
    def __init__(self):
        """Initialize the invoice processor with OCR and LLM services"""
        # Initialize OCR service with LLMWhisperer API key from environment variables
        self.ocr_service = OCRService(
            api_key=os.environ.get('LLMWHISPERER_API_KEY'),
            base_url=os.environ.get('LLMWHISPERER_BASE_URL')
        )
        self.llm_service = LLMService()
        
        # In a real implementation, this would be a database
        # For simplicity, we're using in-memory storage
        self.invoices = {}
        self.recommendations = {}
        
        # Create data directory if it doesn't exist
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'data')
        os.makedirs(self.data_dir, exist_ok=True)
    
    def process_invoice(self, file_path: str) -> Dict[str, Any]:
        """
        Process an invoice file and extract information
        
        Args:
            file_path: Path to the invoice file
            
        Returns:
            Processed invoice data
        """
        try:
            # Extract text using OCR
            logger.info(f"Extracting text from invoice: {file_path}")
            print('file_path',file_path)
            ocr_text = self.ocr_service.process_file(file_path)
            logger.info(f"OCR text extracted: {ocr_text}")
            print('ocr_text',ocr_text)
            
            # Extract structured data using LLM
            logger.info("Extracting structured data from OCR text")
            invoice_data_str = self.llm_service.extract_invoice_data(ocr_text)
            invoice_data = json.loads(invoice_data_str) if isinstance(invoice_data_str, str) else invoice_data_str
            
            # Create invoice object
            invoice_id = str(uuid.uuid4())
            invoice_data['id'] = invoice_id
            invoice_data['file_path'] = file_path
            
            # Analyze invoice
            logger.info("Analyzing invoice data")
            analysis_str = self.llm_service.analyze_invoice(invoice_data)
            logger.info(f"Analysis result: {analysis_str}")
            analysis = json.loads(analysis_str) if isinstance(analysis_str, str) else analysis_str
            
            # Generate recommendations
            logger.info("Generating recommendations")
            recommendations_str = self.llm_service.generate_recommendations(invoice_data, analysis)
            recommendations = json.loads(recommendations_str) if isinstance(recommendations_str, str) else recommendations_str
            recommendations['invoice_id'] = invoice_id
            
            # Store invoice and recommendations
            self.invoices[invoice_id] = invoice_data
            self.recommendations[invoice_id] = recommendations
            
            # Save to disk (in a real implementation, this would be a database)
            self._save_invoice(invoice_id, invoice_data)
            self._save_recommendations(invoice_id, recommendations)
            logger.info("Invoice saved to disk")
            logger.info("Recommendations saved to disk")
            logger.info("Analysis saving to disk")
            # Save analysis to disk
            self._save_analysis(invoice_id, analysis)
            logger.info("Analysis saved to disk")
            
            # Return combined data
            result = {
                "invoice": invoice_data,
                "analysis": analysis,
                "recommendations": recommendations
            }

            # Save full result to static/data/full_results/{invoice_id}.json
            full_results_dir = os.path.join("static", "data", "full_results")
            os.makedirs(full_results_dir, exist_ok=True)
            full_result_path = os.path.join(full_results_dir, f"{invoice_id}.json")
            with open(full_result_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            return result

        except Exception as e:
            logger.error(f"Error processing invoice: {str(e)}")
            raise
    
    def get_all_full_results(self) -> list:
        """
        Loads all full invoice results from static/data/full_results.
        """
        full_results_dir = os.path.join("static", "data", "full_results")
        results = []
        if not os.path.exists(full_results_dir):
            return results
        for filename in os.listdir(full_results_dir):
            if filename.endswith(".json"):
                with open(os.path.join(full_results_dir, filename), "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        results.append(data)
                    except Exception as e:
                        import logging
                        logging.warning(f"Failed to load {filename}: {e}")
        return results
        
    def get_full_result_by_id(self, invoice_id: str) -> dict:
        """
        Loads a specific full invoice result by ID.
        """
        full_results_dir = os.path.join("static", "data", "full_results")
        full_result_path = os.path.join(full_results_dir, f"{invoice_id}.json")
        
        if os.path.exists(full_result_path):
            try:
                with open(full_result_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                import logging
                logging.warning(f"Failed to load {full_result_path}: {e}")
                return None
        return None

    def get_all_invoices(self) -> List[Dict[str, Any]]:
        """
        Get list of all processed invoices (summary only)
        Returns:
            List of dicts with id and summary fields
        """
        # Load invoices from disk if not in memory
        if not self.invoices:
            self._load_invoices()
        
        def summary(inv):
            return {
                "id": inv.get("id"),
                "provider": inv.get("provider"),
                "invoice_number": inv.get("invoice_number"),
                "issue_date": inv.get("issue_date"),
                "customer_name": inv.get("customer_name"),
                "total_amount": inv.get("total_amount"),
                "period_start": inv.get("period_start"),
                "period_end": inv.get("period_end"),
                "total_kwh": inv.get("total_kwh")
            }
        return [summary(inv) for inv in self.invoices.values()]
    
    def get_invoice(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """
        Get details for a specific invoice
        
        Args:
            invoice_id: ID of the invoice
            
        Returns:
            Invoice data or None if not found
        """
        # Load invoices from disk if not in memory
        if not self.invoices:
            self._load_invoices()
        
        return self.invoices.get(invoice_id)
    
    def get_recommendations(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """
        Get recommendations for a specific invoice
        
        Args:
            invoice_id: ID of the invoice
            
        Returns:
            Recommendations or None if not found
        """
        # Load recommendations from disk if not in memory
        if not self.recommendations:
            self._load_recommendations()
        
        return self.recommendations.get(invoice_id)

    def get_analysis(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """
        Get analysis for a specific invoice
        Args:
            invoice_id: ID of the invoice
        Returns:
            Analysis dict or None if not found
        """
        logger.info(f"Getting analysis for invoice: {invoice_id}")
        file_path = os.path.join(self.data_dir, f"analysis_{invoice_id}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return None

    
    def _save_invoice(self, invoice_id: str, invoice_data: Dict[str, Any]) -> None:
        """Save invoice data to disk"""
        file_path = os.path.join(self.data_dir, f"invoice_{invoice_id}.json")
        with open(file_path, 'w') as f:
            json.dump(invoice_data, f, indent=2)

    def _save_analysis(self, invoice_id: str, analysis: Dict[str, Any]) -> None:
        """Save analysis to disk"""
        file_path = os.path.join(self.data_dir, f"analysis_{invoice_id}.json")
        with open(file_path, 'w') as f:
            json.dump(analysis, f, indent=2)
    
    def _save_recommendations(self, invoice_id: str, recommendations: Dict[str, Any]) -> None:
        """Save recommendations to disk"""
        file_path = os.path.join(self.data_dir, f"recommendations_{invoice_id}.json")
        with open(file_path, 'w') as f:
            json.dump(recommendations, f, indent=2)
    
    def _load_invoices(self) -> None:
        """Load all invoices from disk"""
        self.invoices = {}
        for filename in os.listdir(self.data_dir):
            if filename.startswith("invoice_") and filename.endswith(".json"):
                invoice_id = filename.replace("invoice_", "").replace(".json", "")
                file_path = os.path.join(self.data_dir, filename)
                with open(file_path, 'r') as f:
                    self.invoices[invoice_id] = json.load(f)
    
    def _load_recommendations(self) -> None:
        """Load all recommendations from disk"""
        self.recommendations = {}
        for filename in os.listdir(self.data_dir):
            if filename.startswith("recommendations_") and filename.endswith(".json"):
                invoice_id = filename.replace("recommendations_", "").replace(".json", "")
                file_path = os.path.join(self.data_dir, filename)
                with open(file_path, 'r') as f:
                    self.recommendations[invoice_id] = json.load(f)
    
    def generate_report(self, invoice_ids: List[str] = None) -> pd.DataFrame:
        """
        Generate a report of invoice data
        
        Args:
            invoice_ids: List of invoice IDs to include in the report (None for all)
            
        Returns:
            DataFrame with invoice data
        """
        # Load invoices from disk if not in memory
        if not self.invoices:
            self._load_invoices()
        
        # Filter invoices if IDs provided
        invoices_to_report = self.invoices
        if invoice_ids:
            invoices_to_report = {k: v for k, v in self.invoices.items() if k in invoice_ids}
        
        # Create DataFrame
        report_data = []
        for invoice_id, invoice in invoices_to_report.items():
            report_data.append({
                "id": invoice_id,
                "provider": invoice.get("provider"),
                "invoice_number": invoice.get("invoice_number"),
                "issue_date": invoice.get("issue_date"),
                "due_date": invoice.get("due_date"),
                "customer_name": invoice.get("customer_name"),
                "total_amount": invoice.get("total_amount"),
                "total_kwh": invoice.get("total_kwh")
            })
        
        return pd.DataFrame(report_data)
