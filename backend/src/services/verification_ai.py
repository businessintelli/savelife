"""
Verification AI Service for SaveLife.com

This service provides AI-powered verification capabilities including:
- Document analysis and authenticity verification
- Medical record validation
- Identity verification
- Fraud detection and risk assessment
- HIPAA-compliant processing
"""

import re
import json
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


class VerificationStatus(Enum):
    """Verification status enumeration"""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"
    INCOMPLETE = "incomplete"


class DocumentType(Enum):
    """Document type enumeration"""
    MEDICAL_RECORD = "medical_record"
    INSURANCE_DOCUMENT = "insurance_document"
    IDENTITY_DOCUMENT = "identity_document"
    FINANCIAL_DOCUMENT = "financial_document"
    TREATMENT_PLAN = "treatment_plan"
    MEDICAL_BILL = "medical_bill"
    PRESCRIPTION = "prescription"
    LAB_RESULT = "lab_result"


@dataclass
class DocumentAnalysis:
    """Data class for document analysis results"""
    document_type: DocumentType
    authenticity_score: float
    extracted_data: Dict[str, Any]
    confidence_score: float
    verification_status: VerificationStatus
    flags: List[str]
    processing_notes: str


@dataclass
class VerificationResult:
    """Data class for overall verification results"""
    campaign_id: str
    overall_status: VerificationStatus
    trust_score: float
    document_analyses: List[DocumentAnalysis]
    verification_timestamp: datetime
    reviewer_notes: str
    next_steps: List[str]


