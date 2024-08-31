# Project Evaluation Checklist

## Essential Project Requirements

- [ ] **Minimal Technical Requirements**
  - [x] Ensure the frontend is developed using pure vanilla JavaScript (unless overridden by a module).
  - [x] Make the website a Single-Page Application (SPA) with functional Back and Forward browser buttons.
  - [x] Ensure compatibility with the latest stable version of Google Chrome.
  - [ ] Prevent unhandled errors or warnings during navigation.
  - [x] Ensure the entire project can be launched with a single command using Docker (`docker-compose up --build`).
  - [x] If using Docker in clusters, ensure Docker runtime files are in `/goinfre` or `/sgoinfre`.
  - [x] Avoid "bind-mount volumes" with non-root UIDs in Docker containers.

- [x] **Game Requirements**
  - [x] [Note: Overridden by remote player module] Allow users to participate in a live Pong game against another player using the same keyboard.
  - [x] Implement a tournament system for multiple players, displaying the match order.
  - [x] Include a registration system where players input their alias names at the start of a tournament.
  - [x] Implement a matchmaking system for tournament organization.
  - [x] Ensure all players, including AI, follow identical rules (e.g., paddle speed).
  - [x] Capture the essence of the original Pong game (1972) in the design, adhering to frontend constraints.

- [x] **Security Concerns**
  - [x] Hash any passwords stored in the database.
  - [x] Protect the website against SQL injections and XSS attacks.
  - [x] Enable HTTPS connections for all backend features, using WSS instead of WS.
  - [x] Implement validation for all forms and user input.
  - [x] Store credentials, API keys, and environment variables in a `.env` file, ignored by Git.

## Major Modules

- [x] **Use a Framework as Backend (1.0)**
  - [x] Implement a specific web framework (Django) for backend development.
  
- [x] **User Management: Implementing Remote Authentication (1.0)**
  - [x] Integrate OAuth 2.0 authentication with 42 for secure user login.
  - [x] Manage duplicate usernames/emails with a justified approach.
  - [x] Implement secure login, authorization flows, and token exchange.

- [ ] **Gameplay and User Experience: Remote Players (1.0)**
  - [ ] Enable distant players to play the same Pong game from separate computers.
  - [ ] Handle network issues like disconnections and lags effectively to enhance user experience.

- [ ] **AI-Algo: Introduce an AI Opponent (1.0)**
  - [ ] Develop an AI opponent that simulates human behavior with strategic decision-making.
  - [ ] Ensure AI can only refresh its view of the game once per second.
  - [ ] If Game Customization Options module is used, AI must utilize power-ups.
  - [ ] Explain AI functionality during evaluation, ensuring it can occasionally win games.

- [ ] **Server-Side Pong: Replacing Basic Pong with Server-Side Pong and Implementing an API (1.0)**
  - [ ] Develop server-side logic for Pong game mechanics.
  - [ ] Create an API to interact with the game via CLI and web interface.
  - [ ] Ensure responsive gameplay and seamless integration with the web application.

- [X] **DevOps: Infrastructure Setup for Log Management (1.0)**
  - [x] Deploy Elasticsearch for efficient log storage and indexing.
  - [x] Configure Logstash to process and forward log data to Elasticsearch.
  - [X] Set up Kibana for log visualization, dashboards, and insights.
  - [X] Define data retention policies and implement security measures for log management.

## Minor Modules

- [x] **Use a Database for the Backend (0.5)**
  - [x] Implement PostgreSQL as the backend database.
  - [x] Ensure consistency and compatibility with other project components.

- [x] **Accessibility: Expanding Browser Compatibility (0.5)**
  - [x] Extend support to an additional web browser.
  - [x] Test and optimize the application to function correctly in the new browser.
  - [x] Address any compatibility issues and maintain a consistent user experience.
  
## Eval Sheet Focus

- [ ] **Preliminary Tests**
  - [ ] Ensure all credentials, API keys, and environment variables are in a `.env` file.
  - [ ] Ensure the docker-compose file is at the root of the repository.
  - [ ] Run the `docker-compose up --build` command to ensure everything builds and runs without errors.

- [ ] **Basic Checks**
  - [ ] Ensure the website is available.
  - [ ] Verify that the user can subscribe to the website.
  - [ ] Ensure registered users can log in.
  - [ ] Confirm that the website is a Single Page Application (SPA) with functional "Back" and "Forward" buttons.
  - [ ] Ensure the website can be browsed using the latest version of Chrome.

- [ ] **Security Checks**
  - [ ] Ensure the website is secured and TLS is implemented if necessary.
  - [ ] Verify that passwords are hashed in the database.
  - [ ] Ensure there is server-side validation/sanitization on all forms and user inputs.
  - [ ] Thoroughly test security measures to ensure they are properly implemented.

- [ ] **Gameplay Checks**
  - [ ] Ensure the game is playable and respects the original Pong game mechanics.
  - [ ] Provide intuitive controls or clear instructions.
  - [ ] Implement an end-game screen or ensure the game page exits when the game is over.

- [ ] **Lag & Disconnection Handling**
  - [ ] Ensure the game does not crash during lags or disconnections.
  - [ ] Implement handling for unexpected disconnections (e.g., pause, reconnect).
  - [ ] Allow lagging users to catch up with the match.

- [ ] **Modules Verification**
  - [ ] Verify that each major module is functioning correctly.
  - [ ] Ensure there are no errors in the implementation of the modules.
  - [ ] Confirm that the purpose of each module is understood and well explained.
  - [ ] Ensure each module is thoroughly demonstrated and explained during evaluation.

## Submission and Peer-Evaluation

- [ ] **Final Submission**
  - [ ] Ensure all work is committed to the Git repository.
  - [ ] Double-check file names and repository structure.
  - [ ] Make sure the project complies with all the requirements before submission.
  - [ ] Make sure only Kibana and Nginx have exposed ports to outside.
  - [ ] Make sure everything works on the school's computers.
