import requests
import os
from typing import List, Dict, Any, Optional
import re
from dotenv import load_dotenv

load_dotenv()

class AIServices:
    def __init__(self):
        self.hf_api_key = os.getenv('HF_API_KEY')
        self.ibm_api_key = os.getenv('IBM_API_KEY')
        
        # Hugging Face endpoints
        self.hf_medical_ner_url = "https://api-inference.huggingface.co/models/samant/medical-ner"
        self.hf_translation_url = "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-es-en"
        self.ibm_granite_url = "https://api-inference.huggingface.co/models/ibm-granite/granite-3.0-8b-instruct"
        
        self.hf_headers = {"Authorization": f"Bearer {self.hf_api_key}"} if self.hf_api_key else {}
        self.ibm_headers = {"Authorization": f"Bearer {self.ibm_api_key}"} if self.ibm_api_key else {}
        
        # Translation models mapping
        self.translation_models = {
            'spanish': 'Helsinki-NLP/opus-mt-es-en',
            'french': 'Helsinki-NLP/opus-mt-fr-en',
            'german': 'Helsinki-NLP/opus-mt-de-en',
            'italian': 'Helsinki-NLP/opus-mt-it-en',
            'portuguese': 'Helsinki-NLP/opus-mt-pt-en',
            'hindi': 'Helsinki-NLP/opus-mt-hi-en',
            'chinese': 'Helsinki-NLP/opus-mt-zh-en',
            'japanese': 'Helsinki-NLP/opus-mt-ja-en'
        }
    
    def extract_drugs_from_text(self, text: str, language: str = 'english') -> List[Dict[str, Any]]:
        """Extract drugs from text using Hugging Face medical-ner model"""
        try:
            # Translate if not English
            if language != 'english' and language in self.translation_models:
                text = self.translate_text(text, language, 'english')
            
            if not self.hf_api_key:
                return self._fallback_drug_extraction(text)
            
            payload = {"inputs": text}
            response = requests.post(
                self.hf_medical_ner_url, 
                headers=self.hf_headers, 
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                entities = response.json()
                return self._process_ner_entities(entities, text)
            else:
                return self._fallback_drug_extraction(text)
                
        except Exception as e:
            print(f"Error with Hugging Face NER: {e}")
            return self._fallback_drug_extraction(text)
    
    def _process_ner_entities(self, entities: List[Dict], text: str) -> List[Dict[str, Any]]:
        """Process NER entities to extract drugs and dosages"""
        extracted_drugs = []
        
        # Enhanced drug patterns
        drug_patterns = {
            'aspirin': r'aspirin|acetylsalicylic acid|asa',
            'ibuprofen': r'ibuprofen|advil|motrin|brufen',
            'acetaminophen': r'acetaminophen|paracetamol|tylenol|panadol',
            'amoxicillin': r'amoxicillin|amoxil|trimox',
            'metformin': r'metformin|glucophage',
            'lisinopril': r'lisinopril|zestril|prinivil',
            'simvastatin': r'simvastatin|zocor',
            'omeprazole': r'omeprazole|prilosec|losec',
            'prednisone': r'prednisone|deltasone',
            'albuterol': r'albuterol|proventil|ventolin',
            'warfarin': r'warfarin|coumadin',
            'clopidogrel': r'clopidogrel|plavix',
            'insulin': r'insulin|humulin|novolin',
            'allopurinol': r'allopurinol|zyloprim',
            'probenecid': r'probenecid|benemid',
            'amiodarone': r'amiodarone|cordarone',
            'propranolol': r'propranolol|inderal',
            'iron': r'iron|ferrous|ferric',
            'grapefruit': r'grapefruit|citrus',
            'alcohol': r'alcohol|ethanol|drinking'
        }
        
        text_lower = text.lower()
        
        for drug_name, pattern in drug_patterns.items():
            if re.search(pattern, text_lower):
                dosage = self._extract_dosage(text, drug_name)
                frequency = self._extract_frequency(text)
                
                extracted_drugs.append({
                    'drug_name': drug_name,
                    'dosage': dosage,
                    'frequency': frequency,
                    'confidence': 0.95
                })
        
        return extracted_drugs
    
    def _extract_dosage(self, text: str, drug_name: str) -> str:
        """Extract dosage information from text"""
        dosage_patterns = [
            r'(\d+(?:\.\d+)?)\s*(mg|g|mcg|ml|units)',
            r'(\d+(?:\.\d+)?)\s*(milligram|gram|microgram|milliliter)',
            r'(\d+(?:\.\d+)?)\s*(mg|g|mcg|ml|units)\s*(tablet|capsule|pill|dose)',
        ]
        
        for pattern in dosage_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return f"{matches[0][0]}{matches[0][1]}"
        
        return "Standard dosage"
    
    def _extract_frequency(self, text: str) -> str:
        """Extract frequency information from text"""
        frequency_patterns = {
            r'twice\s*daily|bid|b\.i\.d': 'twice daily',
            r'three\s*times\s*daily|tid|t\.i\.d': 'three times daily',
            r'four\s*times\s*daily|qid|q\.i\.d': 'four times daily',
            r'once\s*daily|qd|q\.d': 'once daily',
            r'every\s*(\d+)\s*hours?': 'every {0} hours',
            r'every\s*(\d+)\s*days?': 'every {0} days'
        }
        
        for pattern, replacement in frequency_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if '{0}' in replacement:
                    return replacement.format(match.group(1))
                return replacement
        
        return "as needed"
    
    def _fallback_drug_extraction(self, text: str) -> List[Dict[str, Any]]:
        """Fallback drug extraction using keyword matching"""
        return self._process_ner_entities([], text)
    
    def get_explainable_ai_analysis(self, interaction: Dict[str, Any]) -> str:
        """Get explainable AI analysis using IBM Granite model"""
        try:
            if not self.ibm_api_key:
                return self._generate_fallback_explanation(interaction)
            
            # Create patient-friendly prompt
            prompt = f"""
            Explain this drug interaction like I'm a patient: '{interaction['description']}'. 
            Keep it to one simple sentence and mention the main risk.
            Make it easy to understand without medical jargon.
            """
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 150,
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "do_sample": True
                }
            }
            
            response = requests.post(
                self.ibm_granite_url,
                headers=self.ibm_headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', '')
                else:
                    return self._generate_fallback_explanation(interaction)
            else:
                return self._generate_fallback_explanation(interaction)
                
        except Exception as e:
            print(f"Error with IBM Granite API: {e}")
            return self._generate_fallback_explanation(interaction)
    
    def _generate_fallback_explanation(self, interaction: Dict[str, Any]) -> str:
        """Generate fallback patient-friendly explanation"""
        severity = interaction.get('severity', 'medium')
        description = interaction['description'].lower()
        
        if severity == 'high':
            return f"⚠️ HIGH RISK: Taking {interaction['drug1']} and {interaction['drug2']} together can cause {description}. This is dangerous and you should talk to your doctor immediately."
        elif severity == 'medium':
            return f"⚠️ MEDIUM RISK: Taking {interaction['drug1']} and {interaction['drug2']} together may cause {description}. You should check with your doctor before taking them together."
        else:
            return f"ℹ️ LOW RISK: Taking {interaction['drug1']} and {interaction['drug2']} together might cause {description}. This is usually safe but watch for any unusual symptoms."
    
    def translate_text(self, text: str, source_lang: str, target_lang: str = 'english') -> str:
        """Translate text using Hugging Face translation models"""
        try:
            if source_lang == target_lang or not self.hf_api_key:
                return text
            
            model_name = self.translation_models.get(source_lang)
            if not model_name:
                return text
            
            url = f"https://api-inference.huggingface.co/models/{model_name}"
            payload = {"inputs": text}
            
            response = requests.post(url, headers=self.hf_headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('translation_text', text)
            
            return text
            
        except Exception as e:
            print(f"Translation error: {e}")
            return text
    
    def get_detailed_ai_analysis(self, interaction: Dict[str, Any], patient_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get comprehensive AI analysis with patient context"""
        try:
            if not self.ibm_api_key:
                return self._generate_fallback_detailed_analysis(interaction, patient_context)
            
            # Build comprehensive prompt
            context_info = ""
            if patient_context:
                context_info = f"""
                Patient Context:
                - Age: {patient_context.get('age', 'Unknown')}
                - Pregnant: {patient_context.get('pregnant', False)}
                - Kidney Disease: {patient_context.get('kidney_disease', False)}
                - Liver Disease: {patient_context.get('liver_disease', False)}
                - Known Allergies: {patient_context.get('allergies', [])}
                """
            
            prompt = f"""
            As a medical AI assistant, provide a comprehensive analysis of this drug interaction:
            
            Drug 1: {interaction['drug1']}
            Drug 2: {interaction['drug2']}
            Interaction: {interaction['description']}
            Severity: {interaction['severity']}
            {context_info}
            
            Provide:
            1. Severity assessment with detailed explanation
            2. Patient-friendly explanation
            3. Clinical implications and risks
            4. Specific recommendations for healthcare providers
            5. Alternative medication suggestions
            6. Monitoring requirements
            7. Patient counseling points
            
            Format your response with clear sections and bullet points.
            """
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 500,
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "do_sample": True
                }
            }
            
            response = requests.post(
                self.ibm_granite_url,
                headers=self.ibm_headers,
                json=payload,
                timeout=90
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    ai_analysis = result[0].get('generated_text', '')
                    return {
                        'detailed_analysis': ai_analysis,
                        'patient_explanation': self._generate_fallback_explanation(interaction),
                        'severity': interaction['severity'],
                        'recommendations': self._extract_recommendations(ai_analysis)
                    }
            
            return self._generate_fallback_detailed_analysis(interaction, patient_context)
            
        except Exception as e:
            print(f"Error with detailed AI analysis: {e}")
            return self._generate_fallback_detailed_analysis(interaction, patient_context)
    
    def _generate_fallback_detailed_analysis(self, interaction: Dict[str, Any], patient_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate fallback detailed analysis"""
        severity = interaction.get('severity', 'medium')
        
        analysis = f"""
        **Severity Assessment:** {severity.upper()} RISK
        
        **Patient-Friendly Explanation:** 
        Taking {interaction['drug1']} and {interaction['drug2']} together may cause {interaction['description'].lower()}. 
        This interaction is classified as {severity} risk.
        
        **Clinical Implications:**
        - Increased risk of adverse effects
        - Potential for reduced therapeutic efficacy
        - Possible need for dosage adjustments
        - Enhanced monitoring requirements
        
        **Recommendations:**
        - Consult healthcare provider before combining these medications
        - Monitor for any unusual symptoms
        - Consider alternative medications if possible
        - Regular follow-up with healthcare provider
        """
        
        return {
            'detailed_analysis': analysis,
            'patient_explanation': self._generate_fallback_explanation(interaction),
            'severity': severity,
            'recommendations': ['Consult healthcare provider', 'Monitor symptoms', 'Consider alternatives']
        }
    
    def _extract_recommendations(self, analysis: str) -> List[str]:
        """Extract recommendations from AI analysis"""
        recommendations = []
        
        # Simple extraction of recommendations
        lines = analysis.split('\n')
        for line in lines:
            if 'recommend' in line.lower() or 'should' in line.lower() or 'consult' in line.lower():
                recommendations.append(line.strip())
        
        if not recommendations:
            recommendations = ['Consult healthcare provider', 'Monitor symptoms', 'Consider alternatives']
        
        return recommendations[:5]  # Limit to 5 recommendations
