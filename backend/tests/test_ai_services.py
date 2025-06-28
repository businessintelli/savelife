"""
Comprehensive test suite for SaveLife.com AI Services API

This test suite validates all AI service endpoints including campaign assistance,
verification services, and donor matching functionality. Tests cover both
successful operations and error handling scenarios.
"""

import pytest
import json
from datetime import datetime
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.services.campaign_ai import CampaignAI, CampaignSuggestions, StoryAnalysis
from src.services.verification_ai import VerificationAI, DocumentType, VerificationStatus, DocumentAnalysis
from src.services.donor_matching_ai import DonorMatchingAI, DonorSegment, MatchingStrategy


@pytest.fixture
def client():
    """Create test client for Flask application"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_campaign_data():
    """Sample campaign data for testing"""
    return {
        'name': 'Sarah Johnson',
        'medical_condition': 'Stage II breast cancer requiring chemotherapy and surgery',
        'treatment_plan': '6 months chemotherapy followed by mastectomy and reconstruction',
        'insurance_status': 'Limited coverage with high deductible'
    }


@pytest.fixture
def sample_document_data():
    """Sample document data for testing"""
    return {
        'document_text': '''
        MEDICAL RECORD
        Patient: Sarah Johnson
        Date: 03/15/2024
        Diagnosis: Stage II Breast Cancer (T2N1M0)
        Treatment Plan: Neoadjuvant chemotherapy followed by surgical resection
        Physician: Dr. Emily Chen, MD
        Institution: City Medical Center
        ''',
        'document_type': 'medical_record'
    }


@pytest.fixture
def sample_donor_data():
    """Sample donor data for testing"""
    return {
        'id': 'donor_123',
        'giving_history': [
            {
                'date': '2024-01-15',
                'amount': 100,
                'campaign_category': 'cancer'
            },
            {
                'date': '2024-02-20',
                'amount': 250,
                'campaign_category': 'surgery'
            }
        ],
        'demographics': {
            'age_group': '36-50',
            'income_level': 'medium',
            'location': {
                'city': 'Austin',
                'state': 'Texas'
            }
        },
        'preferences': {
            'contact_time': 'evening',
            'communication_method': 'email'
        }
    }


class TestCampaignAIEndpoints:
    """Test suite for Campaign AI service endpoints"""

    def test_campaign_suggestions_success(self, client, sample_campaign_data):
        """Test successful campaign suggestions generation"""
        response = client.post('/api/ai/campaign/suggestions',
                             json=sample_campaign_data,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify response structure
        assert 'title' in data
        assert 'goal_amount' in data
        assert 'story_framework' in data
        assert 'keywords' in data
        assert 'confidence_score' in data
        assert 'timestamp' in data
        
        # Verify data types and ranges
        assert isinstance(data['title'], str)
        assert isinstance(data['goal_amount'], (int, float))
        assert data['goal_amount'] > 0
        assert isinstance(data['keywords'], list)
        assert 0 <= data['confidence_score'] <= 1
        
        # Verify content quality
        assert len(data['title']) > 10  # Reasonable title length
        assert len(data['keywords']) > 0  # Should have relevant keywords

    def test_campaign_suggestions_missing_data(self, client):
        """Test campaign suggestions with missing required data"""
        incomplete_data = {'name': 'John Doe'}  # Missing medical_condition
        
        response = client.post('/api/ai/campaign/suggestions',
                             json=incomplete_data,
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'medical_condition' in data['error']

    def test_campaign_suggestions_no_data(self, client):
        """Test campaign suggestions with no data"""
        response = client.post('/api/ai/campaign/suggestions',
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'No data provided' in data['error']

    def test_title_suggestions_success(self, client):
        """Test successful title suggestions generation"""
        title_data = {
            'name': 'Sarah Johnson',
            'condition': 'breast cancer',
            'treatment': 'chemotherapy and surgery'
        }
        
        response = client.post('/api/ai/campaign/title-suggestions',
                             json=title_data,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'suggestions' in data
        assert 'timestamp' in data
        assert isinstance(data['suggestions'], list)
        assert len(data['suggestions']) > 0
        
        # Verify all suggestions are strings
        for suggestion in data['suggestions']:
            assert isinstance(suggestion, str)
            assert len(suggestion) > 5  # Reasonable minimum length

    def test_goal_recommendation_success(self, client):
        """Test successful goal recommendation"""
        goal_data = {
            'medical_condition': 'Stage II breast cancer',
            'treatment_details': 'Chemotherapy, surgery, and reconstruction',
            'insurance_coverage': 'High deductible health plan'
        }
        
        response = client.post('/api/ai/campaign/goal-recommendation',
                             json=goal_data,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify response structure
        assert 'recommended_amount' in data
        assert 'base_amount' in data
        assert 'complexity_multiplier' in data
        assert 'reasoning' in data
        assert 'confidence' in data
        assert 'condition_analysis' in data
        
        # Verify data types and ranges
        assert isinstance(data['recommended_amount'], (int, float))
        assert data['recommended_amount'] > 0
        assert 0 <= data['confidence'] <= 1

    def test_story_optimization_success(self, client):
        """Test successful story optimization"""
        story_data = {
            'story': 'Sarah is a 34-year-old mother who was recently diagnosed with breast cancer. She needs help paying for treatment.',
            'medical_condition': 'breast cancer'
        }
        
        response = client.post('/api/ai/campaign/story-optimization',
                             json=story_data,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify response structure
        assert 'readability_score' in data
        assert 'emotional_impact_score' in data
        assert 'clarity_score' in data
        assert 'suggestions' in data
        assert 'optimized_content' in data
        
        # Verify score ranges
        assert 0 <= data['readability_score'] <= 100
        assert 0 <= data['emotional_impact_score'] <= 100
        assert 0 <= data['clarity_score'] <= 100

    def test_writing_assistance_success(self, client):
        """Test successful writing assistance"""
        assistance_data = {
            'current_text': 'Help Sarah fight',
            'section': 'title'
        }
        
        response = client.post('/api/ai/campaign/writing-assistance',
                             json=assistance_data,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'assistance' in data
        assert 'timestamp' in data
        assert isinstance(data['assistance'], dict)


class TestVerificationAIEndpoints:
    """Test suite for Verification AI service endpoints"""

    def test_document_analysis_success(self, client, sample_document_data):
        """Test successful document analysis"""
        response = client.post('/api/ai/verification/analyze-document',
                             json=sample_document_data,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify response structure
        assert 'document_type' in data
        assert 'authenticity_score' in data
        assert 'extracted_data' in data
        assert 'confidence_score' in data
        assert 'verification_status' in data
        assert 'flags' in data
        assert 'processing_notes' in data
        
        # Verify data types and ranges
        assert data['document_type'] == 'medical_record'
        assert 0 <= data['authenticity_score'] <= 100
        assert 0 <= data['confidence_score'] <= 1
        assert isinstance(data['extracted_data'], dict)
        assert isinstance(data['flags'], list)

    def test_document_analysis_invalid_type(self, client):
        """Test document analysis with invalid document type"""
        invalid_data = {
            'document_text': 'Sample document text',
            'document_type': 'invalid_type'
        }
        
        response = client.post('/api/ai/verification/analyze-document',
                             json=invalid_data,
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Invalid document type' in data['error']

    def test_campaign_verification_success(self, client, sample_document_data):
        """Test successful campaign verification"""
        verification_data = {
            'campaign_data': {
                'id': 'camp_123',
                'goal_amount': 50000,
                'description': 'Help Sarah fight breast cancer'
            },
            'documents': [sample_document_data]
        }
        
        response = client.post('/api/ai/verification/verify-campaign',
                             json=verification_data,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify response structure
        assert 'campaign_id' in data
        assert 'overall_status' in data
        assert 'trust_score' in data
        assert 'document_analyses' in data
        assert 'verification_timestamp' in data
        assert 'reviewer_notes' in data
        assert 'next_steps' in data
        
        # Verify data types
        assert isinstance(data['document_analyses'], list)
        assert 0 <= data['trust_score'] <= 100

    def test_fraud_detection_success(self, client):
        """Test successful fraud detection"""
        fraud_data = {
            'campaign_data': {
                'goal_amount': 50000,
                'description': 'Help with medical expenses'
            },
            'user_history': {
                'previous_campaigns': 1
            }
        }
        
        response = client.post('/api/ai/verification/fraud-detection',
                             json=fraud_data,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify response structure
        assert 'fraud_score' in data
        assert 'risk_level' in data
        assert 'detected_indicators' in data
        assert 'recommendation' in data
        
        # Verify data types and ranges
        assert 0 <= data['fraud_score'] <= 100
        assert data['risk_level'] in ['low', 'medium', 'high']
        assert isinstance(data['detected_indicators'], list)


class TestDonorMatchingEndpoints:
    """Test suite for Donor Matching AI service endpoints"""

    def test_donor_profile_creation_success(self, client, sample_donor_data):
        """Test successful donor profile creation"""
        response = client.post('/api/ai/donor/profile',
                             json=sample_donor_data,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify response structure
        assert 'donor_id' in data
        assert 'segment' in data
        assert 'interests' in data
        assert 'engagement_score' in data
        assert 'lifetime_value' in data
        assert 'demographics' in data
        assert 'location' in data
        assert 'preferences' in data
        
        # Verify data types and ranges
        assert data['donor_id'] == 'donor_123'
        assert 0 <= data['engagement_score'] <= 100
        assert data['lifetime_value'] >= 0
        assert isinstance(data['interests'], list)

    def test_donor_profile_missing_id(self, client):
        """Test donor profile creation with missing ID"""
        incomplete_data = {
            'giving_history': [],
            'demographics': {}
        }
        
        response = client.post('/api/ai/donor/profile',
                             json=incomplete_data,
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Donor ID is required' in data['error']

    def test_campaign_matching_success(self, client, sample_donor_data):
        """Test successful campaign matching"""
        matching_data = {
            'donor_data': sample_donor_data,
            'available_campaigns': [
                {
                    'id': 'camp_1',
                    'title': 'Help Emma Fight Leukemia',
                    'category': 'cancer',
                    'goal_amount': 75000,
                    'location': {'state': 'Texas'}
                },
                {
                    'id': 'camp_2',
                    'title': 'Support Heart Surgery',
                    'category': 'surgery',
                    'goal_amount': 45000,
                    'location': {'state': 'California'}
                }
            ],
            'strategy': 'hybrid'
        }
        
        response = client.post('/api/ai/donor/matching',
                             json=matching_data,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify response structure
        assert 'donor_id' in data
        assert 'strategy_used' in data
        assert 'total_matches' in data
        assert 'recommended_campaigns' in data
        assert 'processing_timestamp' in data
        
        # Verify data types
        assert data['strategy_used'] == 'hybrid'
        assert isinstance(data['recommended_campaigns'], list)
        assert data['total_matches'] >= 0
        
        # Verify campaign recommendation structure
        if data['recommended_campaigns']:
            campaign = data['recommended_campaigns'][0]
            assert 'campaign_id' in campaign
            assert 'match_score' in campaign
            assert 'reasoning' in campaign
            assert 'recommended_amount' in campaign
            assert 'optimal_timing' in campaign
            assert 'personalized_message' in campaign
            assert 'confidence_level' in campaign
            
            # Verify score ranges
            assert 0 <= campaign['match_score'] <= 100
            assert campaign['recommended_amount'] > 0

    def test_campaign_matching_invalid_strategy(self, client, sample_donor_data):
        """Test campaign matching with invalid strategy"""
        matching_data = {
            'donor_data': sample_donor_data,
            'available_campaigns': [],
            'strategy': 'invalid_strategy'
        }
        
        response = client.post('/api/ai/donor/matching',
                             json=matching_data,
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Invalid matching strategy' in data['error']


class TestHealthAndErrorHandling:
    """Test suite for health checks and error handling"""

    def test_health_check_success(self, client):
        """Test health check endpoint"""
        response = client.get('/api/ai/health')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify response structure
        assert 'status' in data
        assert 'services' in data
        assert 'timestamp' in data
        
        # Verify service status
        assert data['status'] == 'healthy'
        assert 'campaign_ai' in data['services']
        assert 'verification_ai' in data['services']
        assert 'donor_matching_ai' in data['services']
        
        # Verify all services are operational
        for service, status in data['services'].items():
            assert status == 'operational'

    def test_404_error_handling(self, client):
        """Test 404 error handling"""
        response = client.get('/api/ai/nonexistent-endpoint')
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert 'Endpoint not found' in data['error']

    def test_405_error_handling(self, client):
        """Test 405 method not allowed error handling"""
        response = client.get('/api/ai/campaign/suggestions')  # Should be POST
        
        assert response.status_code == 405
        data = response.get_json()
        assert 'error' in data
        assert 'Method not allowed' in data['error']

    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = client.options('/api/ai/health')
        
        # Verify CORS headers are present
        assert 'Access-Control-Allow-Origin' in response.headers
        assert 'Access-Control-Allow-Methods' in response.headers
        assert 'Access-Control-Allow-Headers' in response.headers


class TestPerformanceAndSecurity:
    """Test suite for performance and security aspects"""

    def test_response_time_requirements(self, client, sample_campaign_data):
        """Test that API responses meet time requirements"""
        import time
        
        start_time = time.time()
        response = client.post('/api/ai/campaign/suggestions',
                             json=sample_campaign_data,
                             content_type='application/json')
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Campaign suggestions should complete within 3 seconds
        assert response_time < 3.0
        assert response.status_code == 200

    def test_large_payload_handling(self, client):
        """Test handling of large payloads"""
        large_story = 'A' * 10000  # 10KB story
        
        story_data = {
            'story': large_story,
            'medical_condition': 'cancer'
        }
        
        response = client.post('/api/ai/campaign/story-optimization',
                             json=story_data,
                             content_type='application/json')
        
        # Should handle large payloads gracefully
        assert response.status_code in [200, 413]  # Success or payload too large

    def test_input_sanitization(self, client):
        """Test input sanitization and validation"""
        malicious_data = {
            'name': '<script>alert("xss")</script>',
            'medical_condition': 'SELECT * FROM users; --'
        }
        
        response = client.post('/api/ai/campaign/suggestions',
                             json=malicious_data,
                             content_type='application/json')
        
        # Should handle malicious input safely
        if response.status_code == 200:
            data = response.get_json()
            # Verify no script tags in response
            assert '<script>' not in str(data)

    def test_concurrent_requests(self, client, sample_campaign_data):
        """Test handling of concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = client.post('/api/ai/campaign/suggestions',
                                 json=sample_campaign_data,
                                 content_type='application/json')
            results.append(response.status_code)
        
        # Create multiple threads for concurrent requests
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all requests completed successfully
        assert len(results) == 5
        for status_code in results:
            assert status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

