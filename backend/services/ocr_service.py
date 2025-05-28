import os
import tempfile
import logging
from typing import List, Dict, Any, Union, Optional
import PyPDF2
from PIL import Image, ImageEnhance
from fpdf import FPDF
from unstract.llmwhisperer import LLMWhispererClientV2
import dotenv 

dotenv.load_dotenv(override=True)
logger = logging.getLogger(__name__)

def image_to_pdf(input_image_path: str, output_pdf_path: str, enhancement_params: Optional[Dict[str, float]] = None) -> str:
    """
    Convert an image to PDF with optional enhancement
    
    Args:
        input_image_path: Path to the input image
        output_pdf_path: Path to save the output PDF
        enhancement_params: Dictionary of enhancement parameters (brightness, contrast, sharpness)
        
    Returns:
        Path to the created PDF
    """
    # Default enhancement parameters if none provided
    if enhancement_params is None:
        enhancement_params = {
            'brightness': 1.2,  # Enhance brightness by 20%
            'contrast': 1.5,    # Enhance contrast by 50%
            'sharpness': 1.5    # Enhance sharpness by 50%
        }
    
    try:
        # Open the image
        image = Image.open(input_image_path)

        # Apply image enhancements
        if 'brightness' in enhancement_params:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(enhancement_params['brightness'])
        
        if 'contrast' in enhancement_params:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(enhancement_params['contrast'])
        
        if 'sharpness' in enhancement_params:
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(enhancement_params['sharpness'])

        # Convert the image to RGB mode if it is not (since PDF requires RGB)
        image = image.convert("RGB")

        # Create a temporary file to save the image
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_image_path = temp_file.name
            image.save(temp_image_path)

        # Create PDF
        pdf = FPDF()
        pdf.add_page()

        # Set the image size to fit the PDF page (keeping the aspect ratio)
        page_width = pdf.w - 20  # PDF page width minus margin
        page_height = pdf.h - 20  # PDF page height minus margin

        # Get the image dimensions
        img_width, img_height = image.size

        # Calculate scaling factors to maintain the aspect ratio
        scale_width = page_width / img_width
        scale_height = page_height / img_height
        scale = min(scale_width, scale_height)

        # Calculate new width and height to preserve aspect ratio
        new_width = img_width * scale
        new_height = img_height * scale

        # Position the image in the center of the page
        x = (page_width - new_width) / 2
        y = (page_height - new_height) / 2

        # Add the image to the PDF
        pdf.image(temp_image_path, x=x, y=y, w=new_width, h=new_height)

        # Save the PDF
        pdf.output(output_pdf_path)

        # Clean up the temporary file
        os.remove(temp_image_path)
        
        logger.info(f"PDF created successfully: {output_pdf_path}")
        return output_pdf_path
    
    except Exception as e:
        logger.error(f"Error converting image to PDF: {str(e)}")
        raise

class OCRService:
    """Service for performing OCR on invoice images and PDFs using LLMWhisperer"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        """
        Initialize the OCR service with LLMWhisperer
        
        Args:
            api_key: LLMWhisperer API key
            base_url: LLMWhisperer API base URL
        """
        self.api_key = api_key or os.environ.get('LLMWHISPERER_API_KEY', "FdutG4XNpnK5ILGwYTei2WWhhdnSEan-oMurX2jVUEE")
        self.base_url = base_url or os.environ.get('LLMWHISPERER_BASE_URL', "https://llmwhisperer-api.us-central.unstract.com/api/v2")
        
        # Initialize the LLMWhisperer client
        self.client = LLMWhispererClientV2(base_url=self.base_url, api_key=self.api_key)
        
        # Create a temporary directory for processing files
        self.temp_dir = os.path.join(tempfile.gettempdir(), 'aienergy_ocr')
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def process_image(self, image_path: str) -> str:
        """
        Extract text from an image using LLMWhisperer
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text from the image
        """
        try:
            # Convert image to PDF for better OCR results
            pdf_path = os.path.join(self.temp_dir, f"{os.path.basename(image_path)}.pdf")
            image_to_pdf(image_path, pdf_path)
            
            # Process the PDF with LLMWhisperer
            return self.process_pdf(pdf_path)
        except Exception as e:
            logger.error(f"Error processing image with OCR: {str(e)}")
            raise
        finally:
            # Clean up temporary PDF if it exists
            if 'pdf_path' in locals() and os.path.exists(pdf_path):
                os.remove(pdf_path)
    
    def process_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF using LLMWhisperer
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text from the PDF
        """
        try:
            # Use LLMWhisperer to extract text
            whisper_result = self.client.whisper(
                file_path=pdf_path, 
                wait_for_completion=True,
                wait_timeout=200
            )
            logger.info(f"LLMWhisperer result1: {whisper_result}")
            
            # Extract the result text
            if whisper_result and 'extraction' in whisper_result and 'result_text' in whisper_result['extraction']:
                return whisper_result['extraction']['result_text']
            else:
                # Fallback to PyPDF2 if LLMWhisperer doesn't return text
                logger.warning("LLMWhisperer did not return expected result format, falling back to PyPDF2")
                return self._extract_text_with_pypdf2(pdf_path)
        except Exception as e:
            logger.error(f"Error processing PDF with LLMWhisperer: {str(e)}")
            # Fallback to PyPDF2
            logger.info("Falling back to PyPDF2 for text extraction")
            return self._extract_text_with_pypdf2(pdf_path)
    
    def _extract_text_with_pypdf2(self, pdf_path: str) -> str:
        """
        Extract text from a PDF using PyPDF2 as a fallback
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text from the PDF
        """
        extracted_text = ""
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    if text:
                        extracted_text += text + "\n\n"
            
            return extracted_text
        except Exception as e:
            logger.error(f"Error extracting text with PyPDF2: {str(e)}")
            raise
    
    def process_file(self, file_path: str) -> str:
        """
        Process a file (image or PDF) and extract text
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted text from the file
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension in ['.pdf']:
            return self.process_pdf(file_path)
        elif file_extension in ['.jpg', '.jpeg', '.png']:
            return self.process_image(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

