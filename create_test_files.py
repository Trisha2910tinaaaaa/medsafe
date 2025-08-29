#!/usr/bin/env python3
"""
Script to create test files for MedSafe upload functionality
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

def create_test_pdf():
    """Create a test PDF with prescription text"""
    filename = "test_prescription.pdf"
    
    # Create PDF
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Add title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Medical Prescription")
    
    # Add prescription text
    c.setFont("Helvetica", 12)
    prescription_text = [
        "Patient: John Doe",
        "Date: 2024-01-15",
        "",
        "Prescription:",
        "1. Aspirin 500mg - Take twice daily for pain relief",
        "2. Ibuprofen 400mg - Take as needed for inflammation",
        "3. Amoxicillin 500mg - Take three times daily for infection",
        "",
        "Instructions:",
        "- Take with food",
        "- Complete full course of antibiotics",
        "- Contact doctor if side effects occur",
        "",
        "Doctor: Dr. Smith",
        "License: MD12345"
    ]
    
    y_position = height - 100
    for line in prescription_text:
        c.drawString(50, y_position, line)
        y_position -= 20
    
    c.save()
    print(f"✅ Created test PDF: {filename}")
    return filename

def create_test_text():
    """Create a test text file with prescription"""
    filename = "test_prescription.txt"
    
    content = """MEDICAL PRESCRIPTION

Patient: Jane Smith
Date: 2024-01-15

PRESCRIPTION:
1. Paracetamol 500mg - Take every 6 hours for fever
2. Aspirin 100mg - Take once daily for heart health
3. Vitamin D 1000IU - Take once daily

INSTRUCTIONS:
- Take medications as directed
- Store in cool, dry place
- Keep out of reach of children

Doctor: Dr. Johnson
License: MD67890
"""
    
    with open(filename, 'w') as f:
        f.write(content)
    
    print(f"✅ Created test text file: {filename}")
    return filename

if __name__ == "__main__":
    print("Creating test files for MedSafe upload functionality...")
    
    # Create test files
    pdf_file = create_test_pdf()
    text_file = create_test_text()
    
    print("\n📁 Test files created:")
    print(f"   📄 {pdf_file} - Test PDF prescription")
    print(f"   📝 {text_file} - Test text prescription")
    
    print("\n🎯 You can now test the file upload functionality in MedSafe!")
    print("   - Upload the PDF file in the 'File Upload' tab")
    print("   - The system will extract text and analyze for drug interactions")
