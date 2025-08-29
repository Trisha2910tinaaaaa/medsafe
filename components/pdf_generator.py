from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from typing import Dict, List, Any
import io
from datetime import datetime

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        # Subtitle style
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.darkblue
        )
        
        # Section style
        self.section_style = ParagraphStyle(
            'CustomSection',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkgreen
        )
        
        # Normal text style
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6
        )
        
        # Warning style
        self.warning_style = ParagraphStyle(
            'CustomWarning',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            textColor=colors.red
        )
        
        # Success style
        self.success_style = ParagraphStyle(
            'CustomSuccess',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            textColor=colors.darkgreen
        )
    
    def generate_analysis_report(self, analysis_data: Dict[str, Any]) -> bytes:
        """Generate comprehensive analysis report PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
        
        story = []
        
        # Header
        story.append(Paragraph("MedSafe - AI-Powered Prescription Verification", self.title_style))
        story.append(Paragraph(f"Analysis Report - {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", self.subtitle_style))
        story.append(Spacer(1, 20))
        
        # Original Prescription
        if analysis_data.get('original_text'):
            story.append(Paragraph("Original Prescription", self.section_style))
            story.append(Paragraph(analysis_data['original_text'], self.normal_style))
            story.append(Spacer(1, 15))
        
        # Drugs Identified
        if analysis_data.get('drugs_found'):
            story.append(Paragraph("Drugs Identified", self.section_style))
            drugs_text = ", ".join([drug.title() for drug in analysis_data['drugs_found']])
            story.append(Paragraph(f"<b>Detected drugs:</b> {drugs_text}", self.normal_style))
            story.append(Spacer(1, 15))
        
        # Drug Interactions
        if analysis_data.get('interactions'):
            story.append(Paragraph("Drug Interactions Analysis", self.section_style))
            
            for i, interaction in enumerate(analysis_data['interactions'], 1):
                # Interaction header
                severity_color = self._get_severity_color(interaction.get('severity', 'medium'))
                interaction_title = f"Interaction {i}: {interaction['drug1'].title()} + {interaction['drug2'].title()}"
                story.append(Paragraph(f"<b>{interaction_title}</b>", self.section_style))
                
                # Severity
                severity_text = f"<b>Severity:</b> {interaction['severity'].upper()}"
                story.append(Paragraph(severity_text, self.warning_style if interaction['severity'] == 'high' else self.normal_style))
                
                # Description
                story.append(Paragraph(f"<b>Description:</b> {interaction['description']}", self.normal_style))
                
                # AI Analysis
                if interaction.get('ai_analysis'):
                    story.append(Paragraph("<b>AI Analysis:</b>", self.normal_style))
                    story.append(Paragraph(interaction['ai_analysis'], self.normal_style))
                
                story.append(Spacer(1, 10))
        else:
            story.append(Paragraph("Drug Interactions Analysis", self.section_style))
            story.append(Paragraph("✅ No drug interactions detected! Your prescription appears safe.", self.success_style))
            story.append(Spacer(1, 15))
        
        # Dosage Recommendations
        if analysis_data.get('dosage_results'):
            story.append(Paragraph("Dosage Recommendations", self.section_style))
            
            for result in analysis_data['dosage_results']:
                story.append(Paragraph(f"<b>{result['drug'].title()}</b>", self.section_style))
                story.append(Paragraph(f"<b>Recommended Dosage:</b> {result.get('recommended_dosage', 'Consult healthcare provider')}", self.normal_style))
                
                if result.get('alternatives'):
                    alternatives_text = ", ".join(result['alternatives'])
                    story.append(Paragraph(f"<b>Alternative Medications:</b> {alternatives_text}", self.normal_style))
                
                story.append(Spacer(1, 10))
        
        # Patient Context
        if analysis_data.get('patient_context'):
            story.append(Paragraph("Patient Context", self.section_style))
            context = analysis_data['patient_context']
            
            context_data = [
                ["Age", str(context.get('age', 'Unknown'))],
                ["Weight", f"{context.get('weight', 'Unknown')} kg"],
                ["Pregnant", "Yes" if context.get('pregnant') else "No"],
                ["Kidney Disease", "Yes" if context.get('kidney_disease') else "No"],
                ["Liver Disease", "Yes" if context.get('liver_disease') else "No"],
                ["Allergies", ", ".join(context.get('allergies', [])) or "None reported"]
            ]
            
            context_table = Table(context_data, colWidths=[2*inch, 3*inch])
            context_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(context_table)
            story.append(Spacer(1, 15))
        
        # Summary
        story.append(Paragraph("Summary", self.section_style))
        
        total_drugs = len(analysis_data.get('drugs_found', []))
        total_interactions = len(analysis_data.get('interactions', []))
        high_risk = len([i for i in analysis_data.get('interactions', []) if i.get('severity') == 'high'])
        medium_risk = len([i for i in analysis_data.get('interactions', []) if i.get('severity') == 'medium'])
        
        summary_data = [
            ["Metric", "Count"],
            ["Drugs Identified", str(total_drugs)],
            ["Total Interactions", str(total_interactions)],
            ["High Risk Interactions", str(high_risk)],
            ["Medium Risk Interactions", str(medium_risk)]
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 1*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Recommendations
        story.append(Paragraph("General Recommendations", self.section_style))
        recommendations = [
            "• Always consult with a healthcare provider before starting new medications",
            "• Keep a complete list of all medications you are taking",
            "• Report any unusual symptoms to your healthcare provider immediately",
            "• Follow dosage instructions carefully",
            "• Do not stop taking prescribed medications without consulting your doctor",
            "• Store medications properly and check expiration dates"
        ]
        
        for rec in recommendations:
            story.append(Paragraph(rec, self.normal_style))
        
        story.append(Spacer(1, 20))
        
        # Footer
        story.append(Paragraph("Generated by MedSafe AI-Powered Prescription Verification System", self.normal_style))
        story.append(Paragraph("This report is for informational purposes only and should not replace professional medical advice.", self.warning_style))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _get_severity_color(self, severity: str) -> str:
        """Get color for severity level"""
        severity_colors = {
            'high': colors.red,
            'medium': colors.orange,
            'low': colors.green
        }
        return severity_colors.get(severity.lower(), colors.black)
    
    def generate_simple_report(self, analysis_data: Dict[str, Any]) -> bytes:
        """Generate a simple analysis report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
        
        story = []
        
        # Header
        story.append(Paragraph("MedSafe Analysis Report", self.title_style))
        story.append(Spacer(1, 20))
        
        # Drugs found
        if analysis_data.get('drugs_found'):
            story.append(Paragraph("Drugs Identified", self.section_style))
            drugs_text = ", ".join([drug.title() for drug in analysis_data['drugs_found']])
            story.append(Paragraph(drugs_text, self.normal_style))
            story.append(Spacer(1, 15))
        
        # Interactions
        if analysis_data.get('interactions'):
            story.append(Paragraph("Drug Interactions", self.section_style))
            for interaction in analysis_data['interactions']:
                interaction_text = f"{interaction['drug1'].title()} + {interaction['drug2'].title()}: {interaction['description']}"
                story.append(Paragraph(interaction_text, self.normal_style))
        else:
            story.append(Paragraph("No interactions detected", self.success_style))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
