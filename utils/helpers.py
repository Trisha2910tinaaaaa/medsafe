import pandas as pd
import requests
import os
import json
from typing import List, Dict, Any, Optional
import time
from dotenv import load_dotenv
import re

load_dotenv()

class DrugInteractionAnalyzer:
    def __init__(self):
        self.interactions_df = pd.read_csv('data/ddi_mapped_with_rxcui.csv')
        self.hf_api_token = os.getenv('HUGGINGFACE_API_TOKEN')
        self.ibm_api_token = os.getenv('IBM_GRANITE_API_TOKEN')
        
        # Hugging Face API endpoints
        self.hf_medical_ner_url = "https://api-inference.huggingface.co/models/samant/medical-ner"
        self.hf_headers = {"Authorization": f"Bearer {self.hf_api_token}"} if self.hf_api_token else {}
        
        # IBM Granite API endpoint
        self.ibm_granite_url = "https://api-inference.huggingface.co/models/ibm-granite/granite-3.0-8b-instruct"
        self.ibm_headers = {"Authorization": f"Bearer {self.ibm_api_token}"} if self.ibm_api_token else {}
        
    def extract_drugs_from_text(self, prescription_text: str) -> List[Dict[str, Any]]:
        """
        Extract drug names and dosages using Hugging Face's medical-ner model
        """
        try:
            if not self.hf_api_token:
                # Fallback to enhanced keyword-based approach
                return self._fallback_drug_extraction(prescription_text)
            
            # Call Hugging Face medical-ner model
            payload = {"inputs": prescription_text}
            response = requests.post(
                self.hf_medical_ner_url, 
                headers=self.hf_headers, 
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                entities = response.json()
                return self._process_ner_entities(entities, prescription_text)
            else:
                return self._fallback_drug_extraction(prescription_text)
                
        except Exception as e:
            print(f"Error with Hugging Face API: {e}")
            return self._fallback_drug_extraction(prescription_text)
    
    def _process_ner_entities(self, entities: List[Dict], text: str) -> List[Dict[str, Any]]:
        """Process NER entities to extract drugs and dosages"""
        extracted_drugs = []
        
        # Enhanced drug database
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
                # Extract dosage information
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
        # Look for dosage patterns
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
    
    def _fallback_drug_extraction(self, prescription_text: str) -> List[Dict[str, Any]]:
        """Enhanced fallback drug extraction"""
        return self._process_ner_entities([], prescription_text)
    
    def check_interactions(self, drugs: List[str]) -> List[Dict[str, Any]]:
        """
        Check for drug interactions between the provided drugs
        """
        interactions = []
        
        for i, drug1 in enumerate(drugs):
            for j, drug2 in enumerate(drugs[i+1:], i+1):
                # Check both directions
                interaction1 = self.interactions_df[
                    (self.interactions_df['drug1'] == drug1) & 
                    (self.interactions_df['drug2'] == drug2)
                ]
                
                interaction2 = self.interactions_df[
                    (self.interactions_df['drug1'] == drug2) & 
                    (self.interactions_df['drug2'] == drug1)
                ]
                
                if not interaction1.empty:
                    interaction = interaction1.iloc[0]
                    interactions.append({
                        'drug1': drug1,
                        'drug2': drug2,
                        'description': interaction['interaction_description'],
                        'severity': interaction['severity']
                    })
                elif not interaction2.empty:
                    interaction = interaction2.iloc[0]
                    interactions.append({
                        'drug1': drug1,
                        'drug2': drug2,
                        'description': interaction['interaction_description'],
                        'severity': interaction['severity']
                    })
        
        return interactions
    
    def get_ai_analysis(self, interaction: Dict[str, Any]) -> str:
        """
        Get AI-powered analysis using IBM Granite model
        """
        try:
            if not self.ibm_api_token:
                return self._fallback_ai_analysis(interaction)
            
            # Create comprehensive prompt for IBM Granite
            prompt = f"""
            As a medical AI assistant, analyze this drug interaction:
            
            Drug 1: {interaction['drug1']}
            Drug 2: {interaction['drug2']}
            Interaction: {interaction['description']}
            Severity: {interaction['severity']}
            
            Provide a comprehensive analysis including:
            1. Severity assessment with detailed explanation
            2. Patient-friendly explanation of the interaction
            3. Clinical implications and risks
            4. Specific recommendations for healthcare providers
            5. Alternative medication suggestions
            6. Monitoring requirements
            
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
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', '')
                else:
                    return self._fallback_ai_analysis(interaction)
            else:
                return self._fallback_ai_analysis(interaction)
                
        except Exception as e:
            print(f"Error with IBM Granite API: {e}")
            return self._fallback_ai_analysis(interaction)
    
    def _fallback_ai_analysis(self, interaction: Dict[str, Any]) -> str:
        """Enhanced fallback AI analysis"""
        severity_map = {
            'high': {
                'level': 'High Risk - Immediate medical attention may be required',
                'color': '🔴',
                'urgency': 'URGENT'
            },
            'medium': {
                'level': 'Medium Risk - Monitor closely and consult healthcare provider',
                'color': '🟡',
                'urgency': 'MODERATE'
            },
            'low': {
                'level': 'Low Risk - Generally safe but monitor for side effects',
                'color': '🟢',
                'urgency': 'LOW'
            }
        }
        
        severity_info = severity_map.get(interaction['severity'], severity_map['medium'])
        
        ai_analysis = f"""
        {severity_info['color']} **SEVERITY ASSESSMENT: {severity_info['urgency']}**
        
        **Risk Level:** {severity_info['level']}
        
        **📋 Clinical Analysis:**
        Taking {interaction['drug1'].title()} and {interaction['drug2'].title()} together may cause {interaction['description'].lower()}. 
        This interaction is classified as **{interaction['severity'].upper()}** risk based on clinical evidence.
        
        **🔬 Mechanism of Interaction:**
        - {interaction['drug1'].title()} and {interaction['drug2'].title()} may interact through pharmacokinetic or pharmacodynamic mechanisms
        - The interaction could affect drug absorption, metabolism, or elimination
        - Potential for additive or synergistic effects on target systems
        
        **⚠️ Clinical Implications:**
        - Increased risk of adverse effects
        - Potential for reduced therapeutic efficacy
        - Possible need for dosage adjustments
        - Enhanced monitoring requirements
        
        **💡 Recommendations:**
        - **Immediate:** Consult healthcare provider before combining these medications
        - **Monitoring:** Regular assessment of therapeutic response and adverse effects
        - **Alternatives:** Consider therapeutic alternatives if available
        - **Education:** Patient counseling on signs of adverse reactions
        
        **📊 Risk Factors:**
        - Patient age and comorbidities
        - Duration of concurrent therapy
        - Dosage levels of both medications
        - Individual patient factors (genetics, liver/renal function)
        
        **🔍 Monitoring Parameters:**
        - Clinical response to therapy
        - Laboratory parameters as appropriate
        - Signs and symptoms of adverse effects
        - Drug levels if therapeutic drug monitoring is available
        """
        
        return ai_analysis.strip()
    
    def get_dosage_recommendations(self, drug_name: str, patient_age: int, weight: float = None, renal_function: str = "normal") -> Dict[str, Any]:
        """
        Get comprehensive age-specific dosage recommendations
        """
        # Comprehensive dosage database
        dosage_data = {
            'aspirin': {
                'adult': {
                    'analgesic': '325-650mg every 4-6 hours',
                    'antiplatelet': '81-325mg once daily',
                    'max_daily': '4000mg',
                    'contraindications': ['Active bleeding', 'Peptic ulcer disease', 'Aspirin allergy']
                },
                'elderly': {
                    'analgesic': '325mg every 4-6 hours',
                    'antiplatelet': '81mg once daily',
                    'max_daily': '2000mg',
                    'contraindications': ['Active bleeding', 'Peptic ulcer disease', 'Aspirin allergy', 'Renal impairment']
                },
                'pediatric': {
                    'analgesic': '10-15mg/kg every 4-6 hours',
                    'antiplatelet': 'Not recommended under 18',
                    'max_daily': '60mg/kg',
                    'contraindications': ['Reye syndrome risk', 'Viral infections']
                }
            },
            'ibuprofen': {
                'adult': {
                    'analgesic': '200-400mg every 4-6 hours',
                    'anti-inflammatory': '400-800mg every 6-8 hours',
                    'max_daily': '3200mg',
                    'contraindications': ['Active peptic ulcer', 'Renal impairment', 'Heart failure']
                },
                'elderly': {
                    'analgesic': '200mg every 6-8 hours',
                    'anti-inflammatory': '400mg every 8 hours',
                    'max_daily': '1600mg',
                    'contraindications': ['Active peptic ulcer', 'Renal impairment', 'Heart failure', 'Hypertension']
                },
                'pediatric': {
                    'analgesic': '5-10mg/kg every 6-8 hours',
                    'anti-inflammatory': '10mg/kg every 6-8 hours',
                    'max_daily': '40mg/kg',
                    'contraindications': ['Dehydration', 'Renal impairment']
                }
            },
            'acetaminophen': {
                'adult': {
                    'analgesic': '500-1000mg every 4-6 hours',
                    'antipyretic': '500-1000mg every 4-6 hours',
                    'max_daily': '4000mg',
                    'contraindications': ['Liver disease', 'Alcohol abuse', 'G6PD deficiency']
                },
                'elderly': {
                    'analgesic': '500mg every 6 hours',
                    'antipyretic': '500mg every 6 hours',
                    'max_daily': '3000mg',
                    'contraindications': ['Liver disease', 'Alcohol abuse', 'Renal impairment']
                },
                'pediatric': {
                    'analgesic': '10-15mg/kg every 4-6 hours',
                    'antipyretic': '10-15mg/kg every 4-6 hours',
                    'max_daily': '75mg/kg',
                    'contraindications': ['Liver disease', 'Dehydration']
                }
            },
            'amoxicillin': {
                'adult': {
                    'standard': '500mg three times daily',
                    'high_dose': '875mg twice daily',
                    'max_daily': '3000mg',
                    'contraindications': ['Penicillin allergy', 'Mononucleosis']
                },
                'elderly': {
                    'standard': '500mg twice daily',
                    'high_dose': '875mg once daily',
                    'max_daily': '2000mg',
                    'contraindications': ['Penicillin allergy', 'Renal impairment']
                },
                'pediatric': {
                    'standard': '20-40mg/kg divided in 3 doses',
                    'high_dose': '45mg/kg divided in 2 doses',
                    'max_daily': '2000mg',
                    'contraindications': ['Penicillin allergy', 'Mononucleosis']
                }
            }
        }
        
        if patient_age < 18:
            age_group = 'pediatric'
        elif patient_age > 65:
            age_group = 'elderly'
        else:
            age_group = 'adult'
        
        drug_info = dosage_data.get(drug_name, {})
        age_specific_info = drug_info.get(age_group, {})
        
        # Adjust for renal function
        renal_adjustments = {
            'mild': 0.75,
            'moderate': 0.5,
            'severe': 0.25,
            'dialysis': 0.1
        }
        
        renal_factor = renal_adjustments.get(renal_function.lower(), 1.0)
        
        return {
            'drug': drug_name,
            'recommended_dosage': age_specific_info.get('standard', 'Consult healthcare provider'),
            'age_group': age_group,
            'patient_age': patient_age,
            'renal_adjustment': renal_factor,
            'contraindications': age_specific_info.get('contraindications', []),
            'max_daily': age_specific_info.get('max_daily', 'Consult healthcare provider'),
            'special_considerations': self._get_special_considerations(drug_name, patient_age, weight)
        }
    
    def _get_special_considerations(self, drug_name: str, age: int, weight: float) -> List[str]:
        """Get special considerations for specific drugs and patient factors"""
        considerations = []
        
        if age > 65:
            considerations.extend([
                "Increased risk of adverse effects",
                "May require lower dosages",
                "Monitor renal and hepatic function",
                "Increased fall risk with certain medications"
            ])
        
        if age < 18:
            considerations.extend([
                "Pediatric dosing based on weight/age",
                "Monitor for age-specific adverse effects",
                "Consider developmental factors"
            ])
        
        if weight and weight > 100:
            considerations.append("May require weight-based dosing adjustments")
        
        drug_specific = {
            'aspirin': ["Monitor for bleeding", "Avoid in children with viral infections"],
            'ibuprofen': ["Monitor renal function", "Take with food"],
            'acetaminophen': ["Monitor liver function", "Avoid alcohol"],
            'amoxicillin': ["Take on empty stomach", "Complete full course"]
        }
        
        considerations.extend(drug_specific.get(drug_name, []))
        return considerations
    
    def get_alternatives(self, drug_name: str, reason: str = "interaction") -> List[Dict[str, Any]]:
        """
        Get alternative medications with detailed information
        """
        alternatives_database = {
            'aspirin': [
                {
                    'name': 'Clopidogrel',
                    'brand': 'Plavix',
                    'class': 'Antiplatelet',
                    'indication': 'Cardiovascular protection',
                    'advantages': ['No GI irritation', 'Once daily dosing'],
                    'disadvantages': ['Higher cost', 'Requires prescription']
                },
                {
                    'name': 'Acetaminophen',
                    'brand': 'Tylenol',
                    'class': 'Analgesic/Antipyretic',
                    'indication': 'Pain and fever',
                    'advantages': ['No GI irritation', 'Safe for children'],
                    'disadvantages': ['No anti-inflammatory effect', 'Liver toxicity risk']
                }
            ],
            'ibuprofen': [
                {
                    'name': 'Acetaminophen',
                    'brand': 'Tylenol',
                    'class': 'Analgesic/Antipyretic',
                    'indication': 'Pain and fever',
                    'advantages': ['No GI irritation', 'Safe for children'],
                    'disadvantages': ['No anti-inflammatory effect']
                },
                {
                    'name': 'Naproxen',
                    'brand': 'Aleve',
                    'class': 'NSAID',
                    'indication': 'Pain and inflammation',
                    'advantages': ['Longer duration', 'Less frequent dosing'],
                    'disadvantages': ['GI irritation', 'Cardiovascular risk']
                }
            ],
            'acetaminophen': [
                {
                    'name': 'Ibuprofen',
                    'brand': 'Advil',
                    'class': 'NSAID',
                    'indication': 'Pain and inflammation',
                    'advantages': ['Anti-inflammatory effect', 'Good for inflammation'],
                    'disadvantages': ['GI irritation', 'Not for children under 6 months']
                },
                {
                    'name': 'Aspirin',
                    'brand': 'Bayer',
                    'class': 'NSAID/Antiplatelet',
                    'indication': 'Pain and cardiovascular protection',
                    'advantages': ['Cardiovascular benefits', 'Low cost'],
                    'disadvantages': ['GI irritation', 'Bleeding risk']
                }
            ]
        }
        
        return alternatives_database.get(drug_name, [])
    
    def get_drug_information(self, drug_name: str) -> Dict[str, Any]:
        """
        Get comprehensive drug information
        """
        drug_info = {
            'aspirin': {
                'generic_name': 'Acetylsalicylic Acid',
                'drug_class': 'Nonsteroidal Anti-inflammatory Drug (NSAID)',
                'mechanism': 'Inhibits cyclooxygenase enzymes, reducing prostaglandin synthesis',
                'indications': ['Pain relief', 'Fever reduction', 'Cardiovascular protection'],
                'side_effects': ['GI irritation', 'Bleeding risk', 'Reye syndrome in children'],
                'pregnancy_category': 'C',
                'half_life': '2-3 hours',
                'metabolism': 'Hepatic',
                'excretion': 'Renal'
            },
            'ibuprofen': {
                'generic_name': 'Ibuprofen',
                'drug_class': 'Nonsteroidal Anti-inflammatory Drug (NSAID)',
                'mechanism': 'Inhibits cyclooxygenase-1 and cyclooxygenase-2',
                'indications': ['Pain relief', 'Inflammation reduction', 'Fever'],
                'side_effects': ['GI irritation', 'Renal impairment', 'Cardiovascular risk'],
                'pregnancy_category': 'C',
                'half_life': '2-4 hours',
                'metabolism': 'Hepatic',
                'excretion': 'Renal'
            }
        }
        
        return drug_info.get(drug_name, {})

class APIError(Exception):
    pass