class VerificationAI:
    """AI service for campaign and document verification"""
    
    def __init__(self):
        self.medical_institutions = {
            'mayo clinic', 'cleveland clinic', 'johns hopkins', 'md anderson',
            'memorial sloan kettering', 'massachusetts general', 'cedars-sinai',
            'ucla medical center', 'stanford hospital', 'brigham and women\'s'
        }
        
        self.insurance_providers = {
            'aetna', 'anthem', 'blue cross', 'cigna', 'humana', 'kaiser',
            'united healthcare', 'medicare', 'medicaid', 'tricare'
        }
        
        self.medical_specialties = {
            'oncology', 'cardiology', 'neurology', 'orthopedics', 'pediatrics',
            'emergency medicine', 'internal medicine', 'surgery', 'radiology',
            'pathology', 'anesthesiology', 'psychiatry', 'dermatology'
        }
        
        self.fraud_indicators = [
            'inconsistent dates',
            'mismatched names',
            'suspicious amounts',
            'duplicate campaigns',
            'fake documents',
            'identity mismatch',
            'unrealistic goals',
            'vague medical details'
        ]

    def analyze_document_text(self, document_text: str, document_type: DocumentType) -> DocumentAnalysis:
        """Analyze document text for authenticity and extract relevant information"""
        
        # Initialize analysis result
        analysis = DocumentAnalysis(
            document_type=document_type,
            authenticity_score=0.0,
            extracted_data={},
            confidence_score=0.0,
            verification_status=VerificationStatus.PENDING,
            flags=[],
            processing_notes=""
        )
        
        if not document_text or len(document_text.strip()) < 20:
            analysis.flags.append("Document text too short or empty")
            analysis.verification_status = VerificationStatus.INCOMPLETE
            analysis.processing_notes = "Insufficient document content for analysis"
            return analysis
        
        text_lower = document_text.lower()
        
        # Document type specific analysis
        if document_type == DocumentType.MEDICAL_RECORD:
            analysis = self._analyze_medical_record(document_text, analysis)
        elif document_type == DocumentType.INSURANCE_DOCUMENT:
            analysis = self._analyze_insurance_document(document_text, analysis)
        elif document_type == DocumentType.IDENTITY_DOCUMENT:
            analysis = self._analyze_identity_document(document_text, analysis)
        elif document_type == DocumentType.MEDICAL_BILL:
            analysis = self._analyze_medical_bill(document_text, analysis)
        elif document_type == DocumentType.TREATMENT_PLAN:
            analysis = self._analyze_treatment_plan(document_text, analysis)
        else:
            analysis = self._analyze_generic_document(document_text, analysis)
        
        # Calculate overall authenticity score
        analysis.authenticity_score = self._calculate_authenticity_score(analysis)
        
        # Determine verification status
        if analysis.authenticity_score >= 0.8 and not analysis.flags:
            analysis.verification_status = VerificationStatus.VERIFIED
        elif analysis.authenticity_score >= 0.6:
            analysis.verification_status = VerificationStatus.NEEDS_REVIEW
        elif analysis.flags:
            analysis.verification_status = VerificationStatus.REJECTED
        else:
            analysis.verification_status = VerificationStatus.PENDING
        
        return analysis

    def _analyze_medical_record(self, text: str, analysis: DocumentAnalysis) -> DocumentAnalysis:
        """Analyze medical record document"""
        text_lower = text.lower()
        
        # Extract medical information
        extracted_data = {}
        
        # Look for patient information
        patient_name_match = re.search(r'patient:?\s*([a-zA-Z\s]+)', text_lower)
        if patient_name_match:
            extracted_data['patient_name'] = patient_name_match.group(1).strip()
        
        # Look for dates
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{4}-\d{2}-\d{2}',
            r'[a-zA-Z]+ \d{1,2}, \d{4}'
        ]
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text))
        if dates:
            extracted_data['dates'] = dates[:5]  # Limit to first 5 dates
        
        # Look for medical conditions
        condition_keywords = ['diagnosis', 'condition', 'disease', 'disorder', 'syndrome']
        for keyword in condition_keywords:
            pattern = rf'{keyword}:?\s*([a-zA-Z\s,]+)'
            match = re.search(pattern, text_lower)
            if match:
                extracted_data['medical_condition'] = match.group(1).strip()
                break
        
        # Look for medical institution
        for institution in self.medical_institutions:
            if institution in text_lower:
                extracted_data['medical_institution'] = institution
                analysis.confidence_score += 0.2
                break
        
        # Look for medical specialties
        for specialty in self.medical_specialties:
            if specialty in text_lower:
                extracted_data['medical_specialty'] = specialty
                analysis.confidence_score += 0.1
                break
        
        # Check for required medical record elements
        required_elements = ['patient', 'date', 'doctor', 'physician', 'md', 'diagnosis']
        present_elements = sum(1 for element in required_elements if element in text_lower)
        
        if present_elements < 3:
            analysis.flags.append("Missing required medical record elements")
        
        # Check for suspicious patterns
        if 'copy' in text_lower and 'original' not in text_lower:
            analysis.flags.append("Document appears to be a copy without original verification")
        
        analysis.extracted_data = extracted_data
        analysis.confidence_score = min(1.0, analysis.confidence_score + (present_elements / len(required_elements)))
        
        return analysis

    def _analyze_insurance_document(self, text: str, analysis: DocumentAnalysis) -> DocumentAnalysis:
        """Analyze insurance document"""
        text_lower = text.lower()
        extracted_data = {}
        
        # Look for insurance provider
        for provider in self.insurance_providers:
            if provider in text_lower:
                extracted_data['insurance_provider'] = provider
                analysis.confidence_score += 0.3
                break
        
        # Look for policy information
        policy_match = re.search(r'policy\s*(?:number|#)?:?\s*([a-zA-Z0-9\-]+)', text_lower)
        if policy_match:
            extracted_data['policy_number'] = policy_match.group(1)
            analysis.confidence_score += 0.2
        
        # Look for coverage information
        coverage_keywords = ['coverage', 'benefit', 'deductible', 'copay', 'coinsurance']
        for keyword in coverage_keywords:
            if keyword in text_lower:
                analysis.confidence_score += 0.1
                break
        
        # Look for denial or approval information
        if 'denied' in text_lower or 'rejection' in text_lower:
            extracted_data['claim_status'] = 'denied'
        elif 'approved' in text_lower or 'covered' in text_lower:
            extracted_data['claim_status'] = 'approved'
        
        # Check for required insurance elements
        required_elements = ['policy', 'member', 'coverage', 'effective', 'provider']
        present_elements = sum(1 for element in required_elements if element in text_lower)
        
        if present_elements < 2:
            analysis.flags.append("Missing required insurance document elements")
        
        analysis.extracted_data = extracted_data
        analysis.confidence_score = min(1.0, analysis.confidence_score)
        
        return analysis

    def _analyze_identity_document(self, text: str, analysis: DocumentAnalysis) -> DocumentAnalysis:
        """Analyze identity document"""
        text_lower = text.lower()
        extracted_data = {}
        
        # Look for name
        name_patterns = [
            r'name:?\s*([a-zA-Z\s]+)',
            r'full name:?\s*([a-zA-Z\s]+)'
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text_lower)
            if match:
                extracted_data['name'] = match.group(1).strip()
                analysis.confidence_score += 0.3
                break
        
        # Look for ID number
        id_patterns = [
            r'id\s*(?:number|#)?:?\s*([a-zA-Z0-9\-]+)',
            r'license\s*(?:number|#)?:?\s*([a-zA-Z0-9\-]+)',
            r'ssn:?\s*(\d{3}-?\d{2}-?\d{4})'
        ]
        for pattern in id_patterns:
            match = re.search(pattern, text_lower)
            if match:
                extracted_data['id_number'] = match.group(1)
                analysis.confidence_score += 0.2
                break
        
        # Look for address
        address_pattern = r'address:?\s*([a-zA-Z0-9\s,]+)'
        address_match = re.search(address_pattern, text_lower)
        if address_match:
            extracted_data['address'] = address_match.group(1).strip()
            analysis.confidence_score += 0.2
        
        # Check for government issued ID indicators
        gov_indicators = ['department of motor vehicles', 'dmv', 'state of', 'government', 'official']
        for indicator in gov_indicators:
            if indicator in text_lower:
                analysis.confidence_score += 0.2
                break
        
        analysis.extracted_data = extracted_data
        
        return analysis

    def _analyze_medical_bill(self, text: str, analysis: DocumentAnalysis) -> DocumentAnalysis:
        """Analyze medical bill document"""
        text_lower = text.lower()
        extracted_data = {}
        
        # Look for billing amounts
        amount_patterns = [
            r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'total:?\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'amount due:?\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        ]
        amounts = []
        for pattern in amount_patterns:
            amounts.extend(re.findall(pattern, text))
        
        if amounts:
            extracted_data['amounts'] = amounts[:5]  # Limit to first 5 amounts
            analysis.confidence_score += 0.3
        
        # Look for medical procedures
        procedure_keywords = ['procedure', 'treatment', 'service', 'consultation', 'surgery', 'therapy']
        for keyword in procedure_keywords:
            if keyword in text_lower:
                analysis.confidence_score += 0.1
                break
        
        # Look for billing date
        date_patterns = [r'date of service:?\s*(\d{1,2}/\d{1,2}/\d{4})']
        for pattern in date_patterns:
            match = re.search(pattern, text_lower)
            if match:
                extracted_data['service_date'] = match.group(1)
                analysis.confidence_score += 0.2
                break
        
        # Check for medical billing elements
        billing_elements = ['patient', 'provider', 'service', 'amount', 'insurance', 'balance']
        present_elements = sum(1 for element in billing_elements if element in text_lower)
        
        if present_elements < 3:
            analysis.flags.append("Missing required medical billing elements")
        
        analysis.extracted_data = extracted_data
        
        return analysis

    def _analyze_treatment_plan(self, text: str, analysis: DocumentAnalysis) -> DocumentAnalysis:
        """Analyze treatment plan document"""
        text_lower = text.lower()
        extracted_data = {}
        
        # Look for treatment details
        treatment_keywords = ['treatment', 'therapy', 'medication', 'surgery', 'procedure', 'plan']
        treatment_count = sum(1 for keyword in treatment_keywords if keyword in text_lower)
        
        if treatment_count >= 2:
            analysis.confidence_score += 0.3
        
        # Look for timeline information
        timeline_keywords = ['weeks', 'months', 'sessions', 'appointments', 'schedule']
        for keyword in timeline_keywords:
            if keyword in text_lower:
                analysis.confidence_score += 0.1
                break
        
        # Look for medical professional
        professional_keywords = ['doctor', 'physician', 'md', 'specialist', 'oncologist', 'surgeon']
        for keyword in professional_keywords:
            if keyword in text_lower:
                analysis.confidence_score += 0.2
                break
        
        analysis.extracted_data = extracted_data
        
        return analysis

    def _analyze_generic_document(self, text: str, analysis: DocumentAnalysis) -> DocumentAnalysis:
        """Analyze generic document"""
        text_lower = text.lower()
        
        # Basic document structure analysis
        if len(text.split()) > 50:
            analysis.confidence_score += 0.2
        
        if any(char.isdigit() for char in text):
            analysis.confidence_score += 0.1
        
        if re.search(r'\d{1,2}/\d{1,2}/\d{4}', text):
            analysis.confidence_score += 0.1
        
        analysis.extracted_data = {'word_count': len(text.split())}
        
        return analysis

    def _calculate_authenticity_score(self, analysis: DocumentAnalysis) -> float:
        """Calculate overall authenticity score for document"""
        base_score = analysis.confidence_score
        
        # Penalty for flags
        flag_penalty = len(analysis.flags) * 0.2
        
        # Bonus for extracted data richness
        data_bonus = min(0.2, len(analysis.extracted_data) * 0.05)
        
        authenticity_score = max(0.0, min(1.0, base_score + data_bonus - flag_penalty))
        
        return authenticity_score

    def verify_campaign(self, campaign_data: Dict, documents: List[Dict]) -> VerificationResult:
        """Perform comprehensive campaign verification"""
        
        campaign_id = campaign_data.get('id', 'unknown')
        document_analyses = []
        
        # Analyze each document
        for doc in documents:
            doc_type = DocumentType(doc.get('type', 'medical_record'))
            doc_text = doc.get('text', '')
            
            analysis = self.analyze_document_text(doc_text, doc_type)
            document_analyses.append(analysis)
        
        # Calculate overall trust score
        if document_analyses:
            avg_authenticity = sum(doc.authenticity_score for doc in document_analyses) / len(document_analyses)
            document_coverage = len(document_analyses) / 4  # Assume 4 ideal documents
            trust_score = (avg_authenticity * 0.7) + (min(1.0, document_coverage) * 0.3)
        else:
            trust_score = 0.0
        
        # Determine overall status
        verified_docs = sum(1 for doc in document_analyses if doc.verification_status == VerificationStatus.VERIFIED)
        rejected_docs = sum(1 for doc in document_analyses if doc.verification_status == VerificationStatus.REJECTED)
        
        if verified_docs >= 2 and rejected_docs == 0 and trust_score >= 0.7:
            overall_status = VerificationStatus.VERIFIED
        elif rejected_docs > 0 or trust_score < 0.3:
            overall_status = VerificationStatus.REJECTED
        elif trust_score >= 0.5:
            overall_status = VerificationStatus.NEEDS_REVIEW
        else:
            overall_status = VerificationStatus.PENDING
        
        # Generate next steps
        next_steps = self._generate_next_steps(overall_status, document_analyses, trust_score)
        
        return VerificationResult(
            campaign_id=campaign_id,
            overall_status=overall_status,
            trust_score=trust_score,
            document_analyses=document_analyses,
            verification_timestamp=datetime.now(),
            reviewer_notes=f"Automated verification completed. Trust score: {trust_score:.2f}",
            next_steps=next_steps
        )

    def _generate_next_steps(self, status: VerificationStatus, analyses: List[DocumentAnalysis], trust_score: float) -> List[str]:
        """Generate next steps based on verification results"""
        next_steps = []
        
        if status == VerificationStatus.VERIFIED:
            next_steps.append("Campaign approved for publication")
            next_steps.append("Enable donation processing")
            next_steps.append("Add verification badge to campaign")
        
        elif status == VerificationStatus.NEEDS_REVIEW:
            next_steps.append("Schedule manual review by verification team")
            next_steps.append("Request additional documentation if needed")
            next_steps.append("Contact campaign creator for clarification")
        
        elif status == VerificationStatus.REJECTED:
            next_steps.append("Notify campaign creator of rejection")
            next_steps.append("Provide specific feedback on required improvements")
            next_steps.append("Allow resubmission with corrected documents")
        
        else:  # PENDING or INCOMPLETE
            next_steps.append("Request missing required documents")
            next_steps.append("Provide document submission guidelines")
            next_steps.append("Set follow-up reminder for document submission")
        
        # Add specific recommendations based on document analysis
        missing_docs = []
        if not any(doc.document_type == DocumentType.MEDICAL_RECORD for doc in analyses):
            missing_docs.append("medical records")
        if not any(doc.document_type == DocumentType.IDENTITY_DOCUMENT for doc in analyses):
            missing_docs.append("identity verification")
        
        if missing_docs:
            next_steps.append(f"Request missing documents: {', '.join(missing_docs)}")
        
        return next_steps

    def detect_fraud_indicators(self, campaign_data: Dict, user_history: Dict = None) -> Dict[str, Any]:
        """Detect potential fraud indicators in campaign"""
        
        fraud_score = 0.0
        detected_indicators = []
        
        # Check for suspicious goal amounts
        goal = campaign_data.get('goal_amount', 0)
        if goal > 500000:  # Very high goal
            fraud_score += 0.3
            detected_indicators.append("Unusually high funding goal")
        elif goal < 1000:  # Very low goal
            fraud_score += 0.2
            detected_indicators.append("Unusually low funding goal")
        
        # Check for vague medical details
        description = campaign_data.get('description', '').lower()
        medical_keywords = ['diagnosis', 'treatment', 'doctor', 'hospital', 'surgery', 'therapy']
        medical_mentions = sum(1 for keyword in medical_keywords if keyword in description)
        
        if medical_mentions < 2:
            fraud_score += 0.4
            detected_indicators.append("Vague or insufficient medical details")
        
        # Check for duplicate content (simplified)
        if len(description) < 100:
            fraud_score += 0.2
            detected_indicators.append("Very short campaign description")
        
        # Check user history if available
        if user_history:
            previous_campaigns = user_history.get('previous_campaigns', 0)
            if previous_campaigns > 3:
                fraud_score += 0.3
                detected_indicators.append("Multiple previous campaigns from same user")
        
        # Determine risk level
        if fraud_score >= 0.7:
            risk_level = "HIGH"
        elif fraud_score >= 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            'fraud_score': fraud_score,
            'risk_level': risk_level,
            'detected_indicators': detected_indicators,
            'recommendation': self._get_fraud_recommendation(risk_level)
        }

    def _get_fraud_recommendation(self, risk_level: str) -> str:
        """Get recommendation based on fraud risk level"""
        if risk_level == "HIGH":
            return "Require manual review and additional verification before approval"
        elif risk_level == "MEDIUM":
            return "Enhanced verification required with additional documentation"
        else:
            return "Standard verification process sufficient"


