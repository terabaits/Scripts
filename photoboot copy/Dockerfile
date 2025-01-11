# Use Node.js base image for ARM64
FROM --platform=linux/arm64/v8 node:18-slim

# Set the working directory to backend
WORKDIR /app/backend

# Install Python and build tools for native modules
RUN apt-get update && apt-get install -y python3 make g++ && apt-get clean

# Copy only package.json and lock file first
COPY backend/package*.json ./

# Install dependencies (with better-sqlite3 rebuilt for ARM64)
RUN npm install --build-from-source better-sqlite3

# Copy the rest of the application
COPY backend/ ./

# Expose port
EXPOSE 3003

# Start the application
CMD ["npm", "start"]
