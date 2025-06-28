"""
Campaign AI Assistance Service for SaveLife.com

This service provides AI-powered assistance for campaign creation including:
- Title optimization and suggestions
- Story structure and writing assistance
- Goal amount recommendations
- Content optimization for maximum impact
"""

import re
import json
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CampaignSuggestion:
    """Data class for AI campaign suggestions"""
    title: str
    goal_amount: int
    story_framework: str
    keywords: List[str]
    confidence_score: float


@dataclass
class ContentAnalysis:
    """Data class for content analysis results"""
    readability_score: float
    emotional_impact_score: float
    clarity_score: float
    suggestions: List[str]
    optimized_content: str


class CampaignAI:
    """AI service for campaign creation assistance"""
    
    def __init__(self):
        self.medical_conditions = {
            'cancer': {
                'keywords': ['treatment', 'chemotherapy', 'radiation', 'surgery', 'oncology'],
                'avg_goal': 75000,
                'success_rate': 0.65,
                'story_framework': 'Medical Journey with Treatment Plan'
            },
            'emergency': {
                'keywords': ['urgent', 'immediate', 'emergency', 'critical', 'life-saving'],
                'avg_goal': 50000,
                'success_rate': 0.72,
                'story_framework': 'Emergency Medical Crisis'
            },
            'pediatric': {
                'keywords': ['child', 'children', 'pediatric', 'kids', 'family'],
                'avg_goal': 85000,
                'success_rate': 0.78,
                'story_framework': 'Family Support for Child\'s Medical Needs'
            },
            'chronic': {
                'keywords': ['chronic', 'ongoing', 'long-term', 'management', 'quality of life'],
                'avg_goal': 45000,
                'success_rate': 0.58,
                'story_framework': 'Living with Chronic Condition'
            },
            'mental_health': {
                'keywords': ['mental health', 'therapy', 'counseling', 'psychiatric', 'wellness'],
                'avg_goal': 25000,
                'success_rate': 0.62,
                'story_framework': 'Mental Health Recovery Journey'
            }
        }
        
        self.title_templates = [
            "Help {name} Fight {condition}",
            "Support {name}'s {treatment} Journey",
            "{name} Needs Your Help for {condition}",
            "Stand with {name} Against {condition}",
            "Give {name} Hope: {condition} Treatment Fund",
            "Help {name} Get Back to {goal}",
            "{name}'s Road to Recovery from {condition}",
            "Emergency Fund for {name}'s {treatment}"
        ]
        
        self.story_frameworks = {
            'Medical Journey with Treatment Plan': {
                'structure': [
                    'Personal introduction and background',
                    'Medical diagnosis and current situation',
                    'Detailed treatment plan and timeline',
                    'Financial breakdown and insurance gaps',
                    'How donations will be used specifically',
                    'Expected outcomes and recovery goals',
                    'Gratitude and call to action'
                ],
                'tone': 'hopeful, informative, grateful'
            },
            'Emergency Medical Crisis': {
                'structure': [
                    'Urgent situation description',
                    'Immediate medical needs',
                    'Time-sensitive treatment requirements',
                    'Financial emergency and immediate costs',
                    'How quickly funds are needed',
                    'Impact of community support',
                    'Urgent call to action'
                ],
                'tone': 'urgent, clear, appreciative'
            },
            'Family Support for Child\'s Medical Needs': {
                'structure': [
                    'Child\'s story and personality',
                    'Medical condition explanation (age-appropriate)',
                    'Treatment plan and specialist care',
                    'Family impact and support needs',
                    'Educational and developmental considerations',
                    'Long-term care and future planning',
                    'Community support appreciation'
                ],
                'tone': 'caring, protective, hopeful'
            }
        }

    def analyze_medical_condition(self, description: str) -> Dict[str, any]:
        """Analyze medical condition description to categorize and provide insights"""
        description_lower = description.lower()
        
        # Simple keyword-based classification
        condition_scores = {}
        for condition, data in self.medical_conditions.items():
            score = sum(1 for keyword in data['keywords'] if keyword in description_lower)
            if score > 0:
                condition_scores[condition] = score
        
        if not condition_scores:
            primary_condition = 'chronic'  # Default fallback
        else:
            primary_condition = max(condition_scores.keys(), key=lambda k: condition_scores[k])
        
        condition_data = self.medical_conditions[primary_condition]
        
        return {
            'primary_condition': primary_condition,
            'confidence': min(condition_scores.get(primary_condition, 1) * 0.2, 1.0),
            'suggested_goal': condition_data['avg_goal'],
            'success_rate': condition_data['success_rate'],
            'story_framework': condition_data['story_framework'],
            'relevant_keywords': condition_data['keywords']
        }

    def generate_title_suggestions(self, name: str, condition: str, treatment: str = None) -> List[str]:
        """Generate AI-powered title suggestions"""
        suggestions = []
        
        # Clean and format inputs
        name = name.strip() if name else "Our Loved One"
        condition = condition.strip() if condition else "Medical Treatment"
        treatment = treatment.strip() if treatment else "Treatment"
        
        # Generate titles from templates
        for template in self.title_templates:
            try:
                if '{name}' in template and '{condition}' in template:
                    title = template.format(name=name, condition=condition, treatment=treatment, goal="Health")
                elif '{name}' in template and '{treatment}' in template:
                    title = template.format(name=name, treatment=treatment, condition=condition, goal="Health")
                else:
                    title = template.format(name=name, condition=condition, treatment=treatment, goal="Health")
                
                suggestions.append(title)
            except KeyError:
                continue
        
        # Add some variation and randomization
        additional_suggestions = [
            f"Every Dollar Counts: {name}'s {condition} Fund",
            f"Hope for {name}: Medical Treatment Support",
            f"Community Support for {name}'s Recovery",
            f"{name}'s Fight Against {condition} - Join Us"
        ]
        
        suggestions.extend(additional_suggestions)
        
        # Return top 5 unique suggestions
        unique_suggestions = list(dict.fromkeys(suggestions))[:5]
        return unique_suggestions

    def calculate_goal_recommendation(self, condition_analysis: Dict, treatment_details: str, 
                                    insurance_coverage: str = None) -> Dict[str, any]:
        """Calculate recommended funding goal based on condition and treatment"""
        base_amount = condition_analysis['suggested_goal']
        
        # Adjust based on treatment complexity
        treatment_lower = treatment_details.lower() if treatment_details else ""
        
        # Treatment complexity multipliers
        complexity_factors = {
            'surgery': 1.3,
            'chemotherapy': 1.4,
            'radiation': 1.2,
            'transplant': 2.0,
            'experimental': 1.8,
            'clinical trial': 1.5,
            'specialist': 1.2,
            'emergency': 1.4,
            'icu': 1.6,
            'rehabilitation': 1.3
        }
        
        multiplier = 1.0
        for factor, value in complexity_factors.items():
            if factor in treatment_lower:
                multiplier = max(multiplier, value)
        
        # Insurance adjustment
        insurance_lower = insurance_coverage.lower() if insurance_coverage else ""
        if 'no insurance' in insurance_lower or 'uninsured' in insurance_lower:
            multiplier *= 1.5
        elif 'limited coverage' in insurance_lower or 'high deductible' in insurance_lower:
            multiplier *= 1.3
        elif 'denied' in insurance_lower:
            multiplier *= 1.4
        
        recommended_amount = int(base_amount * multiplier)
        
        # Round to nearest 5000 for cleaner goals
        recommended_amount = round(recommended_amount / 5000) * 5000
        
        return {
            'recommended_amount': recommended_amount,
            'base_amount': base_amount,
            'complexity_multiplier': multiplier,
            'reasoning': f"Based on {condition_analysis['primary_condition']} treatment complexity and insurance situation",
            'confidence': condition_analysis['confidence'] * 0.8  # Slightly lower confidence for goal prediction
        }

    def optimize_campaign_story(self, story: str, condition_analysis: Dict) -> ContentAnalysis:
        """Analyze and optimize campaign story content"""
        if not story or len(story.strip()) < 50:
            return ContentAnalysis(
                readability_score=0.3,
                emotional_impact_score=0.2,
                clarity_score=0.3,
                suggestions=[
                    "Story is too short. Aim for at least 200-300 words.",
                    "Include personal details to create emotional connection.",
                    "Explain the medical situation clearly.",
                    "Describe how donations will be used specifically."
                ],
                optimized_content=story
            )
        
        # Simple content analysis
        word_count = len(story.split())
        sentence_count = len([s for s in story.split('.') if s.strip()])
        avg_sentence_length = word_count / max(sentence_count, 1)
        
        # Readability score (simplified)
        readability_score = min(1.0, max(0.0, 1.0 - (avg_sentence_length - 15) / 20))
        
        # Emotional impact analysis (keyword-based)
        emotional_keywords = ['help', 'hope', 'family', 'love', 'support', 'grateful', 'thank', 'appreciate']
        emotional_count = sum(1 for word in story.lower().split() if word in emotional_keywords)
        emotional_impact_score = min(1.0, emotional_count / 10)
        
        # Clarity analysis
        medical_terms = condition_analysis.get('relevant_keywords', [])
        medical_clarity = sum(1 for term in medical_terms if term in story.lower())
        clarity_score = min(1.0, medical_clarity / max(len(medical_terms), 1))
        
        # Generate suggestions
        suggestions = []
        if readability_score < 0.6:
            suggestions.append("Consider using shorter sentences for better readability.")
        if emotional_impact_score < 0.4:
            suggestions.append("Add more personal details and emotional connection.")
        if clarity_score < 0.5:
            suggestions.append("Include more specific medical details about the condition.")
        if word_count < 200:
            suggestions.append("Expand your story to 200-300 words for better engagement.")
        if 'thank' not in story.lower() and 'grateful' not in story.lower():
            suggestions.append("Express gratitude to potential donors.")
        
        # Simple content optimization
        optimized_content = story
        if not suggestions:
            suggestions.append("Your story looks good! Consider adding specific details about how donations will be used.")
        
        return ContentAnalysis(
            readability_score=readability_score,
            emotional_impact_score=emotional_impact_score,
            clarity_score=clarity_score,
            suggestions=suggestions,
            optimized_content=optimized_content
        )

    def generate_campaign_suggestions(self, campaign_data: Dict) -> CampaignSuggestion:
        """Generate comprehensive campaign suggestions"""
        name = campaign_data.get('name', 'Patient')
        condition_description = campaign_data.get('medical_condition', '')
        treatment_details = campaign_data.get('treatment_plan', '')
        
        # Analyze condition
        condition_analysis = self.analyze_medical_condition(condition_description)
        
        # Generate title suggestions
        title_suggestions = self.generate_title_suggestions(
            name, condition_analysis['primary_condition'], treatment_details
        )
        
        # Calculate goal recommendation
        goal_recommendation = self.calculate_goal_recommendation(
            condition_analysis, treatment_details, campaign_data.get('insurance_status')
        )
        
        # Get story framework
        framework = self.story_frameworks.get(
            condition_analysis['story_framework'], 
            self.story_frameworks['Medical Journey with Treatment Plan']
        )
        
        return CampaignSuggestion(
            title=title_suggestions[0] if title_suggestions else f"Help {name} with Medical Treatment",
            goal_amount=goal_recommendation['recommended_amount'],
            story_framework=condition_analysis['story_framework'],
            keywords=condition_analysis['relevant_keywords'],
            confidence_score=min(condition_analysis['confidence'], goal_recommendation['confidence'])
        )

    def get_writing_assistance(self, current_text: str, section: str) -> Dict[str, any]:
        """Provide real-time writing assistance"""
        assistance = {
            'suggestions': [],
            'improvements': [],
            'tone_feedback': '',
            'length_feedback': ''
        }
        
        word_count = len(current_text.split()) if current_text else 0
        
        if section == 'title':
            if word_count > 10:
                assistance['suggestions'].append("Keep titles concise - aim for 5-8 words")
            if not any(word in current_text.lower() for word in ['help', 'support', 'fund']):
                assistance['suggestions'].append("Include action words like 'Help' or 'Support'")
                
        elif section == 'story':
            if word_count < 50:
                assistance['length_feedback'] = "Story is too short. Aim for 200-300 words."
            elif word_count > 500:
                assistance['length_feedback'] = "Story might be too long. Consider condensing to 300-400 words."
            else:
                assistance['length_feedback'] = f"Good length ({word_count} words). Target range is 200-300 words."
            
            if 'I' in current_text and current_text.count('I') > word_count * 0.1:
                assistance['tone_feedback'] = "Consider focusing more on the patient's needs rather than using 'I' frequently."
            
            if not any(word in current_text.lower() for word in ['thank', 'grateful', 'appreciate']):
                assistance['suggestions'].append("Express gratitude to potential donors")
        
        return assistance


