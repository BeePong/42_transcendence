# Use the official Cypress Docker image
FROM cypress/included:12.17.4

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json
COPY package.json package-lock.json .

# Install dependencies (including Cypress)
RUN npm install

# Copy the rest of your project files
COPY . .

# Run Cypress
CMD ["npx", "cypress", "run"]