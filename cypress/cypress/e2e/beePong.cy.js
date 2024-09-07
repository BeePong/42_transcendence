////////////////////////////////////////////////////////////////////////////////
// Basic Navigation
////////////////////////////////////////////////////////////////////////////////
describe('### Basic Navigation and Content Tests', () => {
  it(' - should visit the `homepage` and contains `about`', () => {
    cy.visit('/');
    cy.task('log', '  - Visited homepage');
    cy.contains('ABOUT').should('be.visible');
    cy.screenshot('homepage-contains-about');
  });

  it(' - should visit the about `page` and contains `about BeePong`', () => {
    cy.visit('/about');
    cy.task('log', '  - Visited about page');
    cy.contains('about BeePong').should('be.visible');
    cy.screenshot('about-page-contains-about-BeePong');
  });

  it(' - should visit the `api` and contains `{"test": "This is a test JSON"}`', () => {
    cy.visit('/api');
    cy.task('log', '  - Visited API page');
    cy.contains('{"test": "This is a test JSON"}').should('be.visible');
    cy.screenshot('api-contains-test-JSON');
  });

  it(' - should visit the `game` and contains `game`', () => {
    cy.visit('/game');
    cy.task('log', '  - Visited game page');
    cy.contains('game').should('be.visible');
    cy.screenshot('game-page-contains-game');
  });

  it(' - should visit the `home` page and contains text about Hive Helsinki students', () => {
    cy.visit('/home');
    cy.task('log', '  - Visited home page');
    cy.contains(/created by 5 ultra[-\s]?talented Hive Helsinki students/i).should('be.visible');
    cy.screenshot('home-page-contains-credits');
  });

  it(' - should visit the `health` and contains `{"status": "healthy"}`', () => {
    cy.visit('/health');
    cy.task('log', '  - Visited health check page');
    cy.contains('{"status": "healthy"}').should('be.visible');
    cy.screenshot('health-check-contains-status-healthy');
  });

  it(' - should visit the `navbar` and contains `about`', () => {
    cy.visit('/navbar');
    cy.task('log', '  - Visited navbar');
    cy.contains('ABOUT').should('be.visible');
    cy.screenshot('navbar-contains-about');
  });
});

////////////////////////////////////////////////////////////////////////////////
// User Registration
////////////////////////////////////////////////////////////////////////////////
describe('### User Registration, Login, Logout, and Duplicate Registration Tests', () => {
  let username = 'b33Pong_cypress'
  let password = 'changeme.'

  function registerUser(username, password) {
    cy.visit('/accounts/register');
    cy.task('log', `  -- RegisterUser helper function: create a test user: ${username}`);
    cy.get('input[name="username"]').clear().type(username);
    cy.get('input[name="password1"]').type(password);
    cy.get('input[name="password2"]').type(password);
    cy.get('button[type="submit"]').click();
  }

  function loginUser(username, password) {
    cy.visit('/accounts/login');
    cy.get('input[name="username"]').type(username);
    cy.get('input[name="password"]').type(password);
    cy.get('button[type="submit"]').click();
  }

  it(' - should register twice with same username, second time should display error', () => {
    cy.task('log', `  - User registration: Should not allow registration of an already existing user`);
    registerUser(username, password)
    registerUser(username, password)
    cy.contains('A user with that username already exists').should('be.visible');
    cy.task('log', `  - User registration: Should not allow registration of an already existing user`);
    cy.screenshot('duplicate-registration-error');
  });

  it(' - should log in successfully', () => {
    cy.task('log', `  - User log in: user should log in`);
    cy.visit('/accounts/login');
    cy.get('input[name="username"]').type(username);
    cy.get('input[name="password"]').type(password);
    cy.get('button[type="submit"]').click();
    cy.contains(username).should('be.visible');
    cy.contains('LOG OUT').should('be.visible');
    cy.task('log', `  - User log in: user logged in`);
    cy.screenshot('successful-login_2');
  });

  it(`should log out ${username} properly`, () => {
    cy.task('log', `  - User loggin out: user should log in first`);
    loginUser(username, password);
    cy.contains('LOG OUT', { timeout: 10000 }).click();
    cy.contains('LOGIN').should('be.visible');
    cy.task('log', `  - User loggin out: user is logged out now`);
    cy.screenshot('logged-out');
  });

  after(() => {
    cy.task('log', `  !!! Could implement a cleaning task to delete the registered user: ${username} !!!`);
    // Clean up user in the database or backend if necessary
  });
});

