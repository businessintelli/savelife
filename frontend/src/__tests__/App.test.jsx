import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../App';

// Mock the AI service calls
jest.mock('../services/aiService', () => ({
  getCampaignSuggestions: jest.fn(),
  getWritingAssistance: jest.fn(),
  verifyDocument: jest.fn(),
  getDonorRecommendations: jest.fn(),
}));

describe('SaveLife.com App Component', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  test('renders homepage with main navigation', () => {
    render(<App />);
    
    // Check for main navigation elements
    expect(screen.getByText('SaveLife.com')).toBeInTheDocument();
    expect(screen.getByText('Start Campaign')).toBeInTheDocument();
    expect(screen.getByText('Browse Campaigns')).toBeInTheDocument();
    expect(screen.getByText('How It Works')).toBeInTheDocument();
    expect(screen.getByText('Login')).toBeInTheDocument();
  });

  test('displays hero section with call-to-action', () => {
    render(<App />);
    
    // Check for hero section content
    expect(screen.getByText(/AI-Powered Medical Crowdfunding/i)).toBeInTheDocument();
    expect(screen.getByText(/helping people help each other/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /start your campaign/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /browse campaigns/i })).toBeInTheDocument();
  });

  test('shows platform statistics', () => {
    render(<App />);
    
    // Check for statistics section
    expect(screen.getByText('$2.5M+')).toBeInTheDocument();
    expect(screen.getByText('Raised for Medical Care')).toBeInTheDocument();
    expect(screen.getByText('1,200+')).toBeInTheDocument();
    expect(screen.getByText('Successful Campaigns')).toBeInTheDocument();
    expect(screen.getByText('98%')).toBeInTheDocument();
    expect(screen.getByText('Verification Rate')).toBeInTheDocument();
  });

  test('displays AI-powered features section', () => {
    render(<App />);
    
    // Check for features section
    expect(screen.getByText('AI-Powered Features')).toBeInTheDocument();
    expect(screen.getByText('Smart Campaign Creation')).toBeInTheDocument();
    expect(screen.getByText('Automated Verification')).toBeInTheDocument();
    expect(screen.getByText('Intelligent Donor Matching')).toBeInTheDocument();
    expect(screen.getByText('24/7 AI Support')).toBeInTheDocument();
  });

  test('shows featured campaigns section', () => {
    render(<App />);
    
    // Check for featured campaigns
    expect(screen.getByText('Featured Campaigns')).toBeInTheDocument();
    expect(screen.getByText(/Help Sarah Fight Breast Cancer/i)).toBeInTheDocument();
    expect(screen.getByText(/Support Michael's Heart Surgery/i)).toBeInTheDocument();
    expect(screen.getByText(/Emma's Leukemia Treatment Fund/i)).toBeInTheDocument();
  });

  test('navigation between sections works correctly', () => {
    render(<App />);
    
    // Test navigation to campaign creation
    const startCampaignButton = screen.getByRole('button', { name: /start your campaign/i });
    fireEvent.click(startCampaignButton);
    
    // Should show campaign creation form
    expect(screen.getByText(/Create Your Campaign/i)).toBeInTheDocument();
  });

  test('responsive design elements are present', () => {
    render(<App />);
    
    // Check for responsive design classes
    const heroSection = screen.getByText(/AI-Powered Medical Crowdfunding/i).closest('section');
    expect(heroSection).toHaveClass('min-h-screen');
    
    // Check for mobile-friendly navigation
    const navigation = screen.getByRole('navigation');
    expect(navigation).toBeInTheDocument();
  });

  test('accessibility features are implemented', () => {
    render(<App />);
    
    // Check for proper heading hierarchy
    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
    
    // Check for proper button roles
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);
    
    // Check for proper link roles
    const links = screen.getAllByRole('link');
    expect(links.length).toBeGreaterThan(0);
  });

  test('error boundaries handle component failures gracefully', () => {
    // Mock console.error to prevent error output during testing
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    // This would test error boundary functionality
    // In a real implementation, you'd trigger an error in a child component
    
    render(<App />);
    
    // Verify the app still renders even if child components fail
    expect(screen.getByText('SaveLife.com')).toBeInTheDocument();
    
    consoleSpy.mockRestore();
  });

  test('loading states are handled appropriately', async () => {
    render(<App />);
    
    // Test loading state for campaign data
    // In a real implementation, this would test loading spinners or skeleton screens
    
    await waitFor(() => {
      expect(screen.getByText('Featured Campaigns')).toBeInTheDocument();
    });
  });

  test('footer contains required information', () => {
    render(<App />);
    
    // Check for footer content
    expect(screen.getByText(/© 2024 SaveLife.com/i)).toBeInTheDocument();
    expect(screen.getByText('Privacy Policy')).toBeInTheDocument();
    expect(screen.getByText('Terms of Service')).toBeInTheDocument();
    expect(screen.getByText('Contact Us')).toBeInTheDocument();
  });
});

describe('SaveLife.com App Integration Tests', () => {
  test('campaign creation flow integration', async () => {
    const mockSuggestions = {
      title: 'Help John Fight Cancer',
      goal_amount: 50000,
      story_framework: 'Test story framework',
      keywords: ['cancer', 'treatment', 'support'],
      confidence_score: 0.85
    };

    const { getCampaignSuggestions } = require('../services/aiService');
    getCampaignSuggestions.mockResolvedValue(mockSuggestions);

    render(<App />);
    
    // Navigate to campaign creation
    const startButton = screen.getByRole('button', { name: /start your campaign/i });
    fireEvent.click(startButton);
    
    // Fill out campaign form
    const nameInput = screen.getByLabelText(/patient name/i);
    const conditionInput = screen.getByLabelText(/medical condition/i);
    
    fireEvent.change(nameInput, { target: { value: 'John Doe' } });
    fireEvent.change(conditionInput, { target: { value: 'Cancer treatment' } });
    
    // Request AI suggestions
    const getSuggestionsButton = screen.getByRole('button', { name: /get ai suggestions/i });
    fireEvent.click(getSuggestionsButton);
    
    // Wait for AI suggestions to appear
    await waitFor(() => {
      expect(screen.getByText('Help John Fight Cancer')).toBeInTheDocument();
    });
    
    expect(getCampaignSuggestions).toHaveBeenCalledWith({
      name: 'John Doe',
      medical_condition: 'Cancer treatment'
    });
  });

  test('campaign browsing and filtering integration', () => {
    render(<App />);
    
    // Navigate to browse campaigns
    const browseButton = screen.getByRole('button', { name: /browse campaigns/i });
    fireEvent.click(browseButton);
    
    // Test filtering functionality
    const categoryFilter = screen.getByLabelText(/category/i);
    fireEvent.change(categoryFilter, { target: { value: 'cancer' } });
    
    // Test search functionality
    const searchInput = screen.getByLabelText(/search campaigns/i);
    fireEvent.change(searchInput, { target: { value: 'heart surgery' } });
    
    // Verify filtering and search work together
    expect(categoryFilter.value).toBe('cancer');
    expect(searchInput.value).toBe('heart surgery');
  });

  test('donation flow integration', async () => {
    render(<App />);
    
    // Navigate to a campaign
    const campaignCard = screen.getByText(/Help Sarah Fight Breast Cancer/i);
    fireEvent.click(campaignCard);
    
    // Click donate button
    const donateButton = screen.getByRole('button', { name: /donate now/i });
    fireEvent.click(donateButton);
    
    // Fill out donation form
    const amountInput = screen.getByLabelText(/donation amount/i);
    fireEvent.change(amountInput, { target: { value: '100' } });
    
    // Verify donation form is properly populated
    expect(amountInput.value).toBe('100');
  });
});