# Example usage and testing functions
def test_campaign_ai():
    """Test function for campaign AI service"""
    ai = CampaignAI()
    
    # Test data
    test_campaign = {
        'name': 'Sarah',
        'medical_condition': 'breast cancer requiring chemotherapy and surgery',
        'treatment_plan': 'chemotherapy for 6 months followed by surgery and radiation',
        'insurance_status': 'limited coverage with high deductible'
    }
    
    # Test suggestions
    suggestions = ai.generate_campaign_suggestions(test_campaign)
    print(f"Title: {suggestions.title}")
    print(f"Goal: ${suggestions.goal_amount:,}")
    print(f"Framework: {suggestions.story_framework}")
    print(f"Confidence: {suggestions.confidence_score:.2f}")
    
    # Test story optimization
    test_story = "Sarah is a mother of two who was recently diagnosed with breast cancer. She needs help paying for treatment."
    condition_analysis = ai.analyze_medical_condition(test_campaign['medical_condition'])
    analysis = ai.optimize_campaign_story(test_story, condition_analysis)
    
    print(f"\nStory Analysis:")
    print(f"Readability: {analysis.readability_score:.2f}")
    print(f"Emotional Impact: {analysis.emotional_impact_score:.2f}")
    print(f"Clarity: {analysis.clarity_score:.2f}")
    print(f"Suggestions: {analysis.suggestions}")


if __name__ == "__main__":
    test_campaign_ai()

