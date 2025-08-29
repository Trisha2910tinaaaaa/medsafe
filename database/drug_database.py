import pandas as pd
from typing import Dict, List, Any

class DrugDatabase:
    def __init__(self):
        self.interactions_data = {
            'drug1': ['aspirin', 'aspirin', 'ibuprofen', 'acetaminophen', 'amoxicillin', 'metformin', 'lisinopril', 'simvastatin', 'omeprazole', 'prednisone', 'albuterol', 'warfarin', 'clopidogrel', 'insulin', 'allopurinol', 'probenecid', 'amiodarone', 'propranolol', 'iron', 'grapefruit', 'alcohol'],
            'drug2': ['ibuprofen', 'warfarin', 'warfarin', 'alcohol', 'allopurinol', 'insulin', 'ibuprofen', 'grapefruit', 'clopidogrel', 'ibuprofen', 'propranolol', 'aspirin', 'aspirin', 'metformin', 'amoxicillin', 'amoxicillin', 'simvastatin', 'albuterol', 'omeprazole', 'simvastatin', 'acetaminophen'],
            'interaction_description': [
                'May increase risk of gastrointestinal bleeding',
                'Increased risk of bleeding',
                'Increased risk of bleeding',
                'May cause liver damage',
                'May increase risk of skin rash',
                'May increase risk of hypoglycemia',
                'May reduce blood pressure lowering effect',
                'May increase simvastatin levels',
                'May reduce clopidogrel effectiveness',
                'May increase risk of stomach ulcers',
                'May reduce albuterol effectiveness',
                'Increased risk of bleeding',
                'Increased risk of bleeding',
                'May increase risk of hypoglycemia',
                'May increase risk of skin rash',
                'May increase amoxicillin levels',
                'May increase risk of muscle damage',
                'May reduce albuterol effectiveness',
                'May reduce iron absorption',
                'May increase simvastatin levels',
                'May cause liver damage'
            ],
            'severity': ['high', 'high', 'high', 'medium', 'low', 'medium', 'medium', 'high', 'medium', 'medium', 'medium', 'high', 'high', 'medium', 'low', 'low', 'high', 'medium', 'low', 'high', 'medium']
        }
        
        self.dosage_data = {
            'aspirin': {
                'adult': {'analgesic': '325-650mg every 4-6 hours', 'antiplatelet': '81-325mg once daily', 'max_daily': '4000mg'},
                'elderly': {'analgesic': '325mg every 4-6 hours', 'antiplatelet': '81mg once daily', 'max_daily': '2000mg'},
                'pediatric': {'analgesic': '10-15mg/kg every 4-6 hours', 'antiplatelet': 'Not recommended under 18', 'max_daily': '60mg/kg'}
            },
            'ibuprofen': {
                'adult': {'analgesic': '200-400mg every 4-6 hours', 'anti-inflammatory': '400-800mg every 6-8 hours', 'max_daily': '3200mg'},
                'elderly': {'analgesic': '200mg every 6-8 hours', 'anti-inflammatory': '400mg every 8 hours', 'max_daily': '1600mg'},
                'pediatric': {'analgesic': '5-10mg/kg every 6-8 hours', 'anti-inflammatory': '10mg/kg every 6-8 hours', 'max_daily': '40mg/kg'}
            },
            'acetaminophen': {
                'adult': {'analgesic': '500-1000mg every 4-6 hours', 'antipyretic': '500-1000mg every 4-6 hours', 'max_daily': '4000mg'},
                'elderly': {'analgesic': '500mg every 6 hours', 'antipyretic': '500mg every 6 hours', 'max_daily': '3000mg'},
                'pediatric': {'analgesic': '10-15mg/kg every 4-6 hours', 'antipyretic': '10-15mg/kg every 4-6 hours', 'max_daily': '75mg/kg'}
            },
            'amoxicillin': {
                'adult': {'standard': '500mg three times daily', 'high_dose': '875mg twice daily', 'max_daily': '3000mg'},
                'elderly': {'standard': '500mg twice daily', 'high_dose': '875mg once daily', 'max_daily': '2000mg'},
                'pediatric': {'standard': '20-40mg/kg divided in 3 doses', 'high_dose': '45mg/kg divided in 2 doses', 'max_daily': '2000mg'}
            },
            'metformin': {
                'adult': {'standard': '500mg twice daily', 'max_dose': '2550mg daily', 'max_daily': '2550mg'},
                'elderly': {'standard': '500mg once daily', 'max_dose': '2000mg daily', 'max_daily': '2000mg'},
                'pediatric': {'standard': '500mg twice daily', 'max_dose': '2000mg daily', 'max_daily': '2000mg'}
            }
        }
        
        self.alternatives_data = {
            'aspirin': [
                {'name': 'Clopidogrel', 'brand': 'Plavix', 'class': 'Antiplatelet', 'indication': 'Cardiovascular protection'},
                {'name': 'Acetaminophen', 'brand': 'Tylenol', 'class': 'Analgesic/Antipyretic', 'indication': 'Pain and fever'}
            ],
            'ibuprofen': [
                {'name': 'Acetaminophen', 'brand': 'Tylenol', 'class': 'Analgesic/Antipyretic', 'indication': 'Pain and fever'},
                {'name': 'Naproxen', 'brand': 'Aleve', 'class': 'NSAID', 'indication': 'Pain and inflammation'}
            ],
            'acetaminophen': [
                {'name': 'Ibuprofen', 'brand': 'Advil', 'class': 'NSAID', 'indication': 'Pain and inflammation'},
                {'name': 'Aspirin', 'brand': 'Bayer', 'class': 'NSAID/Antiplatelet', 'indication': 'Pain and cardiovascular protection'}
            ],
            'amoxicillin': [
                {'name': 'Azithromycin', 'brand': 'Zithromax', 'class': 'Macrolide', 'indication': 'Bacterial infections'},
                {'name': 'Doxycycline', 'brand': 'Vibramycin', 'class': 'Tetracycline', 'indication': 'Bacterial infections'}
            ]
        }
        
        self.drug_info = {
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
        
        self.interactions_df = pd.DataFrame(self.interactions_data)
    
    def get_interactions(self, drugs: List[str]) -> List[Dict[str, Any]]:
        """Get drug interactions for a list of drugs"""
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
    
    def get_dosage_recommendations(self, drug_name: str, age: int, weight: float = None, renal_function: str = "normal") -> Dict[str, Any]:
        """Get age-specific dosage recommendations"""
        drug_name_lower = drug_name.lower()
        
        if drug_name_lower not in self.dosage_data:
            return {
                'drug': drug_name,
                'recommended_dosage': 'Consult healthcare provider',
                'age_group': 'unknown',
                'patient_age': age,
                'contraindications': [],
                'max_daily': 'Consult healthcare provider',
                'special_considerations': []
            }
        
        # Determine age group
        if age < 18:
            age_group = 'pediatric'
        elif age > 65:
            age_group = 'elderly'
        else:
            age_group = 'adult'
        
        dosage_info = self.dosage_data[drug_name_lower].get(age_group, {})
        
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
            'recommended_dosage': dosage_info.get('standard', dosage_info.get('analgesic', 'Consult healthcare provider')),
            'age_group': age_group,
            'patient_age': age,
            'renal_adjustment': renal_factor,
            'contraindications': self._get_contraindications(drug_name_lower, age),
            'max_daily': dosage_info.get('max_daily', 'Consult healthcare provider'),
            'special_considerations': self._get_special_considerations(drug_name_lower, age, weight)
        }
    
    def get_alternatives(self, drug_name: str, reason: str = "interaction") -> List[Dict[str, Any]]:
        """Get alternative medications"""
        drug_name_lower = drug_name.lower()
        return self.alternatives_data.get(drug_name_lower, [])
    
    def get_drug_information(self, drug_name: str) -> Dict[str, Any]:
        """Get comprehensive drug information"""
        drug_name_lower = drug_name.lower()
        return self.drug_info.get(drug_name_lower, {})
    
    def _get_contraindications(self, drug_name: str, age: int) -> List[str]:
        """Get contraindications for a drug"""
        contraindications = {
            'aspirin': ['Active bleeding', 'Peptic ulcer disease', 'Aspirin allergy'],
            'ibuprofen': ['Active peptic ulcer', 'Renal impairment', 'Heart failure'],
            'acetaminophen': ['Liver disease', 'Alcohol abuse', 'G6PD deficiency'],
            'amoxicillin': ['Penicillin allergy', 'Mononucleosis'],
            'metformin': ['Severe renal impairment', 'Metabolic acidosis', 'Heart failure']
        }
        
        base_contraindications = contraindications.get(drug_name, [])
        
        # Add age-specific contraindications
        if age < 18 and drug_name == 'aspirin':
            base_contraindications.append('Reye syndrome risk')
        
        return base_contraindications
    
    def _get_special_considerations(self, drug_name: str, age: int, weight: float) -> List[str]:
        """Get special considerations for specific drugs and patient factors"""
        considerations = []
        
        if age > 65:
            considerations.extend([
                "Increased risk of adverse effects",
                "May require lower dosages",
                "Monitor renal and hepatic function"
            ])
        
        if age < 18:
            considerations.extend([
                "Pediatric dosing based on weight/age",
                "Monitor for age-specific adverse effects"
            ])
        
        if weight and weight > 100:
            considerations.append("May require weight-based dosing adjustments")
        
        drug_specific = {
            'aspirin': ["Monitor for bleeding", "Avoid in children with viral infections"],
            'ibuprofen': ["Monitor renal function", "Take with food"],
            'acetaminophen': ["Monitor liver function", "Avoid alcohol"],
            'amoxicillin': ["Take on empty stomach", "Complete full course"],
            'metformin': ["Monitor blood glucose", "Take with meals"]
        }
        
        considerations.extend(drug_specific.get(drug_name, []))
        return considerations
