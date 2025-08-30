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
        
        # Handle both Streamlit UploadedFile and FastAPI UploadFile objects
        if hasattr(uploaded_file, 'type'):
            file_type = uploaded_file.type
        elif hasattr(uploaded_file, 'content_type'):
            file_type = uploaded_file.content_type
        else:
            # Fallback: determine type from filename
            file_name = getattr(uploaded_file, 'name', getattr(uploaded_file, 'filename', 'unknown'))
            if file_name.lower().endswith('.pdf'):
                file_type = "application/pdf"
            elif file_name.lower().endswith(('.jpg', '.jpeg')):
                file_type = "image/jpeg"
            elif file_name.lower().endswith('.png'):
                file_type = "image/png"
            elif file_name.lower().endswith('.tiff'):
                file_type = "image/tiff"
            elif file_name.lower().endswith('.bmp'):
                file_type = "image/bmp"
            else:
                return "", "Unable to determine file type"
        
        file_name = getattr(uploaded_file, 'name', getattr(uploaded_file, 'filename', 'unknown'))
        
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
            # Handle different file object types
            if hasattr(uploaded_file, 'read'):
                # For FastAPI UploadFile, read the content
                if hasattr(uploaded_file, 'seek'):
                    uploaded_file.seek(0)
                pdf_content = uploaded_file.read()
            elif hasattr(uploaded_file, 'getvalue'):
                # For Streamlit UploadedFile
                pdf_content = uploaded_file.getvalue()
            else:
                raise Exception("Unsupported file object type")
            
            # Open PDF with PyMuPDF
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            
            extracted_text = ""
            
            # Extract text from each page
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                text = page.get_text()
                extracted_text += text + "\n"
            
            pdf_document.close()
            
            # Check if any text was extracted
            if not extracted_text.strip():
                return "No text could be extracted from the PDF. The PDF might be image-based or encrypted."
            
            return extracted_text.strip()
            
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def _extract_text_from_image(self, uploaded_file) -> str:
        """Extract text from image using OCR"""
        try:
            # Import pytesseract for OCR
            try:
                import pytesseract
            except ImportError:
                return "OCR library not installed. Please install pytesseract: pip install pytesseract"
            
            # Handle different file object types
            if hasattr(uploaded_file, 'read'):
                # For FastAPI UploadFile, read the content
                if hasattr(uploaded_file, 'seek'):
                    uploaded_file.seek(0)
                image_content = uploaded_file.read()
            elif hasattr(uploaded_file, 'getvalue'):
                # For Streamlit UploadedFile
                image_content = uploaded_file.getvalue()
            else:
                raise Exception("Unsupported file object type")
            
            # Open image with PIL
            image = Image.open(io.BytesIO(image_content))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text using OCR
            extracted_text = pytesseract.image_to_string(image, lang='eng')
            
            if not extracted_text.strip():
                return "No text could be extracted from the image. Please ensure the image contains readable text."
            
            return extracted_text.strip()
            
        except Exception as e:
            # Fallback: return a more informative error message
            return f"Error extracting text from image: {str(e)}. Please ensure pytesseract is installed and configured properly."
    
    def validate_file(self, uploaded_file) -> Tuple[bool, str]:
        """Validate uploaded file"""
        if uploaded_file is None:
            return False, "No file uploaded"
        
        # Get file size
        if hasattr(uploaded_file, 'size'):
            file_size = uploaded_file.size
        elif hasattr(uploaded_file, 'file') and hasattr(uploaded_file.file, 'seek'):
            # For FastAPI UploadFile, get size by seeking
            current_pos = uploaded_file.file.tell()
            uploaded_file.file.seek(0, 2)  # Seek to end
            file_size = uploaded_file.file.tell()
            uploaded_file.file.seek(current_pos)  # Reset position
        else:
            file_size = 0
        
        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            return False, "File size too large. Maximum size is 10MB."
        
        # Get file type
        if hasattr(uploaded_file, 'type'):
            file_type = uploaded_file.type
        elif hasattr(uploaded_file, 'content_type'):
            file_type = uploaded_file.content_type
        else:
            # Fallback: determine type from filename
            file_name = getattr(uploaded_file, 'name', getattr(uploaded_file, 'filename', 'unknown'))
            if file_name.lower().endswith('.pdf'):
                file_type = "application/pdf"
            elif file_name.lower().endswith(('.jpg', '.jpeg')):
                file_type = "image/jpeg"
            elif file_name.lower().endswith('.png'):
                file_type = "image/png"
            elif file_name.lower().endswith('.tiff'):
                file_type = "image/tiff"
            elif file_name.lower().endswith('.bmp'):
                file_type = "image/bmp"
            else:
                return False, "Unable to determine file type"
        
        # Check file type
        allowed_types = [
            "application/pdf",
            "image/jpeg",
            "image/jpg",
            "image/png",
            "image/tiff",
            "image/bmp"
        ]
        
        if file_type not in allowed_types:
            return False, f"Unsupported file type: {file_type}. Supported types: PDF, JPEG, PNG, TIFF, BMP"
        
        return True, "File is valid"
    
    def get_file_preview(self, uploaded_file) -> Optional[str]:
        """Get preview of uploaded file"""
        if uploaded_file is None:
            return None
        
        try:
            if uploaded_file.type == "application/pdf":
                return self._get_pdf_preview(uploaded_file)
            elif uploaded_file.type.startswith("image/"):
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
        
        # Get file name
        file_name = getattr(uploaded_file, 'name', getattr(uploaded_file, 'filename', 'unknown'))
        
        # Get file type
        if hasattr(uploaded_file, 'type'):
            file_type = uploaded_file.type
        elif hasattr(uploaded_file, 'content_type'):
            file_type = uploaded_file.content_type
        else:
            file_type = "unknown"
        
        # Get file size
        if hasattr(uploaded_file, 'size'):
            file_size = uploaded_file.size
        elif hasattr(uploaded_file, 'file') and hasattr(uploaded_file.file, 'seek'):
            current_pos = uploaded_file.file.tell()
            uploaded_file.file.seek(0, 2)
            file_size = uploaded_file.file.tell()
            uploaded_file.file.seek(current_pos)
        else:
            file_size = 0
        
        return {
            'name': file_name,
            'type': file_type,
            'size': file_size,
            'size_mb': round(file_size / (1024 * 1024), 2) if file_size > 0 else 0
        }
