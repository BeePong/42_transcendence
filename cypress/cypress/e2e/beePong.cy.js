describe('Basic Navigation and Content Tests', () => {
  it('should visit the `homepage` and contains `about`', () => {
    cy.visit('/');
    cy.task('log', 'Visited homepage');
    cy.contains('ABOUT').should('be.visible');
    cy.screenshot('homepage-contains-about');
  });

  it('should visit the about `page` and contains `about BeePong`', () => {
    cy.visit('/about');
    cy.task('log', 'Visited about page');
    cy.contains('about BeePong').should('be.visible');
    cy.screenshot('about-page-contains-about-BeePong');
  });

  it('should visit the `api` and contains `{"test": "This is a test JSON"}`', () => {
    cy.visit('/api');
    cy.task('log', 'Visited API page');
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
    cy.task('log', 'Visited registration page');
    cy.get('input[name="username"]').type('b33P0ng');
    cy.get('input[name="password1"]').type('Password123');
    cy.get('input[name="password2"]').type('Password321');
    cy.get('button[type="submit"]').click();
    cy.screenshot('after-click-password-mismatch');
    cy.contains("The two password fields").should('be.visible');
    cy.screenshot('validation-error-password-mismatch');
  });
});

// Accounts Navigation and Form Tests
describe('Accounts Navigation and Form Tests', () => {
  it('should visit the `register` page and display the registration form', () => {
    cy.visit('/accounts/register');
    cy.task('log', 'Visited register page');
    cy.contains('REGISTER').should('be.visible');
    cy.screenshot('register-page');
  });

  it('should visit the `login` page and display the login form', () => {
    cy.visit('/accounts/login');
    cy.task('log', 'Visited login page');
    cy.contains('LOGIN TO PLAY TOURNAMENTS').should('be.visible');
    cy.screenshot('login-page');
  });

  it('should visit the `logout` page and redirect to home or login page', () => {
    cy.visit('/accounts/logout');
    cy.task('log', 'Visited logout page');
    cy.contains('LOGIN').should('be.visible');
    cy.screenshot('logout-page');
  });

  it('should visit the `oauth_token` page and display oauth token content', () => {
    cy.visit('/accounts/oauth_token');
    cy.task('log', 'Visited oauth token page');
    cy.contains('Oauth Token').should('be.visible');
    cy.screenshot('oauth-token-page');
  });

  it('should visit the `oauth_error` page and display oauth error message', () => {
    cy.visit('/accounts/oauth_error');
    cy.task('log', 'Visited oauth error page');
    cy.contains('42 Authorization Error').should('be.visible');
    cy.screenshot('oauth-error-page');
  });
});

// Tournament Navigation and Interaction Tests
describe('Tournament Navigation and Interaction Tests', () => {
  it('should visit the `tournament` page and display the tournaments', () => {
    cy.visit('/tournament/');
    cy.task('log', 'Visited tournament page');
    cy.contains('Tournaments').should('be.visible');
    cy.screenshot('tournament-page');
  });

  it('should visit the `create tournament` page and display the form', () => {
    cy.visit('/tournament/create/');
    cy.task('log', 'Visited create tournament page');
    cy.contains('Create Tournament').should('be.visible');
    cy.screenshot('create-tournament-page');
  });

  it('should visit a tournament lobby page and display lobby content', () => {
    const tournamentId = 1; 
    cy.visit(`/tournament/${tournamentId}/lobby/`);
    cy.task('log', 'Visited tournament lobby page');
    cy.contains('Lobby').should('be.visible');
    cy.screenshot('tournament-lobby-page');
  });
});

// Error Handling Tests
describe('Error Handling Tests', () => {
  it('should display 404 page for non-existent routes (requires Django DEBUG=false to pass)', () => {
    cy.visit('/non-existent-page', { failOnStatusCode: false });
    cy.task('log', 'Visited non-existent page with Django DEBUG=false');
    cy.contains('404 not found').should('be.visible');
    cy.screenshot('404-page-not-found-debug-false');
  });

  it('should display 404 page for non-existent routes (requires Django DEBUG=true to pass)', () => {
    cy.visit('/non-existent-page', { failOnStatusCode: false });
    cy.task('log', 'Visited non-existent page with Django DEBUG=true');
    cy.contains('Page not found (404)').should('be.visible');
    cy.screenshot('404-page-not-found-debug-true');
  });
});