////////////////////////////////////////////////////////////////////////////////
// Form Validation Tests
////////////////////////////////////////////////////////////////////////////////
describe('### Form Validation Tests', () => {
  it(' - should display error for empty login fields', () => {
    cy.visit('/accounts/login');
    cy.get('input[name="username"]').focus().blur();
    cy.get('input[name="username"]').then(($input) => {
      expect($input[0].validationMessage).to.eq('Please fill out this field.');
    });
    cy.task('log', '  - Form validation: empty login fields detected');
  });

  it(' - should display error for invalid username format', () => {
    cy.visit('/accounts/login');
    cy.get('input[name="username"]').type('invalidusername');
    cy.get('input[name="password"]').type('short');
    cy.get('button[type="submit"]').click();
    cy.screenshot('after-click-invalid-username-login');
    cy.contains('Please enter a').should('be.visible');
    cy.task('log', '  - Form validation: invalid username detected');
    cy.screenshot('validation-error-invalid-username');
  });

  it(' - should display error for password mismatch on registration', () => {
    cy.visit('/accounts/register');
    cy.get('input[name="username"]').type('b33P0ng');
    cy.get('input[name="password1"]').type('Password123');
    cy.get('input[name="password2"]').type('Password321');
    cy.get('button[type="submit"]').click();
    cy.screenshot('after-click-password-mismatch');
    cy.contains("The two password fields").should('be.visible');
    cy.task('log', '  - Form validation: password mismatch detected');
    cy.screenshot('validation-error-password-mismatch');
  });
});

////////////////////////////////////////////////////////////////////////////////
// Accounts Navigation and Form Tests
////////////////////////////////////////////////////////////////////////////////
describe('### Accounts Navigation and Form Tests', () => {
  it(' - should visit the `register` page and display the registration form', () => {
    cy.visit('/accounts/register');
    cy.task('log', '  - Visited register page');
    cy.contains('REGISTER').should('be.visible');
    cy.task('log', '  - Account navigation and validation: accessed register page successfully');
    cy.screenshot('register-page');
  });

  it(' - should visit the `login` page and display the login form', () => {
    cy.visit('/accounts/login');
    cy.task('log', '  - Visited login page');
    cy.contains('LOGIN TO PLAY TOURNAMENTS').should('be.visible');
    cy.task('log', '  - Account navigation and validation: accessed login page successfully');
    cy.screenshot('login-page');
  });

  it(' - should visit the `logout` page and redirect to home or login page', () => {
    cy.visit('/accounts/logout');
    cy.task('log', '  - Visited logout page');
    cy.contains('LOGIN').should('be.visible');
    cy.task('log', '  - Account navigation and validation: accessed logout page successfully');
    cy.screenshot('logout-page');
  });

  ///  //  it(' - should visit the `oauth_token` page and display oauth token content', () => {
  ///  //    cy.visit('/accounts/oauth_token');
  ///  //    cy.task('log', '  - Visited oauth token page');
  ///  //    cy.contains('Oauth Token').should('be.visible');
  ///  //    cy.screenshot('oauth-token-page');
  ///  //  });
  ///  //
  ///  //  it(' - should visit the `oauth_error` page and display oauth error message', () => {
  ///  //    cy.visit('/accounts/oauth_error');
  ///  //    cy.task('log', '  - Visited oauth error page');
  ///  //    cy.contains('42 Authorization Error').should('be.visible');
  ///  //    cy.screenshot('oauth-error-page');
  ///  //  });
});

