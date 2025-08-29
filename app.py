import streamlit as st
import requests
import json
import base64
from datetime import datetime
import io

# Page configuration
st.set_page_config(
    page_title="MedSafe - AI Prescription Verification",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        color: black;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 4px solid #1e3c72;
    }
    
    .interaction-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 2px solid #e53e3e;
        box-shadow: 0 4px 12px rgba(229, 62, 62, 0.1);
        color: #2d3748;
    }
    
    .interaction-card h4 {
        color: #e53e3e;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    
    .interaction-card p {
        margin: 0.5rem 0;
        line-height: 1.6;
    }
    
    .success-card {
        background: #f0fff4;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #38a169;
    }
    
    .warning-card {
        background: #fffaf0;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #d69e2e;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        color: #2d3748;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: left;
        margin: 1rem 0;
        border: 2px solid #dee2e6;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card h3 {
        color: #1e3c72;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    
    .upload-area {
        border: 2px dashed #1e3c72;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f8fafc;
        margin: 1rem 0;
    }
    
    .patient-form {
        background: #f7fafc;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
    }
    
    .language-selector {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: black;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 25px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
        color: black;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000"

def check_api_health():
    """Check if the backend API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def call_api_endpoint(endpoint, data):
    """Generic function to call API endpoints"""
    try:
        response = requests.post(f"{API_BASE_URL}{endpoint}", json=data, timeout=60)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None

def get_severity_color(severity):
    """Get color for severity level"""
    colors = {
        'high': '#e53e3e',
        'medium': '#d69e2e', 
        'low': '#38a169'
    }
    return colors.get(severity.lower(), '#718096')

# Main App
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>💊 MedSafe - AI-Powered Prescription Verification</h1>
        <p>Advanced Drug Interaction Analysis with IBM Granite & Hugging Face AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🔧 System Status")
        api_status = check_api_health()
        if api_status:
            st.success("✅ Backend API Connected")
        else:
            st.error("❌ Backend API Offline")
            st.info("Please start the backend server first")
        
        st.markdown("### 🤖 AI Models")
        st.info("• Hugging Face Medical NER")
        st.info("• IBM Granite 3.0 8B")
        st.info("• Multi-language Translation")
        
        st.markdown("### 📋 Example Prescriptions")
        examples = [
            "Take aspirin 500mg twice daily and ibuprofen 400mg for pain relief",
            "Patient should use amoxicillin 500mg three times daily for infection",
            "Prescribe paracetamol for fever and aspirin for headache"
        ]
        
        selected_example = st.selectbox("Choose an example:", examples, key="example_select")
        if st.button("Load Example", key="load_example"):
            st.session_state.prescription_text = selected_example
    
    # Main content with tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🏥 Drug Interactions", "💊 Dosage & Alternatives", "📄 File Upload", "📊 Comprehensive Analysis"])
    
    # Tab 1: Drug Interactions
    with tab1:
        st.markdown("## 🔍 Drug Interaction Analysis")
        
        # Language selection
        col1, col2 = st.columns(2)
        with col1:
            language = st.selectbox(
                "Select Language:",
                ["english", "spanish", "french", "german", "italian", "portuguese", "hindi", "chinese", "japanese"],
                help="Select the language of your prescription",
                key="interaction_language"
            )
        
        # Patient context
        with col2:
            st.markdown("### Patient Information")
            age = st.slider("Age", 1, 100, 25, key="interaction_age")
            weight = st.number_input("Weight (kg)", 1.0, 200.0, 70.0, key="interaction_weight")
            renal_function = st.selectbox("Renal Function", ["normal", "mild", "moderate", "severe", "dialysis"], key="interaction_renal")
        
        # Prescription input
        prescription_text = st.text_area(
            "Enter Prescription Text:",
            value=st.session_state.get('prescription_text', ''),
            height=150,
            placeholder="Enter your prescription here...",
            key="interaction_text"
        )
        
        # Patient medical history
        with st.expander("📋 Patient Medical History", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                pregnant = st.checkbox("Pregnant", key="pregnant")
                kidney_disease = st.checkbox("Kidney Disease", key="kidney_disease")
            with col2:
                liver_disease = st.checkbox("Liver Disease", key="liver_disease")
                heart_disease = st.checkbox("Heart Disease", key="heart_disease")
            with col3:
                diabetes = st.checkbox("Diabetes", key="diabetes")
                allergies = st.text_input("Known Allergies", placeholder="e.g., penicillin, aspirin", key="allergies")
        
        # Analyze button
        if st.button("🔍 Analyze Drug Interactions", type="primary", key="analyze_interactions"):
            if prescription_text.strip():
                with st.spinner("🤖 AI is analyzing your prescription..."):
                    # Prepare patient context
                    patient_context = {
                        "age": age,
                        "weight": weight,
                        "renal_function": renal_function,
                        "pregnant": pregnant,
                        "kidney_disease": kidney_disease,
                        "liver_disease": liver_disease,
                        "heart_disease": heart_disease,
                        "diabetes": diabetes,
                        "allergies": [allergies] if allergies else []
                    }
                    
                    # Call API
                    data = {
                        "text": prescription_text,
                        "language": language,
                        "patient_context": patient_context
                    }
                    
                    result = call_api_endpoint("/check_interactions", data)
                    
                    if result and result.get('success'):
                        # Display results
                        st.markdown("### 📊 Analysis Results")
                        
                        # Drugs found
                        if result.get('drugs_found'):
                            st.markdown(f"""
                            <div class="feature-card">
                                <h4>🔍 Drugs Identified</h4>
                                <p><strong>{', '.join([drug.title() for drug in result['drugs_found']])}</strong></p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Interactions
                        if result.get('interactions'):
                            st.markdown("### ⚠️ Drug Interactions Found")
                            for i, interaction in enumerate(result['interactions']):
                                severity_color = get_severity_color(interaction.get('severity', 'medium'))
                                st.markdown(f"""
                                <div class="interaction-card">
                                    <h4>Interaction {i+1}: {interaction['drug1'].title()} + {interaction['drug2'].title()}</h4>
                                    <p><strong>Severity:</strong> <span style="color: {severity_color};">{interaction['severity'].upper()}</span></p>
                                    <p><strong>Description:</strong> {interaction['description']}</p>
                                    <p><strong>AI Explanation:</strong> {interaction.get('ai_analysis', 'No AI analysis available')}</p>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div class="success-card">
                                <h4>✅ No Drug Interactions Detected!</h4>
                                <p>Your prescription appears safe based on our analysis.</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.error("❌ Failed to analyze prescription. Please check your input and try again.")
            else:
                st.warning("⚠️ Please enter prescription text to analyze.")
    
    # Tab 2: Dosage & Alternatives
    with tab2:
        st.markdown("## 💊 Dosage & Alternative Recommendations")
        
        # Input section
        col1, col2 = st.columns(2)
        with col1:
            dosage_text = st.text_area(
                "Prescription Text:",
                value=st.session_state.get('prescription_text', ''),
                height=100,
                placeholder="Enter prescription for dosage analysis...",
                key="dosage_text"
            )
        
        with col2:
            dosage_age = st.slider("Patient Age", 1, 100, 25, key="dosage_age")
            dosage_weight = st.number_input("Patient Weight (kg)", 1.0, 200.0, 70.0, key="dosage_weight")
            dosage_renal = st.selectbox("Renal Function", ["normal", "mild", "moderate", "severe", "dialysis"], key="dosage_renal")
        
        if st.button("💊 Check Dosage & Alternatives", type="primary", key="check_dosage"):
            if dosage_text.strip():
                with st.spinner("🤖 Analyzing dosage recommendations..."):
                    data = {
                        "text": dosage_text,
                        "age": dosage_age,
                        "weight": dosage_weight,
                        "renal_function": dosage_renal,
                        "language": "english"
                    }
                    
                    result = call_api_endpoint("/check_dosage", data)
                    
                    if result and result.get('success'):
                        st.markdown("### 📋 Dosage Recommendations")
                        
                        for item in result.get('results', []):
                            st.markdown(f"""
                            <div class="metric-card">
                                <h3>{item['drug'].title()}</h3>
                                <p><strong>Recommended Dosage:</strong> {item.get('recommended_dosage', 'Consult healthcare provider')}</p>
                                <p><strong>Age Group:</strong> {item.get('age_group', 'Unknown')}</p>
                                <p><strong>Max Daily:</strong> {item.get('max_daily', 'Consult healthcare provider')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Alternatives
                            if item.get('alternatives'):
                                st.markdown(f"""
                                <div class="feature-card">
                                    <h4>🔄 Alternative Medications</h4>
                                    <p>{', '.join(item['alternatives'])}</p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Contraindications
                            if item.get('contraindications'):
                                st.markdown(f"""
                                <div class="warning-card">
                                    <h4>⚠️ Contraindications</h4>
                                    <ul>
                                        {''.join([f'<li>{contra}</li>' for contra in item['contraindications']])}
                                    </ul>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.error("❌ Failed to get dosage recommendations.")
            else:
                st.warning("⚠️ Please enter prescription text for dosage analysis.")
    
    # Tab 3: File Upload
    with tab3:
        st.markdown("## 📄 Upload Prescription Files")
        
        st.markdown("""
        <div class="upload-area">
            <h3>📁 Upload Your Prescription</h3>
            <p>Supported formats: PDF, JPEG, PNG, TIFF, BMP</p>
            <p>Maximum file size: 10MB</p>
            <p>AI-powered text extraction and analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'jpg', 'jpeg', 'png', 'tiff', 'bmp'],
            help="Upload a prescription file for analysis",
            key="file_uploader"
        )
        
        if uploaded_file:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            # Display file info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"📄 **File Type:** {uploaded_file.type}")
            with col2:
                st.info(f"📏 **Size:** {round(uploaded_file.size / 1024, 2)} KB")
            with col3:
                st.info(f"📁 **Name:** {uploaded_file.name}")
            
            # File analysis parameters
            st.markdown("### 👤 Patient Information")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                file_age = st.slider("Patient Age", 1, 100, 25, key="file_age")
            with col2:
                file_weight = st.number_input("Patient Weight (kg)", 1.0, 200.0, 70.0, key="file_weight")
            with col3:
                file_renal = st.selectbox("Renal Function", ["normal", "mild", "moderate", "severe", "dialysis"], key="file_renal")
            with col4:
                file_language = st.selectbox("Document Language", ["english", "spanish", "french", "german", "italian", "portuguese", "hindi", "chinese", "japanese"], key="file_language")
            
            # Patient medical history for file analysis
            with st.expander("📋 Patient Medical History", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    file_pregnant = st.checkbox("Pregnant", key="file_pregnant")
                    file_kidney = st.checkbox("Kidney Disease", key="file_kidney")
                with col2:
                    file_liver = st.checkbox("Liver Disease", key="file_liver")
                    file_heart = st.checkbox("Heart Disease", key="file_heart")
                with col3:
                    file_diabetes = st.checkbox("Diabetes", key="file_diabetes")
                    file_allergies = st.text_input("Known Allergies", placeholder="e.g., penicillin", key="file_allergies")
            
            if st.button("🔍 Analyze Uploaded File", type="primary", key="analyze_file"):
                if uploaded_file:
                    with st.spinner("🤖 Processing file and analyzing..."):
                        try:
                            # Prepare form data for file upload
                            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                            data = {
                                "age": file_age,
                                "weight": file_weight,
                                "renal_function": file_renal,
                                "language": file_language
                            }
                            
                            # Call the file upload endpoint
                            response = requests.post(f"{API_BASE_URL}/upload_and_analyze", files=files, data=data, timeout=120)
                            
                            if response.status_code == 200:
                                result = response.json()
                                
                                if result.get('success'):
                                    st.markdown("### 📊 File Analysis Results")
                                    
                                    # Display extracted text
                                    if result.get('original_text'):
                                        with st.expander("📄 Extracted Text from Document", expanded=False):
                                            st.text_area("Extracted Text:", value=result['original_text'], height=150, disabled=True)
                                    
                                    # Display drugs found
                                    if result.get('drugs_found'):
                                        st.markdown(f"""
                                        <div class="feature-card">
                                            <h4>🔍 Drugs Identified from Document</h4>
                                            <p><strong>{', '.join([drug.title() for drug in result['drugs_found']])}</strong></p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                    # Display interactions
                                    if result.get('interactions'):
                                        st.markdown("### ⚠️ Drug Interactions Found")
                                        for i, interaction in enumerate(result['interactions']):
                                            severity_color = get_severity_color(interaction.get('severity', 'medium'))
                                            st.markdown(f"""
                                            <div class="interaction-card">
                                                <h4>Interaction {i+1}: {interaction['drug1'].title()} + {interaction['drug2'].title()}</h4>
                                                <p><strong>Severity:</strong> <span style="color: {severity_color};">{interaction['severity'].upper()}</span></p>
                                                <p><strong>Description:</strong> {interaction['description']}</p>
                                                <p><strong>AI Explanation:</strong> {interaction.get('ai_analysis', 'No AI analysis available')}</p>
                                            </div>
                                            """, unsafe_allow_html=True)
                                    else:
                                        st.markdown("""
                                        <div class="success-card">
                                            <h4>✅ No Drug Interactions Detected!</h4>
                                            <p>Your prescription appears safe based on our analysis.</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                    # Display dosage recommendations
                                    if result.get('dosage_results'):
                                        st.markdown("### 💊 Dosage Recommendations")
                                        for item in result['dosage_results']:
                                            st.markdown(f"""
                                            <div class="metric-card">
                                                <h3>{item['drug'].title()}</h3>
                                                <p><strong>Recommended Dosage:</strong> {item.get('recommended_dosage', 'Consult healthcare provider')}</p>
                                                <p><strong>Age Group:</strong> {item.get('age_group', 'Unknown')}</p>
                                                <p><strong>Max Daily:</strong> {item.get('max_daily', 'Consult healthcare provider')}</p>
                                            </div>
                                            """, unsafe_allow_html=True)
                                            
                                            # Alternatives
                                            if item.get('alternatives'):
                                                st.markdown(f"""
                                                <div class="feature-card">
                                                    <h4>🔄 Alternative Medications</h4>
                                                    <p>{', '.join(item['alternatives'])}</p>
                                                </div>
                                                """, unsafe_allow_html=True)
                                    
                                    # File info
                                    if result.get('file_info'):
                                        st.markdown("### 📁 File Information")
                                        file_info = result['file_info']
                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            st.info(f"📄 **File:** {file_info.get('name', 'Unknown')}")
                                        with col2:
                                            st.info(f"📏 **Size:** {file_info.get('size_mb', 0)} MB")
                                        with col3:
                                            st.info(f"🔍 **Type:** {file_info.get('type', 'Unknown')}")
                                    
                                    # Store results for PDF generation
                                    st.session_state.file_analysis_results = result
                                    
                                    # Generate PDF button
                                    if st.button("📄 Generate PDF Report", type="secondary", key="generate_file_pdf"):
                                        if 'file_analysis_results' in st.session_state:
                                            with st.spinner("📄 Generating PDF report..."):
                                                try:
                                                    # Call the PDF generation endpoint
                                                    response = requests.post(f"{API_BASE_URL}/generate_pdf_report", json=st.session_state.file_analysis_results, timeout=60)
                                                    
                                                    if response.status_code == 200:
                                                        # Create download button for PDF
                                                        st.success("✅ PDF report generated successfully!")
                                                        
                                                        # Create download button
                                                        st.download_button(
                                                            label="📥 Download PDF Report",
                                                            data=response.content,
                                                            file_name="medsafe_file_analysis_report.pdf",
                                                            mime="application/pdf",
                                                            key="download_file_pdf"
                                                        )
                                                        
                                                        st.info("📄 The PDF includes all analysis results, patient context, and AI recommendations")
                                                    else:
                                                        st.error(f"❌ Failed to generate PDF: {response.status_code}")
                                                        
                                                except Exception as e:
                                                    st.error(f"❌ Error generating PDF: {str(e)}")
                                                    st.info("💡 Make sure the backend server is running.")
                                        else:
                                            st.warning("⚠️ Please run file analysis first to generate PDF report.")
                                    
                                else:
                                    st.error("❌ Failed to analyze file. Please check your input and try again.")
                            else:
                                st.error(f"❌ API Error: {response.status_code} - {response.text}")
                                
                        except Exception as e:
                            st.error(f"❌ Error processing file: {str(e)}")
                            st.info("💡 Make sure the backend server is running and the file is in a supported format.")
                else:
                    st.warning("⚠️ Please upload a file to analyze.")
    
    # Tab 4: Comprehensive Analysis
    with tab4:
        st.markdown("## 📊 Comprehensive Analysis")
        
        # Input section
        comp_text = st.text_area(
            "Prescription Text for Comprehensive Analysis:",
            value=st.session_state.get('prescription_text', ''),
            height=120,
            placeholder="Enter prescription for comprehensive analysis...",
            key="comp_text"
        )
        
        # Patient context for comprehensive analysis
        with st.expander("📋 Patient Context for Analysis", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                comp_age = st.slider("Age", 1, 100, 25, key="comp_age")
                comp_weight = st.number_input("Weight (kg)", 1.0, 200.0, 70.0, key="comp_weight")
                comp_renal = st.selectbox("Renal Function", ["normal", "mild", "moderate", "severe", "dialysis"], key="comp_renal")
            
            with col2:
                comp_pregnant = st.checkbox("Pregnant", key="comp_pregnant")
                comp_kidney = st.checkbox("Kidney Disease", key="comp_kidney")
                comp_liver = st.checkbox("Liver Disease", key="comp_liver")
                comp_allergies = st.text_input("Known Allergies", placeholder="e.g., penicillin", key="comp_allergies")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 Run Comprehensive Analysis", type="primary", key="run_comprehensive"):
                if comp_text.strip():
                    with st.spinner("🤖 Running comprehensive analysis..."):
                        # Prepare patient context
                        patient_context = {
                            "age": comp_age,
                            "weight": comp_weight,
                            "renal_function": comp_renal,
                            "pregnant": comp_pregnant,
                            "kidney_disease": comp_kidney,
                            "liver_disease": comp_liver,
                            "allergies": [comp_allergies] if comp_allergies else []
                        }
                        
                        data = {
                            "text": comp_text,
                            "age": comp_age,
                            "weight": comp_weight,
                            "renal_function": comp_renal,
                            "language": "english",
                            "patient_context": patient_context
                        }
                        
                        result = call_api_endpoint("/comprehensive_analysis", data)
                        
                        if result and result.get('success'):
                            # Store results for PDF generation
                            st.session_state.analysis_results = result
                            
                            # Display summary
                            summary = result.get('summary', {})
                            st.markdown("### 📈 Analysis Summary")
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Drugs Found", summary.get('total_drugs', 0))
                            with col2:
                                st.metric("Total Interactions", summary.get('total_interactions', 0))
                            with col3:
                                st.metric("High Risk", summary.get('high_risk_interactions', 0))
                            with col4:
                                st.metric("Medium Risk", summary.get('medium_risk_interactions', 0))
                            
                            # Display detailed results
                            if result.get('interactions'):
                                st.markdown("### ⚠️ Drug Interactions")
                                for interaction in result['interactions']:
                                    st.markdown(f"""
                                    <div class="interaction-card">
                                        <h4>{interaction['drug1'].title()} + {interaction['drug2'].title()}</h4>
                                        <p><strong>Severity:</strong> {interaction['severity'].upper()}</p>
                                        <p><strong>Description:</strong> {interaction['description']}</p>
                                        <p><strong>AI Analysis:</strong> {interaction.get('ai_analysis', 'N/A')}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            if result.get('dosage_results'):
                                st.markdown("### 💊 Dosage Recommendations")
                                for dosage in result['dosage_results']:
                                    st.markdown(f"""
                                    <div class="feature-card">
                                        <h4>{dosage['drug'].title()}</h4>
                                        <p><strong>Dosage:</strong> {dosage.get('recommended_dosage', 'Consult provider')}</p>
                                        <p><strong>Alternatives:</strong> {', '.join(dosage.get('alternatives', []))}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                        else:
                            st.error("❌ Failed to run comprehensive analysis.")
                else:
                    st.warning("⚠️ Please enter prescription text for analysis.")
        
        with col2:
            if st.button("📄 Generate PDF Report", type="secondary", key="generate_pdf"):
                if 'analysis_results' in st.session_state:
                    with st.spinner("📄 Generating PDF report..."):
                        try:
                            # Call the PDF generation endpoint
                            response = requests.post(f"{API_BASE_URL}/generate_pdf_report", json=st.session_state.analysis_results, timeout=60)
                            
                            if response.status_code == 200:
                                # Create download button for PDF
                                st.success("✅ PDF report generated successfully!")
                                
                                # Create download button
                                st.download_button(
                                    label="📥 Download PDF Report",
                                    data=response.content,
                                    file_name="medsafe_analysis_report.pdf",
                                    mime="application/pdf",
                                    key="download_pdf"
                                )
                                
                                st.info("📄 The PDF includes all analysis results, patient context, and AI recommendations")
                            else:
                                st.error(f"❌ Failed to generate PDF: {response.status_code}")
                                
                        except Exception as e:
                            st.error(f"❌ Error generating PDF: {str(e)}")
                            st.info("💡 Make sure the backend server is running.")
                else:
                    st.warning("⚠️ Please run comprehensive analysis first to generate PDF report.")

if __name__ == "__main__":
    main()
