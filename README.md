# 💊 MedSafe - AI-Powered Prescription Verification System

**Advanced Drug Interaction Analysis with IBM Granite & Hugging Face AI**

A production-ready, hackathon-winning medical AI application that analyzes prescriptions for drug interactions, provides dosage recommendations, and generates comprehensive reports using cutting-edge AI models.

## 🚀 Features

### Core Features
- **🔍 Drug Interaction Detection**: Real-time analysis using comprehensive drug databases
- **💊 Age-Specific Dosage Recommendations**: Personalized dosing based on patient age and conditions
- **🔄 Alternative Medication Suggestions**: Smart alternatives for problematic drug combinations
- **🤖 NLP-Based Drug Information Extraction**: Advanced AI-powered text analysis
- **🌐 Multi-Language Support**: Process prescriptions in 8+ languages
- **📄 File Upload Processing**: Support for PDF and image uploads with OCR
- **📊 Explainable AI Analysis**: Patient-friendly explanations of complex interactions
- **📋 Professional PDF Reports**: Downloadable comprehensive analysis reports

### AI Models Used
- **Hugging Face Medical NER**: `samant/medical-ner` for drug entity extraction
- **IBM Granite 3.0 8B**: `ibm-granite/granite-3.0-8b-instruct` for AI analysis
- **Multi-language Translation**: Helsinki-NLP models for language support

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit (Python)
- **AI/ML**: Hugging Face Inference API, IBM Granite
- **Data Processing**: Pandas, NumPy
- **File Processing**: PyMuPDF, pytesseract (OCR)
- **PDF Generation**: ReportLab
- **Environment**: python-dotenv, virtualenv

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Git

### Quick Start (Windows)
1. Clone the repository:
```bash
git clone <repository-url>
cd medsafe
```

2. Run the startup script:
```bash
start_medsafe.bat
```

### Manual Installation
1. Create virtual environment:
```bash
python -m venv medsafe-env
```

2. Activate virtual environment:
```bash
# Windows
medsafe-env\Scripts\activate

# Unix/Linux/Mac
source medsafe-env/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
# Create .env file with your API keys
HF_API_KEY=your_huggingface_api_key_here
IBM_API_KEY=your_ibm_api_key_here
```

5. Start the system:
```bash
python run_medsafe.py
```

## 🎯 Usage

### Starting the Application
1. **Backend**: Runs on `http://localhost:8000`
2. **Frontend**: Runs on `http://localhost:8501`
3. **API Docs**: Available at `http://localhost:8000/docs`

### Using the Application

#### 1. Drug Interaction Analysis
- Enter prescription text in the "Drug Interactions" tab
- Select patient language if not English
- Add patient context (age, weight, medical conditions)
- Click "Analyze Drug Interactions"
- View AI-powered analysis with severity levels

#### 2. Dosage & Alternatives
- Enter prescription text in the "Dosage & Alternatives" tab
- Set patient age and weight
- Click "Check Dosage & Alternatives"
- Get personalized dosage recommendations and alternatives

#### 3. File Upload
- Upload PDF or image files in the "File Upload" tab
- Set patient parameters
- Get OCR-processed analysis

#### 4. Comprehensive Analysis
- Use the "Comprehensive Analysis" tab for full evaluation
- Generate downloadable PDF reports
- Get complete patient context analysis

## 🔧 API Endpoints

### Core Endpoints
- `GET /` - Health check and system info
- `POST /check_interactions` - Drug interaction analysis
- `POST /check_dosage` - Dosage recommendations
- `POST /comprehensive_analysis` - Full analysis
- `POST /upload_and_analyze` - File upload processing
- `POST /generate_pdf_report` - PDF report generation

### Utility Endpoints
- `GET /drug_info/{drug_name}` - Drug information
- `GET /available_drugs` - List of supported drugs
- `GET /supported_languages` - Supported languages

## 📁 Project Structure

```
medsafe/
├── main.py                 # FastAPI backend
├── frontend.py            # Streamlit frontend
├── run_medsafe.py         # Startup script
├── requirements.txt       # Dependencies
├── start_medsafe.bat      # Windows startup
├── .env                   # Environment variables
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── database/
│   └── drug_database.py  # Drug database and interactions
├── components/
│   ├── ai_services.py    # AI model integrations
│   ├── file_processor.py # File upload processing
│   └── pdf_generator.py  # PDF report generation
├── static/               # Static assets
├── templates/            # HTML templates
├── pages/               # Additional pages
└── data/
    └── ddi_mapped_with_rxcui.csv  # Drug interaction dataset
```

## 🔑 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
HF_API_KEY=your_huggingface_api_key_here
IBM_API_KEY=your_ibm_api_key_here
```

### API Keys Setup
1. **Hugging Face**: Get API key from [Hugging Face](https://huggingface.co/settings/tokens)
2. **IBM**: Get API key from [IBM Cloud](https://cloud.ibm.com/iam/apikeys)

## 🧪 Testing

### Example Prescriptions
Try these example prescriptions:

1. **Basic Interaction**:
   ```
   Take aspirin 500mg twice daily and ibuprofen 400mg for pain relief
   ```

2. **Multiple Drugs**:
   ```
   Patient should use amoxicillin 500mg three times daily for infection
   ```

3. **Complex Prescription**:
   ```
   Prescribe paracetamol for fever and aspirin for headache
   ```

### API Testing
Use the interactive API documentation at `http://localhost:8000/docs` to test endpoints directly.

## 🚀 Deployment

### Local Development
```bash
python run_medsafe.py
```

### Production Deployment
1. Set up environment variables
2. Install dependencies
3. Run with production server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
streamlit run frontend.py --server.port 8501
```

## 🔒 Security

- API keys stored in environment variables
- Input validation on all endpoints
- File upload size and type restrictions
- CORS configuration for frontend-backend communication

## 📊 Performance

- FastAPI for high-performance backend
- Async processing for AI model calls
- Caching for frequently accessed data
- Optimized database queries

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

**Medical Disclaimer**: This application is for educational and demonstration purposes only. It should not be used as a substitute for professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare providers for medical decisions.

## 🆘 Support

For issues and questions:
1. Check the API documentation at `http://localhost:8000/docs`
2. Review the console logs for error messages
3. Ensure all dependencies are properly installed
4. Verify API keys are correctly configured

## 🎉 Hackathon Ready

This application is designed to be:
- **Production-ready** with comprehensive error handling
- **Scalable** with modular architecture
- **User-friendly** with intuitive interface
- **Feature-rich** with advanced AI capabilities
- **Well-documented** for easy understanding and extension

Perfect for hackathons, demos, and real-world medical AI applications!
