
describe('Basic Navigation and Content Tests', () => {
  it('should visit the `homepage` and contains `about`', () => {
    cy.visit('/');
    cy.log('Visited homepage');
    cy.contains('ABOUT').should('be.visible');
    cy.screenshot('homepage-contains-about');
  });

  it('should visit the about `page` and contains `about BeePong`', () => {
    cy.visit('/about');
    cy.log('Visited about page');
    cy.contains('about BeePong').should('be.visible');
    cy.screenshot('about-page-contains-about-BeePong');
  });

  it('should visit the `api` and contains `{"test": "This is a test JSON"}`', () => {
    cy.visit('/api');
    cy.log('Visited API page');
    cy.contains('{"test": "This is a test JSON"}').should('be.visible');
    cy.screenshot('api-contains-test-JSON');
  });

  it('should visit the `game` and contains `game`', () => {
    cy.visit('/game');
    cy.log('Visited game page');
    cy.contains('game').should('be.visible');
    cy.screenshot('game-page-contains-game');
  });

  it('should visit the `health` and contains `{"status": "healthy"}`', () => {
    cy.visit('/health');
    cy.log('Visited health check page');
    cy.contains('{"status": "healthy"}').should('be.visible');
    cy.screenshot('health-check-contains-status-healthy');
  });

  it('should visit the `home` page and contains `*created by 5 ultra talanted Hive Helsinki students. Tech stuff here ->`', () => {
    cy.visit('/home');
    cy.log('Visited home page');
    cy.contains("*created by 5 ultra talanted Hive Helsinki students. Tech stuff here ->").should('be.visible');
    cy.screenshot('home-page-contains-credits');
  });

  it('should visit the `navbar` and contains `about`', () => {
    cy.visit('/navbar');
    cy.log('Visited navbar');
    cy.contains('ABOUT').should('be.visible');
    cy.screenshot('navbar-contains-about');
  });
});


describe('Form Validation Tests', () => {
  it('should display error for empty login fields', () => {
    cy.visit('/accounts/login');
    cy.log('Visited login page');
    // Focus on the username input field and then blur to trigger validation
    cy.get('input[name="username"]').focus().blur();

    // Check for the browser-generated validation message
    cy.get('input[name="username"]').then(($input) => {
      // Assert that the browser validation message is correct
      expect($input[0].validationMessage).to.eq('Please fill out this field.');
    });

    // Optionally, you can also check the presence of the error message using contains
    cy.get('input[name="username"]').invoke('prop', 'validationMessage').should('equal', 'Please fill out this field.');
  });

  it('should display error for invalid username format', () => {
    cy.visit('/accounts/login');
    cy.log('Visited login page');
    cy.get('input[name="username"]').should('be.visible').type('invalidusername');
    cy.get('input[name="password"]').should('be.visible').type('short');
    cy.get('button[type="submit"]').click();
    cy.screenshot('after-click-invalid-username-login');
    cy.contains('Please enter a').should('be.visible');
    cy.screenshot('validation-error-invalid-username');
  });

  it('should display error for password mismatch on registration', () => {
    cy.visit('/accounts/register');
    cy.log('Visited registration page');
    cy.get('input[name="username"]').should('be.visible').type('b33P0ng');
    cy.get('input[name="password1"]').should('be.visible').type('Password123');
    cy.get('input[name="password2"]').should('be.visible').type('Password321');
    cy.get('button[type="submit"]').click();
    cy.screenshot('after-click-password-mismatch');
    cy.contains("The two password fields").should('be.visible');
    cy.screenshot('validation-error-password-mismatch');
  });
});

describe('Error Handling Tests', () => {
  // Test for 404 page when Django debug mode is set to false
  it('should display 404 page for non-existent routes (requires Django DEBUG=false)', () => {
    cy.visit('/non-existent-page', { failOnStatusCode: false });
    cy.log('Visited non-existent page with Django DEBUG=false');
    cy.contains('404 not found').should('be.visible');
    cy.screenshot('404-page-not-found-debug-false');
  });

  // Test for 404 page when Django debug mode is set to true
  it('should display 404 page for non-existent routes (requires Django DEBUG=true)', () => {
    cy.visit('/non-existent-page', { failOnStatusCode: false });
    cy.log('Visited non-existent page with Django DEBUG=true');
    cy.contains('Page not found (404)').should('be.visible');
    cy.screenshot('404-page-not-found-debug-true');
  });

  it('should display 500 error message when server fails (requires Django debug=false)', () => {
    // Intercept the API call and force it to fail
    cy.intercept('GET', '/api/fail', {
      statusCode: 500,
      body: 'Internal Server Error',
    }).as('getServerFailure');
    // Visit the page that triggers the API call
    cy.visit('/trigger-error');
    // Wait for the intercepted request and assert that it fails
    cy.wait('@getServerFailure').then((interception) => {
      expect(interception.response.statusCode).to.equal(500);
    });
    // Verify the 500 error message is displayed on the page
    cy.contains('Internal Server Error').should('be.visible');
    // Take a screenshot of the error page
    cy.screenshot('500-error-message');
  });
});

