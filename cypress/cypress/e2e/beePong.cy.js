describe('Sample Test', () => {
  it('should visit the homepage and check for a title', () => {
    // cy.visit('https://localhost'); // Replace with your application's URL
    cy.visit('/');
    cy.contains('ABOUT');
  });
});