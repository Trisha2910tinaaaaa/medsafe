from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import os
import tempfile
from dotenv import load_dotenv

# Import our components
from database.drug_database import DrugDatabase
from components.ai_services import AIServices
from components.file_processor import FileProcessor
from components.pdf_generator import PDFGenerator

load_dotenv()

app = FastAPI(
    title="MedSafe API",
    description="AI-Powered Prescription Verification System",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
drug_db = DrugDatabase()
ai_services = AIServices()
file_processor = FileProcessor()
pdf_generator = PDFGenerator()

# Pydantic models
class InteractionRequest(BaseModel):
    text: str
    language: str = "english"
    patient_context: Optional[Dict[str, Any]] = None

class DosageRequest(BaseModel):
    text: str
    age: int
    weight: Optional[float] = None
    renal_function: str = "normal"
    language: str = "english"

class AnalysisRequest(BaseModel):
    text: str
    age: int
    weight: Optional[float] = None
    renal_function: str = "normal"
    language: str = "english"
    patient_context: Optional[Dict[str, Any]] = None

class InteractionResponse(BaseModel):
    success: bool
    drugs_found: List[str]
    interactions: List[Dict[str, Any]]
    patient_explanations: List[str]

class DosageResponse(BaseModel):
    success: bool
    results: List[Dict[str, Any]]

class AnalysisResponse(BaseModel):
    success: bool
    drugs_found: List[str]
    interactions: List[Dict[str, Any]]
    dosage_results: List[Dict[str, Any]]
    patient_explanations: List[str]
    summary: Dict[str, Any]

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "MedSafe API v2.0",
        "version": "2.0.0",
        "ai_models": {
            "huggingface_ner": "samant/medical-ner",
            "ibm_granite": "ibm-granite/granite-3.0-8b-instruct",
            "translation": "Helsinki-NLP models"
        },
        "features": [
            "Drug Interaction Detection",
            "Age-Specific Dosage Recommendations", 
            "Alternative Medication Suggestions",
            "NLP-Based Drug Information Extraction",
            "Multi-Language Support",
            "PDF/Image Upload Processing",
            "Explainable AI Analysis",
            "PDF Report Generation"
        ]
    }

