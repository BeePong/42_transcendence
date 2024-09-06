//////////////////////////////////////////////////////////////////////////////////
//// Basic Navigation
//////////////////////////////////////////////////////////////////////////////////
//describe('Basic Navigation and Content Tests', () => {
//  it('should visit the `homepage` and contains `about`', () => {
//    cy.visit('/');
//    cy.task('log', 'Visited homepage');
//    cy.contains('ABOUT').should('be.visible');
//    cy.screenshot('homepage-contains-about');
//  });
//
//  it('should visit the about `page` and contains `about BeePong`', () => {
//    cy.visit('/about');
//    cy.task('log', 'Visited about page');
//    cy.contains('about BeePong').should('be.visible');
//    cy.screenshot('about-page-contains-about-BeePong');
//  });
//
//  it('should visit the `api` and contains `{"test": "This is a test JSON"}`', () => {
//    cy.visit('/api');
//    cy.task('log', 'Visited API page');
//    cy.contains('{"test": "This is a test JSON"}').should('be.visible');
//    cy.screenshot('api-contains-test-JSON');
//  });
//
//  it('should visit the `game` and contains `game`', () => {
//    cy.visit('/game');
//    cy.task('log', 'Visited game page');
//    cy.contains('game').should('be.visible');
//    cy.screenshot('game-page-contains-game');
//  });
//
//  it('should visit the `home` page and contains text about Hive Helsinki students', () => {
//    cy.visit('/home');
//    cy.task('log', 'Visited home page');
//    // Use regex to make the assertion more flexible
//    cy.contains(/created by 5 ultra[-\s]?talented Hive Helsinki students/i).should('be.visible');
//    cy.screenshot('home-page-contains-credits');
//  });
//
//  it('should visit the `health` and contains `{"status": "healthy"}`', () => {
//    cy.visit('/health');
//    cy.task('log', 'Visited health check page');
//    cy.contains('{"status": "healthy"}').should('be.visible');
//    cy.screenshot('health-check-contains-status-healthy');
//  });
//
//  it('should visit the `navbar` and contains `about`', () => {
//    cy.visit('/navbar');
//    cy.task('log', 'Visited navbar');
//    cy.contains('ABOUT').should('be.visible');
//    cy.screenshot('navbar-contains-about');
//  });
//});
//
//////////////////////////////////////////////////////////////////////////////////
//// User Registration
//////////////////////////////////////////////////////////////////////////////////
//describe('User Registration, Login, Logout, and Duplicate Registration Tests', () => {
//  let username = 'beePong_cypress'
//  let password = 'changeme.'
//
//  function registerUser(username, password) {
//    cy.visit('/accounts/register');
//    cy.task('log', `User registration: create a test user: ${username}`);
//    cy.get('input[name="username"]').clear().type(username);
//    cy.get('input[name="password1"]').type(password);
//    cy.get('input[name="password2"]').type(password);
//    cy.get('button[type="submit"]').click();
//    cy.screenshot(`registration_${username}`);
//  }
//
//  // Function to log in a user
//  function loginUser(username, password) {
//    cy.visit('/accounts/login');
//    cy.get('input[name="username"]').type(username);
//    cy.get('input[name="password"]').type(password);
//    cy.get('button[type="submit"]').click();
//    cy.screenshot(`login_${username}`);
//  }
//
//  it('should display error when trying to register with the same username', () => {
//    registerUser(username, password)
//    cy.contains('A user with that username already exists').should('be.visible');
//    cy.screenshot('duplicate-registration-error');
//  });
//
//  it('should log in successfully', () => {
//    cy.visit('/accounts/login');
//    cy.get('input[name="username"]').type(username);
//    cy.get('input[name="password"]').type('changeme.');
//    cy.get('button[type="submit"]').click();
//    cy.contains(username).should('be.visible');
//    cy.screenshot('successful-login_2');
//  });
//
//  it(`should log out ${username}`, () => {
//    registerUser(username, password);
//    loginUser(username, password);
//    cy.contains('LOG OUT', { timeout: 10000 }).click();
//    cy.screenshot('logged-out');
//  });
//
//  after(() => {
//    cy.task('log', `Cleaning up the registered user: ${username}`);
//    // Clean up user in the database or backend if necessary
//  });
//});
//
//////////////////////////////////////////////////////////////////////////////////
//// Form Validation Tests
//////////////////////////////////////////////////////////////////////////////////
//describe('Form Validation Tests', () => {
//  it('should display error for empty login fields', () => {
//    cy.visit('/accounts/login');
//    cy.task('log', 'Visited login page');
//    cy.get('input[name="username"]').focus().blur();
//    cy.get('input[name="username"]').then(($input) => {
//      expect($input[0].validationMessage).to.eq('Please fill out this field.');
//    });
//  });
//
//  it('should display error for invalid username format', () => {
//    cy.visit('/accounts/login');
//    cy.task('log', 'Visited login page');
//    cy.get('input[name="username"]').type('invalidusername');
//    cy.get('input[name="password"]').type('short');
//    cy.get('button[type="submit"]').click();
//    cy.screenshot('after-click-invalid-username-login');
//    cy.contains('Please enter a').should('be.visible');
//    cy.screenshot('validation-error-invalid-username');
//  });
//
//  it('should display error for password mismatch on registration', () => {
//    cy.visit('/accounts/register');
//    cy.task('log', 'Visited registration page');
//    cy.get('input[name="username"]').type('b33P0ng');
//    cy.get('input[name="password1"]').type('Password123');
//    cy.get('input[name="password2"]').type('Password321');
//    cy.get('button[type="submit"]').click();
//    cy.screenshot('after-click-password-mismatch');
//    cy.contains("The two password fields").should('be.visible');
//    cy.screenshot('validation-error-password-mismatch');
//  });
//});
//
//////////////////////////////////////////////////////////////////////////////////
//// Accounts Navigation and Form Tests
//////////////////////////////////////////////////////////////////////////////////
//describe('Accounts Navigation and Form Tests', () => {
//  it('should visit the `register` page and display the registration form', () => {
//    cy.visit('/accounts/register');
//    cy.task('log', 'Visited register page');
//    cy.contains('REGISTER').should('be.visible');
//    cy.screenshot('register-page');
//  });
//
//  it('should visit the `login` page and display the login form', () => {
//    cy.visit('/accounts/login');
//    cy.task('log', 'Visited login page');
//    cy.contains('LOGIN TO PLAY TOURNAMENTS').should('be.visible');
//    cy.screenshot('login-page');
//  });
//
//  it('should visit the `logout` page and redirect to home or login page', () => {
//    cy.visit('/accounts/logout');
//    cy.task('log', 'Visited logout page');
//    cy.contains('LOGIN').should('be.visible');
//    cy.screenshot('logout-page');
//  });
//
/////  //  it('should visit the `oauth_token` page and display oauth token content', () => {
/////  //    cy.visit('/accounts/oauth_token');
/////  //    cy.task('log', 'Visited oauth token page');
/////  //    cy.contains('Oauth Token').should('be.visible');
/////  //    cy.screenshot('oauth-token-page');
/////  //  });
/////  //
/////  //  it('should visit the `oauth_error` page and display oauth error message', () => {
/////  //    cy.visit('/accounts/oauth_error');
/////  //    cy.task('log', 'Visited oauth error page');
/////  //    cy.contains('42 Authorization Error').should('be.visible');
/////  //    cy.screenshot('oauth-error-page');
/////  //  });
//});
//
////////////////////////////////////////////////////////////////////////////////
// Tournament Navigation and Interaction Tests
////////////////////////////////////////////////////////////////////////////////
describe('Tournament Navigation and Interaction Tests', () => {
  let username = 'beePong_cypress'
  let password = 'changeme.'

  function registerUser(username, password) {
    cy.visit('/accounts/register');
    cy.task('log', `User registration: create a test user: ${username}`);
    cy.get('input[name="username"]').clear().type(username);
    cy.get('input[name="password1"]').type(password);
    cy.get('input[name="password2"]').type(password);
    cy.get('button[type="submit"]').click();
  }

  // Function to log in a user
  function loginUser(username, password) {
    cy.visit('/accounts/login');
    cy.get('input[name="username"]').type(username);
    cy.get('input[name="password"]').type(password);
    cy.get('button[type="submit"]').click();
  }

  it('should visit the `tournament` page and display the tournaments', () => {
    cy.visit('/tournament/');
    cy.task('log', 'Visited tournament page without being logged in, should redirect to login');
    cy.contains('LOGIN TO PLAY TOURNAMENTS').should('be.visible');
    cy.url().should('include', '/accounts/login');
    cy.screenshot('tournament-page_redir2login');
    registerUser(username, password);
    loginUser(username, password);
    cy.screenshot('tournament-page_user_loggedin');
    cy.visit('/tournament/');
    cy.contains('TOURNAMENTS').should('be.visible');
    cy.screenshot('tournament-page_tournament_url_visible');
    cy.url().should('include', '/tournament');
    cy.screenshot('tournament-page_OK');
    cy.task('log', 'Visited tournament page while being logged in, should be in tournament');
  });

  it('should visit the `create tournament` page and display the form', () => {
    cy.visit('/tournament/create/');
    cy.task('log', 'Visited /tournament/create page without being logged in, should redirect to login');
    cy.url().should('include', '/accounts/login');
    registerUser(username, password);
    loginUser(username, password);
    cy.screenshot('tournament-page_user_loggedin');
    cy.visit('/tournament/create/');
    cy.task('log', 'Visited /tournament/create page while being logged in, should be in tournament');
    cy.contains('NEW TOURNAMENT').should('be.visible');
    cy.url().should('include', '/tournament/create');
    cy.screenshot('create-tournament-page');
  });

  it('should visit a tournament page first unlogged, then logged in create a tournament', () => {
    const tournamentId = 1;
    cy.visit(`/tournament/${tournamentId}/lobby/`);
    cy.task('log', 'Visited tournament lobby page');
    cy.screenshot('tournament-lobby-page');
    cy.contains('LOGIN').should('be.visible');
    registerUser(username, password);
    loginUser(username, password);
    cy.get('button[type="submit"]').click();


  });

  it('should navigate to the tournament page, create a tournament, and join it', () => {
    // Step 1: Visit the homepage
    registerUser(username, password);
    loginUser(username, password);
    cy.screenshot('tournament001-page_user_loggedin');
    cy.visit('/'); // Replace with your homepage URL
    cy.contains('TOURNAMENT').should('be.visible');
    cy.task('log', 'Tournament creation: User created');

    // Step 2: Click on the TOURNAMENT button and check the URL
    cy.contains('TOURNAMENT').click();
    cy.url().should('include', '/tournament');

    // Step 3: Click on the NEW button to create a tournament
    cy.contains('NEW').click();
    cy.task('log', 'Tournament creation: should visit tournament creation');
    cy.url().should('include', '/tournament/create');
    cy.screenshot('tournament002-create-tournament-page_1');

    // Step 4: Fill out the tournament creation form
    cy.task('log', 'Tournament creation: should create tournament_1');
    cy.get('input[name="title"]').type('Test Tournament');
    cy.screenshot('tournament002-create-tournament-page_2');
    cy.task('log', 'Tournament creation: should create tournament_2');
    cy.get('input[name="description"]').type('This is a test tournament');
    cy.screenshot('tournament002-create-tournament-page_3');
    cy.task('log', 'Tournament creation: should create tournament_3');
    cy.get('input[type="radio"][value="2"]').first().click({ force: true }); 
    cy.screenshot('tournament002-create-tournament-page_4');
    cy.task('log', 'Tournament creation: should create tournament_4');
    cy.get('button').contains('CREATE').click();

    cy.task('log', 'Tournament creation: should create tournament_5');
    cy.screenshot('tournament002-create-tournament-page_5');

    // Ensure tournament is created and redirected to the tournament page
    cy.url().should('include', '/tournament');
    cy.task('log', 'Tournament creation: test tournament created');
    cy.screenshot('tournament003-tournament-created');

    // Step 5: Click Join on the newly created tournament
    cy.task('log', 'Tournament creation: join created tournament');
    cy.contains('JOIN').first().click();
    cy.screenshot('tournament004-created_JOINING');
//    cy.get('input[name="alias"]').type(username);
    cy.get('button[type="submit"]').first().click();

    // Verify if the player has joined the tournament and is in the lobby gaming
    cy.screenshot('tournament005-created_JOINED');
    cy.contains('game').should('be.visible');
    cy.screenshot('tournament006-gaming');
  });

});

//////////////////////////////////////////////////////////////////////////////////
//// Error Handling Tests
//////////////////////////////////////////////////////////////////////////////////
//describe('Error Handling Tests', () => {
//  it('should display 404 page for non-existent routes (requires Django DEBUG=false to pass)', () => {
//    cy.visit('/non-existent-page', { failOnStatusCode: false });
//    cy.task('log', 'Visited non-existent page with Django DEBUG=false');
//    cy.contains('404 not found').should('be.visible');
//    cy.screenshot('404-page-not-found-debug-false');
//  });
//
//  it('should display 404 page for non-existent routes (requires Django DEBUG=true to pass)', () => {
//    cy.visit('/non-existent-page', { failOnStatusCode: false });
//    cy.task('log', 'Visited non-existent page with Django DEBUG=true');
//    cy.contains('Page not found (404)').should('be.visible');
//    cy.screenshot('404-page-not-found-debug-true');
//  });
//});
//