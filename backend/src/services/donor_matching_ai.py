"""
Donor Matching AI Service for SaveLife.com

This service provides AI-powered donor matching capabilities including:
- Personalized campaign recommendations for donors
- Donor segmentation and profiling
- Optimal timing for donation requests
- Geographic and demographic matching
- Interest-based campaign discovery
"""

import math
import random
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


class DonorSegment(Enum):
    """Donor segment enumeration"""
    FREQUENT_GIVER = "frequent_giver"
    OCCASIONAL_GIVER = "occasional_giver"
    FIRST_TIME_GIVER = "first_time_giver"
    LARGE_DONOR = "large_donor"
    MICRO_DONOR = "micro_donor"
    LOCAL_SUPPORTER = "local_supporter"
    CAUSE_SPECIFIC = "cause_specific"


class MatchingStrategy(Enum):
    """Matching strategy enumeration"""
    COLLABORATIVE_FILTERING = "collaborative_filtering"
    CONTENT_BASED = "content_based"
    HYBRID = "hybrid"
    GEOGRAPHIC = "geographic"
    DEMOGRAPHIC = "demographic"


@dataclass
class DonorProfile:
    """Data class for donor profile information"""
    donor_id: str
    segment: DonorSegment
    giving_history: List[Dict]
    interests: List[str]
    demographics: Dict[str, Any]
    location: Dict[str, str]
    preferences: Dict[str, Any]
    engagement_score: float
    lifetime_value: float


@dataclass
class CampaignMatch:
    """Data class for campaign match results"""
    campaign_id: str
    match_score: float
    reasoning: List[str]
    recommended_amount: float
    optimal_timing: datetime
    personalized_message: str
    confidence_level: float


@dataclass
class MatchingResult:
    """Data class for donor matching results"""
    donor_id: str
    recommended_campaigns: List[CampaignMatch]
    strategy_used: MatchingStrategy
    total_matches: int
    processing_timestamp: datetime


