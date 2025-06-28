/**
 * SaveLife.com End-to-End Test Suite
 * 
 * Comprehensive E2E tests covering complete user journeys including:
 * - Campaign creation with AI assistance
 * - Document verification workflows
 * - Donation processing
 * - Campaign discovery and browsing
 * - Administrative functions
 */

describe('SaveLife.com Platform E2E Tests', () => {
  beforeEach(() => {
    // Visit the homepage before each test
    cy.visit('http://localhost:5173');
    
    // Set up viewport for consistent testing
    cy.viewport(1280, 720);
    
    // Mock AI service responses for consistent testing
    cy.intercept('POST', '/api/ai/campaign/suggestions', {
      fixture: 'campaign-suggestions.json'
    }).as('getCampaignSuggestions');
    
    cy.intercept('POST', '/api/ai/verification/analyze-document', {
      fixture: 'document-analysis.json'
    }).as('analyzeDocument');
    
    cy.intercept('POST', '/api/ai/donor/matching', {
      fixture: 'donor-matching.json'
    }).as('getDonorMatching');
  });

  describe('Homepage and Navigation', () => {
    it('should display the homepage correctly', () => {
      // Verify main navigation
      cy.get('[data-testid="main-nav"]').should('be.visible');
      cy.get('[data-testid="logo"]').should('contain.text', 'SaveLife.com');
      
      // Verify hero section
      cy.get('[data-testid="hero-section"]').should('be.visible');
      cy.get('[data-testid="hero-title"]').should('contain.text', 'AI-Powered Medical Crowdfunding');
      cy.get('[data-testid="hero-subtitle"]').should('contain.text', 'helping people help each other');
      
      // Verify call-to-action buttons
      cy.get('[data-testid="start-campaign-btn"]').should('be.visible');
      cy.get('[data-testid="browse-campaigns-btn"]').should('be.visible');
    });

    it('should display platform statistics', () => {
      cy.get('[data-testid="stats-section"]').should('be.visible');
      cy.get('[data-testid="stat-raised"]').should('contain.text', '$2.5M+');
      cy.get('[data-testid="stat-campaigns"]').should('contain.text', '1,200+');
      cy.get('[data-testid="stat-verification"]').should('contain.text', '98%');
    });

    it('should display AI-powered features', () => {
      cy.get('[data-testid="features-section"]').should('be.visible');
      cy.get('[data-testid="feature-creation"]').should('contain.text', 'Smart Campaign Creation');
      cy.get('[data-testid="feature-verification"]').should('contain.text', 'Automated Verification');
      cy.get('[data-testid="feature-matching"]').should('contain.text', 'Intelligent Donor Matching');
      cy.get('[data-testid="feature-support"]').should('contain.text', '24/7 AI Support');
    });

    it('should display featured campaigns', () => {
      cy.get('[data-testid="featured-campaigns"]').should('be.visible');
      cy.get('[data-testid="campaign-card"]').should('have.length.at.least', 3);
      
      // Verify campaign card structure
      cy.get('[data-testid="campaign-card"]').first().within(() => {
        cy.get('[data-testid="campaign-title"]').should('be.visible');
        cy.get('[data-testid="campaign-progress"]').should('be.visible');
        cy.get('[data-testid="campaign-goal"]').should('be.visible');
        cy.get('[data-testid="donate-btn"]').should('be.visible');
      });
    });

    it('should navigate between sections smoothly', () => {
      // Test navigation to different sections
      cy.get('[data-testid="nav-how-it-works"]').click();
      cy.url().should('include', '#how-it-works');
      
      cy.get('[data-testid="nav-about"]').click();
      cy.url().should('include', '#about');
      
      cy.get('[data-testid="nav-contact"]').click();
      cy.url().should('include', '#contact');
    });
  });

  describe('Campaign Creation Journey', () => {
    it('should complete the full campaign creation process', () => {
      // Start campaign creation
      cy.get('[data-testid="start-campaign-btn"]').click();
      cy.url().should('include', '/create-campaign');
      
      // Step 1: Basic Information
      cy.get('[data-testid="campaign-form"]').should('be.visible');
      cy.get('[data-testid="patient-name"]').type('Sarah Johnson');
      cy.get('[data-testid="medical-condition"]').type('Stage II breast cancer requiring chemotherapy and surgery');
      cy.get('[data-testid="treatment-plan"]').type('6 months chemotherapy followed by mastectomy and reconstruction');
      cy.get('[data-testid="insurance-status"]').select('Limited coverage');
      
      // Get AI suggestions
      cy.get('[data-testid="get-suggestions-btn"]').click();
      cy.wait('@getCampaignSuggestions');
      
      // Verify AI suggestions appear
      cy.get('[data-testid="ai-suggestions"]').should('be.visible');
      cy.get('[data-testid="suggested-title"]').should('not.be.empty');
      cy.get('[data-testid="suggested-goal"]').should('not.be.empty');
      
      // Accept AI suggestions
      cy.get('[data-testid="accept-title-btn"]').click();
      cy.get('[data-testid="accept-goal-btn"]').click();
      
      // Continue to next step
      cy.get('[data-testid="next-step-btn"]').click();
      
      // Step 2: Campaign Story
      cy.get('[data-testid="story-section"]').should('be.visible');
      cy.get('[data-testid="campaign-story"]').type(
        'Sarah is a 34-year-old mother of two who was recently diagnosed with Stage II breast cancer. ' +
        'She needs help covering the costs of chemotherapy, surgery, and reconstruction that her insurance doesn\'t fully cover.'
      );
      
      // Get story optimization suggestions
      cy.get('[data-testid="optimize-story-btn"]').click();
      cy.get('[data-testid="story-suggestions"]').should('be.visible');
      
      // Continue to next step
      cy.get('[data-testid="next-step-btn"]').click();
      
      // Step 3: Document Upload
      cy.get('[data-testid="document-section"]').should('be.visible');
      
      // Upload medical records
      const medicalRecord = 'medical-record.pdf';
      cy.get('[data-testid="medical-record-upload"]').selectFile({
        contents: Cypress.Buffer.from('Medical record content'),
        fileName: medicalRecord,
        mimeType: 'application/pdf'
      });
      
      // Wait for document analysis
      cy.wait('@analyzeDocument');
      cy.get('[data-testid="verification-status"]').should('contain.text', 'Verified');
      
      // Upload insurance documents
      const insuranceDoc = 'insurance-document.pdf';
      cy.get('[data-testid="insurance-doc-upload"]').selectFile({
        contents: Cypress.Buffer.from('Insurance document content'),
        fileName: insuranceDoc,
        mimeType: 'application/pdf'
      });
      
      // Continue to review
      cy.get('[data-testid="next-step-btn"]').click();
      
      // Step 4: Review and Publish
      cy.get('[data-testid="review-section"]').should('be.visible');
      cy.get('[data-testid="review-title"]').should('contain.text', 'Sarah Johnson');
      cy.get('[data-testid="review-goal"]').should('not.be.empty');
      cy.get('[data-testid="review-story"]').should('not.be.empty');
      
      // Agree to terms
      cy.get('[data-testid="terms-checkbox"]').check();
      
      // Publish campaign
      cy.get('[data-testid="publish-btn"]').click();
      
      // Verify success
      cy.get('[data-testid="success-message"]').should('be.visible');
      cy.get('[data-testid="campaign-url"]').should('be.visible');
    });

    it('should handle AI assistance during campaign creation', () => {
      cy.get('[data-testid="start-campaign-btn"]').click();
      
      // Test real-time writing assistance
      cy.get('[data-testid="patient-name"]').type('John');
      cy.get('[data-testid="writing-help"]').should('be.visible');
      
      // Test title suggestions
      cy.get('[data-testid="medical-condition"]').type('heart surgery');
      cy.get('[data-testid="get-title-suggestions"]').click();
      cy.get('[data-testid="title-suggestions"]').should('be.visible');
      cy.get('[data-testid="title-option"]').first().click();
      
      // Test goal recommendations
      cy.get('[data-testid="get-goal-recommendation"]').click();
      cy.get('[data-testid="goal-explanation"]').should('be.visible');
      cy.get('[data-testid="recommended-amount"]').should('not.be.empty');
    });

    it('should validate form inputs and show appropriate errors', () => {
      cy.get('[data-testid="start-campaign-btn"]').click();
      
      // Try to proceed without required fields
      cy.get('[data-testid="next-step-btn"]').click();
      
      // Verify validation errors
      cy.get('[data-testid="name-error"]').should('be.visible');
      cy.get('[data-testid="condition-error"]').should('be.visible');
      
      // Test invalid goal amount
      cy.get('[data-testid="goal-amount"]').type('-100');
      cy.get('[data-testid="goal-error"]').should('contain.text', 'must be positive');
      
      // Test story length validation
      cy.get('[data-testid="campaign-story"]').type('Too short');
      cy.get('[data-testid="story-error"]').should('contain.text', 'minimum length');
    });
  });

  describe('Campaign Discovery and Browsing', () => {
    it('should browse and filter campaigns effectively', () => {
      cy.get('[data-testid="browse-campaigns-btn"]').click();
      cy.url().should('include', '/browse');
      
      // Verify campaign grid
      cy.get('[data-testid="campaign-grid"]').should('be.visible');
      cy.get('[data-testid="campaign-card"]').should('have.length.at.least', 1);
      
      // Test category filtering
      cy.get('[data-testid="category-filter"]').select('Cancer');
      cy.get('[data-testid="campaign-card"]').should('be.visible');
      
      // Test location filtering
      cy.get('[data-testid="location-filter"]').type('Texas');
      cy.get('[data-testid="apply-filters-btn"]').click();
      
      // Test search functionality
      cy.get('[data-testid="search-input"]').type('heart surgery');
      cy.get('[data-testid="search-btn"]').click();
      
      // Test sorting options
      cy.get('[data-testid="sort-select"]').select('Most Recent');
      cy.get('[data-testid="campaign-card"]').should('be.visible');
      
      // Test pagination
      cy.get('[data-testid="pagination"]').should('be.visible');
      cy.get('[data-testid="next-page"]').click();
    });

    it('should display campaign details correctly', () => {
      cy.get('[data-testid="browse-campaigns-btn"]').click();
      
      // Click on first campaign
      cy.get('[data-testid="campaign-card"]').first().click();
      
      // Verify campaign details page
      cy.get('[data-testid="campaign-header"]').should('be.visible');
      cy.get('[data-testid="campaign-title"]').should('not.be.empty');
      cy.get('[data-testid="campaign-story"]').should('not.be.empty');
      cy.get('[data-testid="progress-bar"]').should('be.visible');
      cy.get('[data-testid="goal-amount"]').should('not.be.empty');
      cy.get('[data-testid="raised-amount"]').should('not.be.empty');
      
      // Verify verification badges
      cy.get('[data-testid="verification-badge"]').should('be.visible');
      cy.get('[data-testid="trust-score"]').should('be.visible');
      
      // Verify donation section
      cy.get('[data-testid="donation-section"]').should('be.visible');
      cy.get('[data-testid="donate-btn"]').should('be.visible');
      
      // Verify updates section
      cy.get('[data-testid="updates-section"]').should('be.visible');
    });

    it('should show personalized recommendations', () => {
      // Simulate logged-in user
      cy.window().then((win) => {
        win.localStorage.setItem('user', JSON.stringify({
          id: 'user_123',
          preferences: { categories: ['cancer', 'surgery'] }
        }));
      });
      
      cy.get('[data-testid="browse-campaigns-btn"]').click();
      
      // Wait for donor matching
      cy.wait('@getDonorMatching');
      
      // Verify personalized section
      cy.get('[data-testid="recommended-for-you"]').should('be.visible');
      cy.get('[data-testid="recommendation-reason"]').should('be.visible');
    });
  });

  describe('Donation Process', () => {
    it('should complete a successful donation', () => {
      // Navigate to a campaign
      cy.get('[data-testid="browse-campaigns-btn"]').click();
      cy.get('[data-testid="campaign-card"]').first().click();
      
      // Start donation process
      cy.get('[data-testid="donate-btn"]').click();
      
      // Verify donation modal
      cy.get('[data-testid="donation-modal"]').should('be.visible');
      
      // Select donation amount
      cy.get('[data-testid="amount-50"]').click();
      cy.get('[data-testid="custom-amount"]').clear().type('100');
      
      // Add optional message
      cy.get('[data-testid="donor-message"]').type('Wishing you a speedy recovery!');
      
      // Choose to remain anonymous
      cy.get('[data-testid="anonymous-checkbox"]').check();
      
      // Continue to payment
      cy.get('[data-testid="continue-payment-btn"]').click();
      
      // Fill payment information (using test data)
      cy.get('[data-testid="card-number"]').type('4242424242424242');
      cy.get('[data-testid="expiry-date"]').type('12/25');
      cy.get('[data-testid="cvv"]').type('123');
      cy.get('[data-testid="cardholder-name"]').type('John Donor');
      
      // Fill billing address
      cy.get('[data-testid="billing-address"]').type('123 Main St');
      cy.get('[data-testid="billing-city"]').type('Austin');
      cy.get('[data-testid="billing-state"]').select('Texas');
      cy.get('[data-testid="billing-zip"]').type('78701');
      
      // Process payment
      cy.get('[data-testid="process-payment-btn"]').click();
      
      // Verify success
      cy.get('[data-testid="donation-success"]').should('be.visible');
      cy.get('[data-testid="receipt-number"]').should('not.be.empty');
      cy.get('[data-testid="tax-receipt"]').should('be.visible');
    });

    it('should handle payment errors gracefully', () => {
      cy.get('[data-testid="browse-campaigns-btn"]').click();
      cy.get('[data-testid="campaign-card"]').first().click();
      cy.get('[data-testid="donate-btn"]').click();
      
      // Use invalid card number
      cy.get('[data-testid="amount-25"]').click();
      cy.get('[data-testid="continue-payment-btn"]').click();
      cy.get('[data-testid="card-number"]').type('4000000000000002'); // Declined card
      cy.get('[data-testid="expiry-date"]').type('12/25');
      cy.get('[data-testid="cvv"]').type('123');
      cy.get('[data-testid="cardholder-name"]').type('John Donor');
      
      cy.get('[data-testid="process-payment-btn"]').click();
      
      // Verify error handling
      cy.get('[data-testid="payment-error"]').should('be.visible');
      cy.get('[data-testid="retry-payment-btn"]').should('be.visible');
    });

    it('should validate donation amounts and limits', () => {
      cy.get('[data-testid="browse-campaigns-btn"]').click();
      cy.get('[data-testid="campaign-card"]').first().click();
      cy.get('[data-testid="donate-btn"]').click();
      
      // Test minimum amount validation
      cy.get('[data-testid="custom-amount"]').type('0');
      cy.get('[data-testid="amount-error"]').should('contain.text', 'minimum');
      
      // Test maximum amount validation
      cy.get('[data-testid="custom-amount"]').clear().type('100000');
      cy.get('[data-testid="amount-error"]').should('contain.text', 'maximum');
      
      // Test valid amount
      cy.get('[data-testid="custom-amount"]').clear().type('50');
      cy.get('[data-testid="amount-error"]').should('not.exist');
    });
  });

  describe('User Authentication and Profiles', () => {
    it('should register a new user account', () => {
      cy.get('[data-testid="login-btn"]').click();
      cy.get('[data-testid="register-tab"]').click();
      
      // Fill registration form
      cy.get('[data-testid="first-name"]').type('John');
      cy.get('[data-testid="last-name"]').type('Doe');
      cy.get('[data-testid="email"]').type('john.doe@example.com');
      cy.get('[data-testid="password"]').type('SecurePassword123!');
      cy.get('[data-testid="confirm-password"]').type('SecurePassword123!');
      
      // Accept terms
      cy.get('[data-testid="terms-checkbox"]').check();
      
      // Submit registration
      cy.get('[data-testid="register-btn"]').click();
      
      // Verify email verification prompt
      cy.get('[data-testid="verify-email-message"]').should('be.visible');
    });

    it('should login with existing credentials', () => {
      cy.get('[data-testid="login-btn"]').click();
      
      // Fill login form
      cy.get('[data-testid="email"]').type('existing@example.com');
      cy.get('[data-testid="password"]').type('password123');
      
      // Submit login
      cy.get('[data-testid="login-submit-btn"]').click();
      
      // Verify successful login
      cy.get('[data-testid="user-menu"]').should('be.visible');
      cy.get('[data-testid="logout-btn"]').should('be.visible');
    });

    it('should manage user profile and preferences', () => {
      // Login first
      cy.get('[data-testid="login-btn"]').click();
      cy.get('[data-testid="email"]').type('user@example.com');
      cy.get('[data-testid="password"]').type('password123');
      cy.get('[data-testid="login-submit-btn"]').click();
      
      // Navigate to profile
      cy.get('[data-testid="user-menu"]').click();
      cy.get('[data-testid="profile-link"]').click();
      
      // Update profile information
      cy.get('[data-testid="profile-form"]').should('be.visible');
      cy.get('[data-testid="bio"]').type('Passionate about helping others in medical need');
      cy.get('[data-testid="location"]').type('Austin, TX');
      
      // Update notification preferences
      cy.get('[data-testid="email-notifications"]').check();
      cy.get('[data-testid="campaign-updates"]').check();
      
      // Save changes
      cy.get('[data-testid="save-profile-btn"]').click();
      cy.get('[data-testid="success-message"]').should('be.visible');
    });
  });

  describe('Accessibility and Responsive Design', () => {
    it('should be accessible with keyboard navigation', () => {
      // Test tab navigation
      cy.get('body').tab();
      cy.focused().should('have.attr', 'data-testid', 'skip-to-content');
      
      cy.tab();
      cy.focused().should('have.attr', 'data-testid', 'logo');
      
      cy.tab();
      cy.focused().should('have.attr', 'data-testid', 'nav-browse');
      
      // Test form navigation
      cy.get('[data-testid="start-campaign-btn"]').click();
      cy.get('[data-testid="patient-name"]').focus().type('Test Patient');
      cy.tab();
      cy.focused().should('have.attr', 'data-testid', 'medical-condition');
    });

    it('should work correctly on mobile devices', () => {
      cy.viewport('iphone-x');
      
      // Verify mobile navigation
      cy.get('[data-testid="mobile-menu-btn"]').should('be.visible');
      cy.get('[data-testid="mobile-menu-btn"]').click();
      cy.get('[data-testid="mobile-nav"]').should('be.visible');
      
      // Test mobile campaign creation
      cy.get('[data-testid="start-campaign-btn"]').click();
      cy.get('[data-testid="campaign-form"]').should('be.visible');
      
      // Verify touch-friendly elements
      cy.get('[data-testid="patient-name"]').should('have.css', 'min-height', '44px');
    });

    it('should support screen readers', () => {
      // Verify ARIA labels and roles
      cy.get('[data-testid="main-nav"]').should('have.attr', 'role', 'navigation');
      cy.get('[data-testid="campaign-grid"]').should('have.attr', 'role', 'grid');
      cy.get('[data-testid="donate-btn"]').should('have.attr', 'aria-label');
      
      // Verify heading hierarchy
      cy.get('h1').should('exist');
      cy.get('h2').should('exist');
      
      // Verify form labels
      cy.get('[data-testid="start-campaign-btn"]').click();
      cy.get('[data-testid="patient-name"]').should('have.attr', 'aria-label');
    });
  });

  describe('Performance and Error Handling', () => {
    it('should load pages within acceptable time limits', () => {
      const startTime = Date.now();
      
      cy.visit('http://localhost:5173');
      cy.get('[data-testid="hero-section"]').should('be.visible');
      
      const loadTime = Date.now() - startTime;
      expect(loadTime).to.be.lessThan(3000); // 3 second limit
    });

    it('should handle network errors gracefully', () => {
      // Simulate network failure
      cy.intercept('POST', '/api/ai/campaign/suggestions', {
        forceNetworkError: true
      }).as('networkError');
      
      cy.get('[data-testid="start-campaign-btn"]').click();
      cy.get('[data-testid="patient-name"]').type('Test Patient');
      cy.get('[data-testid="medical-condition"]').type('Test condition');
      cy.get('[data-testid="get-suggestions-btn"]').click();
      
      cy.wait('@networkError');
      
      // Verify error handling
      cy.get('[data-testid="error-message"]').should('be.visible');
      cy.get('[data-testid="retry-btn"]').should('be.visible');
    });

    it('should handle API errors appropriately', () => {
      // Simulate API error
      cy.intercept('POST', '/api/ai/campaign/suggestions', {
        statusCode: 500,
        body: { error: 'Internal server error' }
      }).as('apiError');
      
      cy.get('[data-testid="start-campaign-btn"]').click();
      cy.get('[data-testid="patient-name"]').type('Test Patient');
      cy.get('[data-testid="medical-condition"]').type('Test condition');
      cy.get('[data-testid="get-suggestions-btn"]').click();
      
      cy.wait('@apiError');
      
      // Verify error handling
      cy.get('[data-testid="error-message"]').should('contain.text', 'temporarily unavailable');
      cy.get('[data-testid="continue-without-ai"]').should('be.visible');
    });
  });

  describe('Security and Privacy', () => {
    it('should protect sensitive information', () => {
      // Verify no sensitive data in localStorage
      cy.window().then((win) => {
        const storage = win.localStorage;
        Object.keys(storage).forEach(key => {
          const value = storage.getItem(key);
          expect(value).to.not.contain('password');
          expect(value).to.not.contain('ssn');
          expect(value).to.not.contain('credit');
        });
      });
      
      // Verify secure form handling
      cy.get('[data-testid="start-campaign-btn"]').click();
      cy.get('[data-testid="campaign-form"]').should('have.attr', 'autocomplete', 'off');
    });

    it('should implement proper session management', () => {
      // Login
      cy.get('[data-testid="login-btn"]').click();
      cy.get('[data-testid="email"]').type('user@example.com');
      cy.get('[data-testid="password"]').type('password123');
      cy.get('[data-testid="login-submit-btn"]').click();
      
      // Verify session timeout handling
      cy.wait(30000); // Wait for session timeout
      cy.get('[data-testid="protected-action"]').click();
      cy.get('[data-testid="login-required"]').should('be.visible');
    });
  });
});

// Custom commands for reusable test actions
Cypress.Commands.add('loginUser', (email, password) => {
  cy.get('[data-testid="login-btn"]').click();
  cy.get('[data-testid="email"]').type(email);
  cy.get('[data-testid="password"]').type(password);
  cy.get('[data-testid="login-submit-btn"]').click();
});

Cypress.Commands.add('createCampaign', (campaignData) => {
  cy.get('[data-testid="start-campaign-btn"]').click();
  cy.get('[data-testid="patient-name"]').type(campaignData.name);
  cy.get('[data-testid="medical-condition"]').type(campaignData.condition);
  cy.get('[data-testid="treatment-plan"]').type(campaignData.treatment);
  cy.get('[data-testid="next-step-btn"]').click();
});

Cypress.Commands.add('makeDonation', (amount) => {
  cy.get('[data-testid="donate-btn"]').click();
  cy.get('[data-testid="custom-amount"]').type(amount.toString());
  cy.get('[data-testid="continue-payment-btn"]').click();
  // Add payment processing steps here
});

