module.exports = {
  e2e: {
    // baseUrl: 'https://localhost',
    baseUrl:  'https://nginx',
    chromeWebSecurity: false,
		supportFile: false, // Disable support file if not used
		setupNodeEvents(on, config) {
      // implement node event listeners here
    },
    env: {
      "CYPRESS_TLS_REJECT_UNAUTHORIZED": "0"
    }
  }
};
