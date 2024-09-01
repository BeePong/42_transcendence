describe('Sample Test', () => {
  it('should visit the homepage and contains about', () => {
    cy.visit('/');
    cy.contains('ABOUT');
  });

  it('should visit the about page and contains about BeePong', () => {
    cy.visit('/about');
    cy.contains('about BeePong');
  });
});