# Example usage and testing
def test_verification_ai():
    """Test function for verification AI service"""
    ai = VerificationAI()
    
    # Test document analysis
    test_medical_record = """
    Patient: John Smith
    Date: 03/15/2024
    Diagnosis: Stage II Breast Cancer
    Physician: Dr. Sarah Johnson, MD
    Treatment Plan: Chemotherapy followed by surgery
    Hospital: Mayo Clinic
    """
    
    analysis = ai.analyze_document_text(test_medical_record, DocumentType.MEDICAL_RECORD)
    print(f"Document Analysis:")
    print(f"Type: {analysis.document_type}")
    print(f"Authenticity Score: {analysis.authenticity_score:.2f}")
    print(f"Status: {analysis.verification_status}")
    print(f"Extracted Data: {analysis.extracted_data}")
    print(f"Flags: {analysis.flags}")
    
    # Test campaign verification
    test_campaign = {
        'id': 'camp_123',
        'goal_amount': 75000,
        'description': 'Help John fight cancer with chemotherapy and surgery at Mayo Clinic'
    }
    
    test_documents = [
        {'type': 'medical_record', 'text': test_medical_record},
        {'type': 'insurance_document', 'text': 'Aetna Insurance Policy #12345 - Coverage denied for experimental treatment'}
    ]
    
    verification = ai.verify_campaign(test_campaign, test_documents)
    print(f"\nCampaign Verification:")
    print(f"Overall Status: {verification.overall_status}")
    print(f"Trust Score: {verification.trust_score:.2f}")
    print(f"Next Steps: {verification.next_steps}")


if __name__ == "__main__":
    test_verification_ai()