class DonorMatchingAI:
    """AI service for donor-campaign matching"""
    
    def __init__(self):
        self.medical_categories = {
            'cancer': {
                'keywords': ['cancer', 'oncology', 'chemotherapy', 'radiation', 'tumor'],
                'avg_donation': 150,
                'donor_segments': ['frequent_giver', 'large_donor', 'cause_specific']
            },
            'pediatric': {
                'keywords': ['child', 'children', 'pediatric', 'kids', 'baby'],
                'avg_donation': 200,
                'donor_segments': ['frequent_giver', 'occasional_giver', 'local_supporter']
            },
            'emergency': {
                'keywords': ['emergency', 'urgent', 'critical', 'immediate'],
                'avg_donation': 100,
                'donor_segments': ['frequent_giver', 'micro_donor', 'first_time_giver']
            },
            'mental_health': {
                'keywords': ['mental health', 'depression', 'anxiety', 'therapy'],
                'avg_donation': 75,
                'donor_segments': ['cause_specific', 'occasional_giver']
            },
            'chronic_illness': {
                'keywords': ['chronic', 'diabetes', 'arthritis', 'autoimmune'],
                'avg_donation': 125,
                'donor_segments': ['frequent_giver', 'cause_specific']
            }
        }
        
        self.demographic_factors = {
            'age': {
                '18-25': {'preferred_causes': ['mental_health', 'emergency'], 'avg_donation': 50},
                '26-35': {'preferred_causes': ['pediatric', 'emergency'], 'avg_donation': 100},
                '36-50': {'preferred_causes': ['cancer', 'pediatric'], 'avg_donation': 200},
                '51-65': {'preferred_causes': ['cancer', 'chronic_illness'], 'avg_donation': 300},
                '65+': {'preferred_causes': ['cancer', 'chronic_illness'], 'avg_donation': 250}
            },
            'income': {
                'low': {'donation_range': (10, 50), 'frequency': 'occasional'},
                'medium': {'donation_range': (25, 150), 'frequency': 'regular'},
                'high': {'donation_range': (100, 500), 'frequency': 'frequent'},
                'very_high': {'donation_range': (250, 1000), 'frequency': 'frequent'}
            }
        }
        
        self.engagement_patterns = {
            'morning': {'hours': [7, 8, 9, 10], 'engagement_multiplier': 1.2},
            'afternoon': {'hours': [12, 13, 14, 15], 'engagement_multiplier': 1.0},
            'evening': {'hours': [18, 19, 20, 21], 'engagement_multiplier': 1.4},
            'weekend': {'days': [5, 6], 'engagement_multiplier': 1.3}
        }

    def create_donor_profile(self, donor_data: Dict) -> DonorProfile:
        """Create comprehensive donor profile from available data"""
        
        donor_id = donor_data.get('id', 'unknown')
        giving_history = donor_data.get('giving_history', [])
        
        # Calculate engagement score
        engagement_score = self._calculate_engagement_score(donor_data)
        
        # Calculate lifetime value
        lifetime_value = sum(donation.get('amount', 0) for donation in giving_history)
        
        # Determine donor segment
        segment = self._determine_donor_segment(giving_history, lifetime_value, engagement_score)
        
        # Extract interests from giving history
        interests = self._extract_interests(giving_history)
        
        # Process demographics
        demographics = donor_data.get('demographics', {})
        location = donor_data.get('location', {})
        preferences = donor_data.get('preferences', {})
        
        return DonorProfile(
            donor_id=donor_id,
            segment=segment,
            giving_history=giving_history,
            interests=interests,
            demographics=demographics,
            location=location,
            preferences=preferences,
            engagement_score=engagement_score,
            lifetime_value=lifetime_value
        )

    def _calculate_engagement_score(self, donor_data: Dict) -> float:
        """Calculate donor engagement score based on activity patterns"""
        
        giving_history = donor_data.get('giving_history', [])
        profile_completeness = len(donor_data.get('demographics', {})) / 5  # Assume 5 key demographic fields
        
        # Recency of last donation
        if giving_history:
            last_donation_date = max(
                datetime.fromisoformat(donation.get('date', '2020-01-01')) 
                for donation in giving_history
            )
            days_since_last = (datetime.now() - last_donation_date).days
            recency_score = max(0, 1 - (days_since_last / 365))  # Decay over a year
        else:
            recency_score = 0
        
        # Frequency of donations
        donation_count = len(giving_history)
        frequency_score = min(1.0, donation_count / 10)  # Max score at 10+ donations
        
        # Average donation amount (normalized)
        if giving_history:
            avg_amount = sum(donation.get('amount', 0) for donation in giving_history) / len(giving_history)
            amount_score = min(1.0, avg_amount / 200)  # Max score at $200+ average
        else:
            amount_score = 0
        
        # Platform engagement
        platform_activity = donor_data.get('platform_activity', {})
        login_frequency = platform_activity.get('monthly_logins', 0)
        activity_score = min(1.0, login_frequency / 10)  # Max score at 10+ logins per month
        
        # Weighted engagement score
        engagement_score = (
            recency_score * 0.3 +
            frequency_score * 0.25 +
            amount_score * 0.2 +
            activity_score * 0.15 +
            profile_completeness * 0.1
        )
        
        return min(1.0, engagement_score)

    def _determine_donor_segment(self, giving_history: List[Dict], lifetime_value: float, engagement_score: float) -> DonorSegment:
        """Determine donor segment based on giving patterns"""
        
        donation_count = len(giving_history)
        
        if lifetime_value >= 1000:
            return DonorSegment.LARGE_DONOR
        elif donation_count >= 10:
            return DonorSegment.FREQUENT_GIVER
        elif donation_count >= 3:
            return DonorSegment.OCCASIONAL_GIVER
        elif donation_count == 0:
            return DonorSegment.FIRST_TIME_GIVER
        elif all(donation.get('amount', 0) <= 25 for donation in giving_history):
            return DonorSegment.MICRO_DONOR
        else:
            return DonorSegment.OCCASIONAL_GIVER

    def _extract_interests(self, giving_history: List[Dict]) -> List[str]:
        """Extract donor interests from giving history"""
        
        interests = []
        category_counts = {}
        
        for donation in giving_history:
            campaign_category = donation.get('campaign_category', '').lower()
            if campaign_category:
                category_counts[campaign_category] = category_counts.get(campaign_category, 0) + 1
        
        # Sort categories by frequency
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Extract top interests
        for category, count in sorted_categories[:5]:  # Top 5 interests
            if count >= 2:  # Must have donated to category at least twice
                interests.append(category)
        
        return interests

    def find_matching_campaigns(self, donor_profile: DonorProfile, available_campaigns: List[Dict], 
                               strategy: MatchingStrategy = MatchingStrategy.HYBRID) -> MatchingResult:
        """Find matching campaigns for a donor using specified strategy"""
        
        if strategy == MatchingStrategy.COLLABORATIVE_FILTERING:
            matches = self._collaborative_filtering_match(donor_profile, available_campaigns)
        elif strategy == MatchingStrategy.CONTENT_BASED:
            matches = self._content_based_match(donor_profile, available_campaigns)
        elif strategy == MatchingStrategy.GEOGRAPHIC:
            matches = self._geographic_match(donor_profile, available_campaigns)
        elif strategy == MatchingStrategy.DEMOGRAPHIC:
            matches = self._demographic_match(donor_profile, available_campaigns)
        else:  # HYBRID
            matches = self._hybrid_match(donor_profile, available_campaigns)
        
        # Sort matches by score and take top 10
        matches.sort(key=lambda x: x.match_score, reverse=True)
        top_matches = matches[:10]
        
        return MatchingResult(
            donor_id=donor_profile.donor_id,
            recommended_campaigns=top_matches,
            strategy_used=strategy,
            total_matches=len(top_matches),
            processing_timestamp=datetime.now()
        )

    def _content_based_match(self, donor_profile: DonorProfile, campaigns: List[Dict]) -> List[CampaignMatch]:
        """Match campaigns based on content similarity to donor interests"""
        
        matches = []
        
        for campaign in campaigns:
            match_score = 0.0
            reasoning = []
            
            campaign_category = campaign.get('category', '').lower()
            campaign_description = campaign.get('description', '').lower()
            campaign_location = campaign.get('location', {})
            
            # Interest matching
            if campaign_category in donor_profile.interests:
                match_score += 0.4
                reasoning.append(f"Matches your interest in {campaign_category}")
            
            # Keyword matching in description
            for interest in donor_profile.interests:
                if interest in campaign_description:
                    match_score += 0.1
                    reasoning.append(f"Campaign mentions {interest}")
            
            # Geographic proximity
            donor_location = donor_profile.location
            if (donor_location.get('state') == campaign_location.get('state') and
                donor_location.get('state')):
                match_score += 0.2
                reasoning.append("Campaign is in your state")
            elif (donor_location.get('country') == campaign_location.get('country') and
                  donor_location.get('country')):
                match_score += 0.1
                reasoning.append("Campaign is in your country")
            
            # Demographic alignment
            donor_age_group = donor_profile.demographics.get('age_group')
            if donor_age_group and campaign_category in self.demographic_factors['age'].get(donor_age_group, {}).get('preferred_causes', []):
                match_score += 0.2
                reasoning.append(f"Popular cause for your age group")
            
            # Campaign urgency
            urgency = campaign.get('urgency', 'normal')
            if urgency == 'immediate' and donor_profile.segment in [DonorSegment.FREQUENT_GIVER, DonorSegment.LARGE_DONOR]:
                match_score += 0.1
                reasoning.append("Urgent campaign matching your giving pattern")
            
            if match_score > 0.1:  # Only include campaigns with meaningful matches
                recommended_amount = self._calculate_recommended_amount(donor_profile, campaign)
                optimal_timing = self._calculate_optimal_timing(donor_profile)
                personalized_message = self._generate_personalized_message(donor_profile, campaign, reasoning)
                
                matches.append(CampaignMatch(
                    campaign_id=campaign.get('id', 'unknown'),
                    match_score=min(1.0, match_score),
                    reasoning=reasoning,
                    recommended_amount=recommended_amount,
                    optimal_timing=optimal_timing,
                    personalized_message=personalized_message,
                    confidence_level=min(1.0, match_score * donor_profile.engagement_score)
                ))
        
        return matches

    def _collaborative_filtering_match(self, donor_profile: DonorProfile, campaigns: List[Dict]) -> List[CampaignMatch]:
        """Match campaigns based on similar donor behavior patterns"""
        
        matches = []
        
        # Simplified collaborative filtering based on donor segment
        segment_preferences = {
            DonorSegment.FREQUENT_GIVER: ['cancer', 'pediatric', 'emergency'],
            DonorSegment.LARGE_DONOR: ['cancer', 'chronic_illness', 'pediatric'],
            DonorSegment.MICRO_DONOR: ['emergency', 'mental_health'],
            DonorSegment.LOCAL_SUPPORTER: ['emergency', 'pediatric'],
            DonorSegment.CAUSE_SPECIFIC: donor_profile.interests or ['cancer']
        }
        
        preferred_categories = segment_preferences.get(donor_profile.segment, ['emergency'])
        
        for campaign in campaigns:
            campaign_category = campaign.get('category', '').lower()
            
            if campaign_category in preferred_categories:
                # Base score from segment preference
                match_score = 0.6
                reasoning = [f"Popular with {donor_profile.segment.value.replace('_', ' ')} donors"]
                
                # Boost for exact interest match
                if campaign_category in donor_profile.interests:
                    match_score += 0.3
                    reasoning.append("Matches your previous giving pattern")
                
                # Success rate boost
                campaign_success_rate = campaign.get('predicted_success_rate', 0.5)
                if campaign_success_rate > 0.7:
                    match_score += 0.1
                    reasoning.append("High likelihood of reaching goal")
                
                recommended_amount = self._calculate_recommended_amount(donor_profile, campaign)
                optimal_timing = self._calculate_optimal_timing(donor_profile)
                personalized_message = self._generate_personalized_message(donor_profile, campaign, reasoning)
                
                matches.append(CampaignMatch(
                    campaign_id=campaign.get('id', 'unknown'),
                    match_score=min(1.0, match_score),
                    reasoning=reasoning,
                    recommended_amount=recommended_amount,
                    optimal_timing=optimal_timing,
                    personalized_message=personalized_message,
                    confidence_level=min(1.0, match_score * 0.8)  # Slightly lower confidence for collaborative filtering
                ))
        
        return matches

    def _geographic_match(self, donor_profile: DonorProfile, campaigns: List[Dict]) -> List[CampaignMatch]:
        """Match campaigns based on geographic proximity"""
        
        matches = []
        donor_location = donor_profile.location
        
        for campaign in campaigns:
            campaign_location = campaign.get('location', {})
            match_score = 0.0
            reasoning = []
            
            # Same city
            if (donor_location.get('city') == campaign_location.get('city') and
                donor_location.get('city')):
                match_score = 0.9
                reasoning.append(f"Campaign in your city: {donor_location['city']}")
            
            # Same state
            elif (donor_location.get('state') == campaign_location.get('state') and
                  donor_location.get('state')):
                match_score = 0.7
                reasoning.append(f"Campaign in your state: {donor_location['state']}")
            
            # Same country
            elif (donor_location.get('country') == campaign_location.get('country') and
                  donor_location.get('country')):
                match_score = 0.4
                reasoning.append(f"Campaign in your country: {donor_location['country']}")
            
            if match_score > 0:
                # Boost for local supporter segment
                if donor_profile.segment == DonorSegment.LOCAL_SUPPORTER:
                    match_score += 0.1
                    reasoning.append("You prefer supporting local causes")
                
                recommended_amount = self._calculate_recommended_amount(donor_profile, campaign)
                optimal_timing = self._calculate_optimal_timing(donor_profile)
                personalized_message = self._generate_personalized_message(donor_profile, campaign, reasoning)
                
                matches.append(CampaignMatch(
                    campaign_id=campaign.get('id', 'unknown'),
                    match_score=min(1.0, match_score),
                    reasoning=reasoning,
                    recommended_amount=recommended_amount,
                    optimal_timing=optimal_timing,
                    personalized_message=personalized_message,
                    confidence_level=min(1.0, match_score * 0.9)
                ))
        
        return matches

    def _demographic_match(self, donor_profile: DonorProfile, campaigns: List[Dict]) -> List[CampaignMatch]:
        """Match campaigns based on demographic alignment"""
        
        matches = []
        donor_demographics = donor_profile.demographics
        
        for campaign in campaigns:
            match_score = 0.0
            reasoning = []
            
            campaign_category = campaign.get('category', '').lower()
            
            # Age-based matching
            age_group = donor_demographics.get('age_group')
            if age_group:
                preferred_causes = self.demographic_factors['age'].get(age_group, {}).get('preferred_causes', [])
                if campaign_category in preferred_causes:
                    match_score += 0.5
                    reasoning.append(f"Popular cause for your age group ({age_group})")
            
            # Income-based matching
            income_level = donor_demographics.get('income_level')
            if income_level:
                income_data = self.demographic_factors['income'].get(income_level, {})
                campaign_goal = campaign.get('goal_amount', 0)
                
                # Match campaign size to donor capacity
                if income_level in ['high', 'very_high'] and campaign_goal > 50000:
                    match_score += 0.2
                    reasoning.append("Large campaign matching your giving capacity")
                elif income_level in ['low', 'medium'] and campaign_goal <= 50000:
                    match_score += 0.2
                    reasoning.append("Campaign size appropriate for your giving level")
            
            # Gender-based preferences (simplified)
            gender = donor_demographics.get('gender')
            if gender == 'female' and campaign_category in ['pediatric', 'mental_health']:
                match_score += 0.1
                reasoning.append("Campaign type with high female donor engagement")
            
            if match_score > 0:
                recommended_amount = self._calculate_recommended_amount(donor_profile, campaign)
                optimal_timing = self._calculate_optimal_timing(donor_profile)
                personalized_message = self._generate_personalized_message(donor_profile, campaign, reasoning)
                
                matches.append(CampaignMatch(
                    campaign_id=campaign.get('id', 'unknown'),
                    match_score=min(1.0, match_score),
                    reasoning=reasoning,
                    recommended_amount=recommended_amount,
                    optimal_timing=optimal_timing,
                    personalized_message=personalized_message,
                    confidence_level=min(1.0, match_score * 0.7)
                ))
        
        return matches

    def _hybrid_match(self, donor_profile: DonorProfile, campaigns: List[Dict]) -> List[CampaignMatch]:
        """Combine multiple matching strategies for optimal results"""
        
        # Get matches from different strategies
        content_matches = self._content_based_match(donor_profile, campaigns)
        collaborative_matches = self._collaborative_filtering_match(donor_profile, campaigns)
        geographic_matches = self._geographic_match(donor_profile, campaigns)
        demographic_matches = self._demographic_match(donor_profile, campaigns)
        
        # Combine and weight matches
        all_matches = {}
        
        # Weight different strategies
        strategy_weights = {
            'content': 0.4,
            'collaborative': 0.3,
            'geographic': 0.2,
            'demographic': 0.1
        }
        
        # Process content-based matches
        for match in content_matches:
            campaign_id = match.campaign_id
            if campaign_id not in all_matches:
                all_matches[campaign_id] = {
                    'match': match,
                    'scores': {'content': match.match_score},
                    'all_reasoning': set(match.reasoning)
                }
            else:
                all_matches[campaign_id]['scores']['content'] = match.match_score
                all_matches[campaign_id]['all_reasoning'].update(match.reasoning)
        
        # Process other strategy matches
        for strategy_name, matches in [
            ('collaborative', collaborative_matches),
            ('geographic', geographic_matches),
            ('demographic', demographic_matches)
        ]:
            for match in matches:
                campaign_id = match.campaign_id
                if campaign_id in all_matches:
                    all_matches[campaign_id]['scores'][strategy_name] = match.match_score
                    all_matches[campaign_id]['all_reasoning'].update(match.reasoning)
        
        # Calculate hybrid scores
        hybrid_matches = []
        for campaign_id, data in all_matches.items():
            scores = data['scores']
            
            # Calculate weighted average
            total_score = 0
            total_weight = 0
            for strategy, weight in strategy_weights.items():
                if strategy in scores:
                    total_score += scores[strategy] * weight
                    total_weight += weight
            
            if total_weight > 0:
                hybrid_score = total_score / total_weight
                
                # Boost for multiple strategy matches
                strategy_count = len(scores)
                if strategy_count >= 3:
                    hybrid_score += 0.1
                elif strategy_count >= 2:
                    hybrid_score += 0.05
                
                # Update the match with hybrid score
                original_match = data['match']
                original_match.match_score = min(1.0, hybrid_score)
                original_match.reasoning = list(data['all_reasoning'])
                original_match.confidence_level = min(1.0, hybrid_score * donor_profile.engagement_score)
                
                hybrid_matches.append(original_match)
        
        return hybrid_matches

    def _calculate_recommended_amount(self, donor_profile: DonorProfile, campaign: Dict) -> float:
        """Calculate recommended donation amount for donor"""
        
        # Base amount from donor history
        if donor_profile.giving_history:
            avg_donation = sum(d.get('amount', 0) for d in donor_profile.giving_history) / len(donor_profile.giving_history)
            base_amount = avg_donation
        else:
            # Default based on demographics
            age_group = donor_profile.demographics.get('age_group', '26-35')
            base_amount = self.demographic_factors['age'].get(age_group, {}).get('avg_donation', 50)
        
        # Adjust based on campaign category
        campaign_category = campaign.get('category', '').lower()
        category_data = self.medical_categories.get(campaign_category, {})
        category_avg = category_data.get('avg_donation', base_amount)
        
        # Weighted average
        recommended_amount = (base_amount * 0.7) + (category_avg * 0.3)
        
        # Adjust based on donor segment
        segment_multipliers = {
            DonorSegment.LARGE_DONOR: 2.0,
            DonorSegment.FREQUENT_GIVER: 1.2,
            DonorSegment.OCCASIONAL_GIVER: 1.0,
            DonorSegment.MICRO_DONOR: 0.5,
            DonorSegment.FIRST_TIME_GIVER: 0.7
        }
        
        multiplier = segment_multipliers.get(donor_profile.segment, 1.0)
        recommended_amount *= multiplier
        
        # Round to reasonable amounts
        if recommended_amount < 25:
            return round(recommended_amount / 5) * 5  # Round to nearest $5
        elif recommended_amount < 100:
            return round(recommended_amount / 10) * 10  # Round to nearest $10
        else:
            return round(recommended_amount / 25) * 25  # Round to nearest $25

    def _calculate_optimal_timing(self, donor_profile: DonorProfile) -> datetime:
        """Calculate optimal timing for donation request"""
        
        now = datetime.now()
        
        # Default to next business day at 10 AM
        optimal_time = now.replace(hour=10, minute=0, second=0, microsecond=0)
        
        # Adjust to next business day if weekend
        while optimal_time.weekday() >= 5:  # Saturday = 5, Sunday = 6
            optimal_time += timedelta(days=1)
        
        # Adjust based on donor preferences
        preferred_time = donor_profile.preferences.get('contact_time', 'morning')
        
        if preferred_time == 'afternoon':
            optimal_time = optimal_time.replace(hour=14)
        elif preferred_time == 'evening':
            optimal_time = optimal_time.replace(hour=19)
        
        # Consider donor engagement patterns
        if donor_profile.engagement_score > 0.8:
            # High engagement donors can be contacted sooner
            if now.hour < 20:  # Before 8 PM
                optimal_time = now + timedelta(hours=2)
        
        return optimal_time

    def _generate_personalized_message(self, donor_profile: DonorProfile, campaign: Dict, reasoning: List[str]) -> str:
        """Generate personalized message for campaign recommendation"""
        
        donor_name = donor_profile.demographics.get('first_name', 'Friend')
        campaign_title = campaign.get('title', 'Medical Campaign')
        campaign_category = campaign.get('category', 'medical treatment')
        
        # Base message templates
        templates = [
            f"Hi {donor_name}, we found a {campaign_category} campaign that matches your interests.",
            f"Dear {donor_name}, this {campaign_category} campaign could use your support.",
            f"Hello {donor_name}, here's a meaningful {campaign_category} opportunity for you."
        ]
        
        base_message = random.choice(templates)
        
        # Add personalized reasoning
        if reasoning:
            primary_reason = reasoning[0].lower()
            base_message += f" {primary_reason.capitalize()}."
        
        # Add call to action based on donor segment
        if donor_profile.segment == DonorSegment.FREQUENT_GIVER:
            base_message += " Your continued support makes a real difference."
        elif donor_profile.segment == DonorSegment.LARGE_DONOR:
            base_message += " Your generous contribution could significantly impact this campaign."
        elif donor_profile.segment == DonorSegment.FIRST_TIME_GIVER:
            base_message += " This could be a great way to start making a difference."
        
        return base_message