@app.post("/check_interactions", response_model=InteractionResponse)
async def check_interactions(request: InteractionRequest):
    """
    Check for drug interactions in prescription text with explainable AI
    """
    try:
        # Extract drugs using AI
        extracted_drugs = ai_services.extract_drugs_from_text(request.text, request.language)
        drugs_found = [drug['drug_name'] for drug in extracted_drugs]
        
        if not drugs_found:
            return InteractionResponse(
                success=True,
                drugs_found=[],
                interactions=[],
                patient_explanations=[]
            )
        
        # Check for interactions
        interactions = drug_db.get_interactions(drugs_found)
        
        # Add AI analysis for each interaction
        patient_explanations = []
        for interaction in interactions:
            # Get explainable AI analysis
            ai_explanation = ai_services.get_explainable_ai_analysis(interaction)
            interaction['ai_analysis'] = ai_explanation
            patient_explanations.append(ai_explanation)
        
        return InteractionResponse(
            success=True,
            drugs_found=drugs_found,
            interactions=interactions,
            patient_explanations=patient_explanations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/check_dosage", response_model=DosageResponse)
async def check_dosage(request: DosageRequest):
    """
    Check dosage recommendations for drugs in prescription text
    """
    try:
        # Extract drugs using AI
        extracted_drugs = ai_services.extract_drugs_from_text(request.text, request.language)
        drugs_found = [drug['drug_name'] for drug in extracted_drugs]
        
        results = []
        for drug in drugs_found:
            dosage_info = drug_db.get_dosage_recommendations(
                drug, 
                request.age, 
                request.weight, 
                request.renal_function
            )
            
            # Get alternatives
            alternatives = drug_db.get_alternatives(drug)
            dosage_info['alternatives'] = [alt['name'] for alt in alternatives]
            
            results.append(dosage_info)
        
        return DosageResponse(
            success=True,
            results=results
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/comprehensive_analysis", response_model=AnalysisResponse)
async def comprehensive_analysis(request: AnalysisRequest):
    """
    Perform comprehensive analysis including interactions, dosage, and alternatives
    """
    try:
        # Extract drugs using AI
        extracted_drugs = ai_services.extract_drugs_from_text(request.text, request.language)
        drugs_found = [drug['drug_name'] for drug in extracted_drugs]
        
        # Check interactions
        interactions = drug_db.get_interactions(drugs_found)
        
        # Add AI analysis for each interaction
        patient_explanations = []
        for interaction in interactions:
            # Get detailed AI analysis with patient context
            detailed_analysis = ai_services.get_detailed_ai_analysis(interaction, request.patient_context)
            interaction['ai_analysis'] = detailed_analysis['detailed_analysis']
            interaction['patient_explanation'] = detailed_analysis['patient_explanation']
            patient_explanations.append(detailed_analysis['patient_explanation'])
        
        # Get dosage recommendations
        dosage_results = []
        for drug in drugs_found:
            dosage_info = drug_db.get_dosage_recommendations(
                drug, 
                request.age, 
                request.weight, 
                request.renal_function
            )
            
            # Get alternatives
            alternatives = drug_db.get_alternatives(drug)
            dosage_info['alternatives'] = [alt['name'] for alt in alternatives]
            
            dosage_results.append(dosage_info)
        
        # Generate summary
        summary = {
            "total_drugs": len(drugs_found),
            "total_interactions": len(interactions),
            "high_risk_interactions": len([i for i in interactions if i.get('severity') == 'high']),
            "medium_risk_interactions": len([i for i in interactions if i.get('severity') == 'medium']),
            "low_risk_interactions": len([i for i in interactions if i.get('severity') == 'low']),
            "patient_age": request.age,
            "analysis_timestamp": "2024-01-01T00:00:00Z"  # In production, use actual timestamp
        }
        
        return AnalysisResponse(
            success=True,
            drugs_found=drugs_found,
            interactions=interactions,
            dosage_results=dosage_results,
            patient_explanations=patient_explanations,
            summary=summary
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/upload_and_analyze")
async def upload_and_analyze(
    file: UploadFile = File(...),
    age: int = Form(...),
    weight: Optional[float] = Form(None),
    renal_function: str = Form("normal"),
    language: str = Form("english")
):
    """
    Upload PDF/image and perform comprehensive analysis
    """
    try:
        # Read file content first
        file_content = await file.read()
        
        # Create a simple file-like object for processing
        class SimpleFile:
            def __init__(self, content, filename, content_type):
                self.content = content
                self.filename = filename
                self.content_type = content_type
                self.name = filename
                self.type = content_type
                self.size = len(content)
                self._position = 0
            
            def read(self):
                return self.content
            
            def getvalue(self):
                return self.content
            
            def seek(self, position):
                self._position = position
        
        simple_file = SimpleFile(file_content, file.filename, file.content_type)
        
        # Validate file
        is_valid, validation_message = file_processor.validate_file(simple_file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=validation_message)
        
        # Process file
        extracted_text, process_message = file_processor.process_uploaded_file(simple_file)
        if not extracted_text or "Error" in extracted_text or "No text could be extracted" in extracted_text:
            raise HTTPException(status_code=400, detail=f"Text extraction failed: {extracted_text or process_message}")
        
        # Extract drugs - with fallback
        try:
            extracted_drugs = ai_services.extract_drugs_from_text(extracted_text, language)
            drugs_found = [drug['drug_name'] for drug in extracted_drugs if 'drug_name' in drug]
        except Exception as e:
            # Fallback: simple keyword extraction
            common_drugs = ['aspirin', 'ibuprofen', 'paracetamol', 'acetaminophen', 'amoxicillin', 'metformin']
            drugs_found = [drug for drug in common_drugs if drug.lower() in extracted_text.lower()]
        
        # Check interactions - with fallback
        try:
            interactions = drug_db.get_interactions(drugs_found) if drugs_found else []
        except Exception as e:
            interactions = []
        
        # Add AI analysis - with fallback
        for interaction in interactions:
            try:
                ai_explanation = ai_services.get_explainable_ai_analysis(interaction)
                interaction['ai_analysis'] = ai_explanation
            except Exception as e:
                interaction['ai_analysis'] = "AI analysis temporarily unavailable"
        
        # Get dosage recommendations - with fallback
        dosage_results = []
        for drug in drugs_found:
            try:
                dosage_info = drug_db.get_dosage_recommendations(drug, age, weight, renal_function)
                alternatives = drug_db.get_alternatives(drug)
                dosage_info['alternatives'] = [alt['name'] for alt in alternatives] if alternatives else []
                dosage_results.append(dosage_info)
            except Exception as e:
                dosage_results.append({
                    'drug': drug,
                    'recommended_dosage': 'Consult healthcare provider',
                    'age_group': 'All ages',
                    'max_daily': 'As prescribed',
                    'alternatives': []
                })
        
        return {
            "success": True,
            "original_text": extracted_text,
            "drugs_found": drugs_found,
            "interactions": interactions,
            "dosage_results": dosage_results,
            "file_info": file_processor.get_file_info(simple_file)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/generate_pdf_report")
async def generate_pdf_report(analysis_data: Dict[str, Any]):
    """
    Generate PDF report from analysis data
    """
    try:
        # Generate PDF
        pdf_content = pdf_generator.generate_analysis_report(analysis_data)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_content)
            tmp_file_path = tmp_file.name
        
        # Return file response
        return FileResponse(
            tmp_file_path,
            media_type="application/pdf",
            filename="medsafe_analysis_report.pdf"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

@app.get("/drug_info/{drug_name}")
async def get_drug_info(drug_name: str):
    """
    Get comprehensive drug information
    """
    try:
        drug_info = drug_db.get_drug_information(drug_name)
        if not drug_info:
            raise HTTPException(status_code=404, detail="Drug not found")
        
        return {
            "success": True,
            "drug_name": drug_name,
            "information": drug_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving drug info: {str(e)}")

@app.get("/available_drugs")
async def get_available_drugs():
    """
    Get list of available drugs in the system
    """
    try:
        # Get unique drugs from the database
        all_drugs = list(set(drug_db.interactions_df['drug1'].tolist() + drug_db.interactions_df['drug2'].tolist()))
        all_drugs.sort()
        
        return {
            "success": True,
            "drugs": all_drugs,
            "count": len(all_drugs)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving drugs: {str(e)}")

@app.get("/supported_languages")
async def get_supported_languages():
    """
    Get list of supported languages for translation
    """
    try:
        languages = list(ai_services.translation_models.keys())
        languages.insert(0, "english")  # Add English as first option
        
        return {
            "success": True,
            "languages": languages,
            "count": len(languages)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving languages: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Railway gives you PORT
    app.run(host="0.0.0.0", port=port)

