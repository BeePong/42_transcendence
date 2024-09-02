describe('Sample Test', () => {
  it('test visits the `homepage` and contains `about`', () => {
    cy.visit('/');
    cy.contains('ABOUT');
  });

  it('test visits the about `page` and contains `about BeePong`', () => {
    cy.visit('/about');
    cy.contains('about BeePong');
  });

  it('test visits the `api` and contains `{"test": "This is a test JSON"}`', () => {
    cy.visit('/api');
    cy.contains('{"test": "This is a test JSON"}');
  });

  it('test visits the `game` and contains `game`', () => {
    cy.visit('/game');
    cy.contains('game');
  });

  it('test visits the `health` and contains `{"status": "healthy"}`', () => {
    cy.visit('/health');
    cy.contains('{"status": "healthy"}');
  });

  it('test visits the `home` page and contains `*created by 5 ultra talanted Hive Helsinki students. Tech stuff here ->`', () => {
    cy.visit('/home');
    cy.contains("*created by 5 ultra talanted Hive Helsinki students. Tech stuff here ->");
  });

  it('test visits the `navbar` and contains `about`', () => {
    cy.visit('/navbar');
    cy.contains('ABOUT');
  });
});