# Example usage and testing
def test_donor_matching_ai():
    """Test function for donor matching AI service"""
    ai = DonorMatchingAI()
    
    # Test donor profile creation
    test_donor_data = {
        'id': 'donor_123',
        'giving_history': [
            {'date': '2024-01-15', 'amount': 100, 'campaign_category': 'cancer'},
            {'date': '2024-02-20', 'amount': 150, 'campaign_category': 'pediatric'},
            {'date': '2024-03-10', 'amount': 75, 'campaign_category': 'cancer'}
        ],
        'demographics': {
            'age_group': '36-50',
            'income_level': 'medium',
            'gender': 'female',
            'first_name': 'Sarah'
        },
        'location': {
            'city': 'Austin',
            'state': 'Texas',
            'country': 'USA'
        },
        'preferences': {
            'contact_time': 'evening'
        },
        'platform_activity': {
            'monthly_logins': 8
        }
    }
    
    donor_profile = ai.create_donor_profile(test_donor_data)
    print(f"Donor Profile:")
    print(f"Segment: {donor_profile.segment}")
    print(f"Interests: {donor_profile.interests}")
    print(f"Engagement Score: {donor_profile.engagement_score:.2f}")
    print(f"Lifetime Value: ${donor_profile.lifetime_value}")
    
    # Test campaign matching
    test_campaigns = [
        {
            'id': 'camp_1',
            'title': 'Help Emma Fight Leukemia',
            'category': 'cancer',
            'description': 'Young girl needs chemotherapy treatment',
            'goal_amount': 75000,
            'location': {'city': 'Austin', 'state': 'Texas', 'country': 'USA'},
            'urgency': 'urgent',
            'predicted_success_rate': 0.8
        },
        {
            'id': 'camp_2',
            'title': 'Support Local Teacher Recovery',
            'category': 'emergency',
            'description': 'Teacher needs emergency surgery after accident',
            'goal_amount': 45000,
            'location': {'city': 'Houston', 'state': 'Texas', 'country': 'USA'},
            'urgency': 'immediate',
            'predicted_success_rate': 0.7
        }
    ]
    
    matching_result = ai.find_matching_campaigns(donor_profile, test_campaigns)
    
    print(f"\nMatching Results:")
    print(f"Strategy Used: {matching_result.strategy_used}")
    print(f"Total Matches: {matching_result.total_matches}")
    
    for match in matching_result.recommended_campaigns:
        print(f"\nCampaign: {match.campaign_id}")
        print(f"Match Score: {match.match_score:.2f}")
        print(f"Recommended Amount: ${match.recommended_amount:.0f}")
        print(f"Reasoning: {', '.join(match.reasoning)}")
        print(f"Message: {match.personalized_message}")


if __name__ == "__main__":
    test_donor_matching_ai()

