
# Use official lightweight Node.js image
FROM node:22-slim

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install production dependencies only
RUN npm ci --omit=dev

# Copy application files
COPY --chown=node:node . .

# Run application as non-root user
USER node

# Application port
EXPOSE 3000

# Start application
CMD ["npm", "start"]
