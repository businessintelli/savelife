"""
AI Services API Routes for SaveLife.com Backend

This module provides REST API endpoints for all AI-powered features including:
- Campaign creation assistance
- Document verification
- Donor matching and recommendations
- Content optimization
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import json
import traceback

from src.services.campaign_ai import CampaignAI
from src.services.verification_ai import VerificationAI, DocumentType, VerificationStatus
from src.services.donor_matching_ai import DonorMatchingAI, MatchingStrategy

# Create blueprint for AI services
ai_bp = Blueprint('ai_services', __name__)

# Initialize AI services
campaign_ai = CampaignAI()
verification_ai = VerificationAI()
donor_matching_ai = DonorMatchingAI()


@ai_bp.route('/campaign/suggestions', methods=['POST'])
def get_campaign_suggestions():
    """
    Generate AI-powered campaign suggestions
    
    Expected JSON payload:
    {
        "name": "Patient name",
        "medical_condition": "Description of medical condition",
        "treatment_plan": "Treatment details",
        "insurance_status": "Insurance coverage status"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['name', 'medical_condition']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Generate suggestions
        suggestions = campaign_ai.generate_campaign_suggestions(data)
        
        # Convert to JSON-serializable format
        response = {
            'title': suggestions.title,
            'goal_amount': suggestions.goal_amount,
            'story_framework': suggestions.story_framework,
            'keywords': suggestions.keywords,
            'confidence_score': suggestions.confidence_score,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@ai_bp.route('/campaign/title-suggestions', methods=['POST'])
def get_title_suggestions():
    """
    Generate title suggestions for campaigns
    
    Expected JSON payload:
    {
        "name": "Patient name",
        "condition": "Medical condition",
        "treatment": "Treatment type (optional)"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        name = data.get('name', '')
        condition = data.get('condition', '')
        treatment = data.get('treatment', '')
        
        if not name or not condition:
            return jsonify({'error': 'Name and condition are required'}), 400
        
        suggestions = campaign_ai.generate_title_suggestions(name, condition, treatment)
        
        return jsonify({
            'suggestions': suggestions,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@ai_bp.route('/campaign/goal-recommendation', methods=['POST'])
def get_goal_recommendation():
    """
    Get AI-powered funding goal recommendation
    
    Expected JSON payload:
    {
        "medical_condition": "Description of condition",
        "treatment_details": "Treatment plan details",
        "insurance_coverage": "Insurance status"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        condition_description = data.get('medical_condition', '')
        treatment_details = data.get('treatment_details', '')
        insurance_coverage = data.get('insurance_coverage', '')
        
        if not condition_description:
            return jsonify({'error': 'Medical condition description is required'}), 400
        
        # Analyze condition first
        condition_analysis = campaign_ai.analyze_medical_condition(condition_description)
        
        # Calculate goal recommendation
        goal_recommendation = campaign_ai.calculate_goal_recommendation(
            condition_analysis, treatment_details, insurance_coverage
        )
        
        response = {
            'recommended_amount': goal_recommendation['recommended_amount'],
            'base_amount': goal_recommendation['base_amount'],
            'complexity_multiplier': goal_recommendation['complexity_multiplier'],
            'reasoning': goal_recommendation['reasoning'],
            'confidence': goal_recommendation['confidence'],
            'condition_analysis': condition_analysis,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@ai_bp.route('/campaign/story-optimization', methods=['POST'])
def optimize_story():
    """
    Analyze and optimize campaign story content
    
    Expected JSON payload:
    {
        "story": "Campaign story text",
        "medical_condition": "Medical condition for context"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        story = data.get('story', '')
        condition_description = data.get('medical_condition', '')
        
        if not story:
            return jsonify({'error': 'Story text is required'}), 400
        
        # Analyze condition for context
        condition_analysis = campaign_ai.analyze_medical_condition(condition_description)
        
        # Optimize story
        analysis = campaign_ai.optimize_campaign_story(story, condition_analysis)
        
        response = {
            'readability_score': analysis.readability_score,
            'emotional_impact_score': analysis.emotional_impact_score,
            'clarity_score': analysis.clarity_score,
            'suggestions': analysis.suggestions,
            'optimized_content': analysis.optimized_content,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@ai_bp.route('/campaign/writing-assistance', methods=['POST'])
def get_writing_assistance():
    """
    Get real-time writing assistance
    
    Expected JSON payload:
    {
        "current_text": "Current text being written",
        "section": "title|story|description"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        current_text = data.get('current_text', '')
        section = data.get('section', 'story')
        
        assistance = campaign_ai.get_writing_assistance(current_text, section)
        
        response = {
            'assistance': assistance,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@ai_bp.route('/verification/analyze-document', methods=['POST'])
def analyze_document():
    """
    Analyze document for verification
    
    Expected JSON payload:
    {
        "document_text": "Extracted text from document",
        "document_type": "medical_record|insurance_document|identity_document|medical_bill|treatment_plan"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        document_text = data.get('document_text', '')
        document_type_str = data.get('document_type', 'medical_record')
        
        if not document_text:
            return jsonify({'error': 'Document text is required'}), 400
        
        # Convert string to DocumentType enum
        try:
            document_type = DocumentType(document_type_str)
        except ValueError:
            return jsonify({'error': f'Invalid document type: {document_type_str}'}), 400
        
        # Analyze document
        analysis = verification_ai.analyze_document_text(document_text, document_type)
        
        response = {
            'document_type': analysis.document_type.value,
            'authenticity_score': analysis.authenticity_score,
            'extracted_data': analysis.extracted_data,
            'confidence_score': analysis.confidence_score,
            'verification_status': analysis.verification_status.value,
            'flags': analysis.flags,
            'processing_notes': analysis.processing_notes,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@ai_bp.route('/verification/verify-campaign', methods=['POST'])
def verify_campaign():
    """
    Perform comprehensive campaign verification
    
    Expected JSON payload:
    {
        "campaign_data": {
            "id": "campaign_id",
            "goal_amount": 50000,
            "description": "Campaign description"
        },
        "documents": [
            {
                "type": "medical_record",
                "text": "Document text content"
            }
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        campaign_data = data.get('campaign_data', {})
        documents = data.get('documents', [])
        
        if not campaign_data:
            return jsonify({'error': 'Campaign data is required'}), 400
        
        # Verify campaign
        verification_result = verification_ai.verify_campaign(campaign_data, documents)
        
        response = {
            'campaign_id': verification_result.campaign_id,
            'overall_status': verification_result.overall_status.value,
            'trust_score': verification_result.trust_score,
            'document_analyses': [
                {
                    'document_type': doc.document_type.value,
                    'authenticity_score': doc.authenticity_score,
                    'verification_status': doc.verification_status.value,
                    'flags': doc.flags,
                    'extracted_data': doc.extracted_data
                }
                for doc in verification_result.document_analyses
            ],
            'verification_timestamp': verification_result.verification_timestamp.isoformat(),
            'reviewer_notes': verification_result.reviewer_notes,
            'next_steps': verification_result.next_steps,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@ai_bp.route('/verification/fraud-detection', methods=['POST'])
def detect_fraud():
    """
    Detect potential fraud indicators
    
    Expected JSON payload:
    {
        "campaign_data": {
            "goal_amount": 50000,
            "description": "Campaign description"
        },
        "user_history": {
            "previous_campaigns": 2
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        campaign_data = data.get('campaign_data', {})
        user_history = data.get('user_history', {})
        
        if not campaign_data:
            return jsonify({'error': 'Campaign data is required'}), 400
        
        # Detect fraud indicators
        fraud_analysis = verification_ai.detect_fraud_indicators(campaign_data, user_history)
        
        response = {
            'fraud_score': fraud_analysis['fraud_score'],
            'risk_level': fraud_analysis['risk_level'],
            'detected_indicators': fraud_analysis['detected_indicators'],
            'recommendation': fraud_analysis['recommendation'],
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@ai_bp.route('/donor/profile', methods=['POST'])
def create_donor_profile():
    """
    Create comprehensive donor profile
    
    Expected JSON payload:
    {
        "id": "donor_123",
        "giving_history": [...],
        "demographics": {...},
        "location": {...},
        "preferences": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        if not data.get('id'):
            return jsonify({'error': 'Donor ID is required'}), 400
        
        # Create donor profile
        donor_profile = donor_matching_ai.create_donor_profile(data)
        
        response = {
            'donor_id': donor_profile.donor_id,
            'segment': donor_profile.segment.value,
            'interests': donor_profile.interests,
            'engagement_score': donor_profile.engagement_score,
            'lifetime_value': donor_profile.lifetime_value,
            'demographics': donor_profile.demographics,
            'location': donor_profile.location,
            'preferences': donor_profile.preferences,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@ai_bp.route('/donor/matching', methods=['POST'])
def find_matching_campaigns():
    """
    Find matching campaigns for a donor
    
    Expected JSON payload:
    {
        "donor_data": {
            "id": "donor_123",
            "giving_history": [...],
            "demographics": {...}
        },
        "available_campaigns": [...],
        "strategy": "hybrid|content_based|collaborative_filtering|geographic|demographic"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        donor_data = data.get('donor_data', {})
        available_campaigns = data.get('available_campaigns', [])
        strategy_str = data.get('strategy', 'hybrid')
        
        if not donor_data:
            return jsonify({'error': 'Donor data is required'}), 400
        
        if not available_campaigns:
            return jsonify({'error': 'Available campaigns list is required'}), 400
        
        # Convert strategy string to enum
        try:
            strategy = MatchingStrategy(strategy_str)
        except ValueError:
            return jsonify({'error': f'Invalid matching strategy: {strategy_str}'}), 400
        
        # Create donor profile
        donor_profile = donor_matching_ai.create_donor_profile(donor_data)
        
        # Find matching campaigns
        matching_result = donor_matching_ai.find_matching_campaigns(
            donor_profile, available_campaigns, strategy
        )
        
        response = {
            'donor_id': matching_result.donor_id,
            'strategy_used': matching_result.strategy_used.value,
            'total_matches': matching_result.total_matches,
            'recommended_campaigns': [
                {
                    'campaign_id': match.campaign_id,
                    'match_score': match.match_score,
                    'reasoning': match.reasoning,
                    'recommended_amount': match.recommended_amount,
                    'optimal_timing': match.optimal_timing.isoformat(),
                    'personalized_message': match.personalized_message,
                    'confidence_level': match.confidence_level
                }
                for match in matching_result.recommended_campaigns
            ],
            'processing_timestamp': matching_result.processing_timestamp.isoformat(),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@ai_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for AI services"""
    try:
        # Test basic functionality of each service
        test_campaign_data = {
            'name': 'Test',
            'medical_condition': 'test condition'
        }
        
        # Test campaign AI
        campaign_ai.analyze_medical_condition('test condition')
        
        # Test verification AI
        verification_ai.analyze_document_text('test document', DocumentType.MEDICAL_RECORD)
        
        # Test donor matching AI
        test_donor_data = {'id': 'test', 'giving_history': []}
        donor_matching_ai.create_donor_profile(test_donor_data)
        
        return jsonify({
            'status': 'healthy',
            'services': {
                'campaign_ai': 'operational',
                'verification_ai': 'operational',
                'donor_matching_ai': 'operational'
            },
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


# Error handlers
@ai_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@ai_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405


@ai_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

