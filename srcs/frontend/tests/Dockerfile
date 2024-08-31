# Use an official Node.js image
FROM node:14

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json
COPY package.json package-lock.json setupJest.js ./

# Install dependencies (including Jest)
RUN npm install

# Copy only the frontend source code
COPY srcs/frontend/ .

# Specify the command to run tests with Jest
CMD ["npx", "jest"]