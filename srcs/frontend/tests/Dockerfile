# Use an official Node.js image
FROM node:14

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json
COPY package.json package-lock.json .

# Install dependencies (including Jest)
RUN npm install

# Copy the rest of frontend project files to /app
COPY . .

# Specify the command to run tests with Jest
CMD ["npx", "jest"]