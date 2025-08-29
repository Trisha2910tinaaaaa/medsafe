import fitz  # PyMuPDF
from PIL import Image
import io
import base64
from typing import Optional, Tuple
import streamlit as st

class FileProcessor:
    def __init__(self):
        pass
    
    def process_uploaded_file(self, uploaded_file) -> Tuple[str, str]:
        """Process uploaded file and extract text"""
        if uploaded_file is None:
            return "", "No file uploaded"
        
        file_type = uploaded_file.content_type
        file_name = uploaded_file.name
        
        try:
            if file_type == "application/pdf":
                return self._extract_text_from_pdf(uploaded_file), "PDF processed successfully"
            elif file_type.startswith("image/"):
                return self._extract_text_from_image(uploaded_file), "Image processed successfully"
            else:
                return "", f"Unsupported file type: {file_type}"
                
        except Exception as e:
            return "", f"Error processing file: {str(e)}"
    
    def _extract_text_from_pdf(self, uploaded_file) -> str:
        """Extract text from PDF file"""
        try:
            # Read PDF content
            pdf_content = uploaded_file.read()
            
            # Open PDF with PyMuPDF
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            
            extracted_text = ""
            
            # Extract text from each page
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                text = page.get_text()
                extracted_text += text + "\n"
            
            pdf_document.close()
            return extracted_text.strip()
            
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def _extract_text_from_image(self, uploaded_file) -> str:
        """Extract text from image using OCR"""
        try:
            # Read image content
            image_content = uploaded_file.read()
            
            # Open image with PIL
            image = Image.open(io.BytesIO(image_content))
            
            # For now, return a placeholder since OCR requires additional setup
            return "Image text extraction requires OCR setup. Please enter text manually."
            
        except Exception as e:
            raise Exception(f"Error extracting text from image: {str(e)}")
    
    def validate_file(self, uploaded_file) -> Tuple[bool, str]:
        """Validate uploaded file"""
        if uploaded_file is None:
            return False, "No file uploaded"
        
        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if uploaded_file.size > max_size:
            return False, "File size too large. Maximum size is 10MB."
        
        # Check file type
        allowed_types = [
            "application/pdf",
            "image/jpeg",
            "image/jpg",
            "image/png",
            "image/tiff",
            "image/bmp"
        ]
        
        if uploaded_file.content_type not in allowed_types:
            return False, f"Unsupported file type: {uploaded_file.content_type}. Supported types: PDF, JPEG, PNG, TIFF, BMP"
        
        return True, "File is valid"
    
    def get_file_preview(self, uploaded_file) -> Optional[str]:
        """Get preview of uploaded file"""
        if uploaded_file is None:
            return None
        
        try:
            if uploaded_file.content_type == "application/pdf":
                return self._get_pdf_preview(uploaded_file)
            elif uploaded_file.content_type.startswith("image/"):
                return self._get_image_preview(uploaded_file)
            else:
                return None
                
        except Exception as e:
            return f"Error generating preview: {str(e)}"
    
    def _get_pdf_preview(self, uploaded_file) -> str:
        """Get preview of PDF file"""
        try:
            pdf_content = uploaded_file.read()
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            
            # Get first page text for preview
            if len(pdf_document) > 0:
                first_page = pdf_document.load_page(0)
                preview_text = first_page.get_text()
                pdf_document.close()
                
                # Limit preview length
                if len(preview_text) > 500:
                    preview_text = preview_text[:500] + "..."
                
                return preview_text
            
            pdf_document.close()
            return "PDF appears to be empty"
            
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
    
    def _get_image_preview(self, uploaded_file) -> str:
        """Get preview of image file"""
        try:
            image_content = uploaded_file.read()
            image = Image.open(io.BytesIO(image_content))
            
            # Get image info
            width, height = image.size
            format_name = image.format
            mode = image.mode
            
            preview_info = f"Image: {format_name} format, {width}x{height} pixels, {mode} mode"
            
            return f"{preview_info}\n\nOCR processing requires additional setup."
                
        except Exception as e:
            return f"Error reading image: {str(e)}"
    
    def save_uploaded_file(self, uploaded_file, save_path: str) -> bool:
        """Save uploaded file to disk"""
        try:
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            return True
        except Exception as e:
            print(f"Error saving file: {str(e)}")
            return False
    
    def get_file_info(self, uploaded_file) -> dict:
        """Get information about uploaded file"""
        if uploaded_file is None:
            return {}
        
        return {
            'name': uploaded_file.name,
            'type': uploaded_file.content_type,
            'size': uploaded_file.size,
            'size_mb': round(uploaded_file.size / (1024 * 1024), 2)
        }
