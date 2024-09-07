module.exports = {
  e2e: {
    baseUrl: 'https://nginx:443',
    setupNodeEvents(on, config) {
      // Implement the logging task
      on('task', {
        log(message) {
          console.log(message);
          return null;
        },
      });

      // If you have any other event listeners, they can go here as well
    },
  },
};