////////////////////////////////////////////////////////////////////////////////
// Tournament Navigation and Interaction Tests
////////////////////////////////////////////////////////////////////////////////
describe('### Tournament Navigation and Interaction Tests', () => {
  let username = 'beePong_cypress'
  let password = 'changeme.'

  function registerUser(username, password) {
    cy.visit('/accounts/register');
    cy.task('log', `  -- RegisterUser helper function: create a test user: ${username}`);
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

  it(' - should visit the `tournament` page and display the tournaments', () => {
    cy.visit('/tournament/');
    cy.task('log', '  - Visited tournament page without being logged in, should redirect to login');
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
    cy.task('log', '  - Visited tournament page while being logged in, should be in tournament');
  });

  it(' - should visit the `create tournament` page and display the form', () => {
    cy.visit('/tournament/create/');
    cy.task('log', '  - Visited /tournament/create page without being logged in, should redirect to login');
    cy.url().should('include', '/accounts/login');
    registerUser(username, password);
    loginUser(username, password);
    cy.screenshot('tournament-page_user_loggedin');
    cy.visit('/tournament/create/');
    cy.task('log', '  - Visited /tournament/create page while being logged in, should be in tournament');
    cy.contains('NEW TOURNAMENT').should('be.visible');
    cy.url().should('include', '/tournament/create');
    cy.screenshot('create-tournament-page');
  });

  it(' - should visit a tournament page first unlogged, then logged in create a tournament', () => {
    const tournamentId = 1;
    cy.visit(`/tournament/${tournamentId}/lobby/`);
    cy.task('log', '  - Visited tournament lobby page');
    cy.screenshot('tournament-lobby-page');
    cy.contains('LOGIN').should('be.visible');
    registerUser(username, password);
    loginUser(username, password);
    cy.get('button[type="submit"]').click();


  });

  it(' - should navigate to the tournament page, create a tournament, and join it', () => {
    // Step 1: Visit the homepage
    registerUser(username, password);
    loginUser(username, password);
    cy.screenshot('tournament001-page_user_loggedin');
    cy.visit('/'); // Replace with your homepage URL
    cy.contains('TOURNAMENT').should('be.visible');
    cy.task('log', '  - Tournament creation: User created');

    // Step 2: Click on the TOURNAMENT button and check the URL
    cy.contains('TOURNAMENT').click();
    cy.url().should('include', '/tournament');

    // Step 3: Click on the NEW button to create a tournament
    cy.contains('NEW').click();
    cy.task('log', '  - Tournament creation: should visit tournament creation');
    cy.url().should('include', '/tournament/create');
    cy.screenshot('tournament002-create-tournament-page_1');

    // Step 4: Fill out the tournament creation form
    cy.task('log', '  - Tournament creation: should create tournament\'s title');
    cy.get('input[name="title"]').type('Test Tournament');
    cy.task('log', '  - Tournament creation: should create tournament\'s description');
    cy.get('input[name="description"]').type('This is a test tournament');
    cy.task('log', '  - Tournament creation: should create tournament\'s with 2 players');
    cy.get('input[type="radio"][value="2"]').first().click({ force: true });
    cy.get('button').contains('CREATE').click();
    cy.task('log', '  - Tournament creation: Tournament should be created');

    // Ensure tournament is created and redirected to the tournament page
    cy.url().should('include', '/tournament');
    cy.task('log', '  - Tournament creation: test tournament created');
    cy.screenshot('tournament003-tournament-created');

    // Step 5: Click Join on the newly created tournament
    cy.task('log', '  - Tournament creation: should join created tournament');
    cy.contains('JOIN').first().click();
    cy.screenshot('tournament004-created_JOINING');
    // cy.task('log', '  - Tournament creation: should join tournament with alias');
    // // Alias the input field containing the username, replace it with "t0t0", and submit
    // cy.get('input[name="username"]') // Select the username field
    //   .as('usernameField') // Alias it
    //   .clear() // Clear any pre-filled username
    //   .type('t0t0'); // Type the new username
    // cy.screenshot('tournament005-Alised as t0t0');

    // cy.task('log', '  - Tournament creation: alias should  be printed');
    // cy.get('@usernameField') // Use the alias to refer to the field
    //   .invoke('val') // Get the value to verify if "t0t0" is entered
    //   .should('equal', 't0t0'); // Assert that the username has been replaced with "t0t0"
    // // cy.get('input[name=username]').type("t0t0");
    // cy.get('button[type="submit"]').first().click();

    // // Verify if the player has joined the tournament and is in the lobby gaming
    // cy.screenshot('tournament005-created_JOINED');
    // cy.contains('game').should('be.visible');
    cy.screenshot('tournament006-gaming');
  });

});

////////////////////////////////////////////////////////////////////////////////
// Error Handling Tests
////////////////////////////////////////////////////////////////////////////////
describe('### Error Handling Tests', () => {
  it(' - should display 404 page for non-existent routes', () => {
    cy.visit('/non-existent-page', { failOnStatusCode: false });
    cy.task('log', '  - Visited non-existent page');
    cy.contains('404').should('be.visible');
    cy.screenshot('404-page-not-found-debug-false');
  });
});

