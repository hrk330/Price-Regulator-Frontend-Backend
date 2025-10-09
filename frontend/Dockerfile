# Use lightweight Node 18 Alpine image
FROM node:18-alpine

# Create working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev)
RUN npm ci

# Copy the source code
COPY . .

# Build Next.js app
RUN npm run build

# Remove dev dependencies to optimize image size
RUN npm prune --production

# Expose the app port
EXPOSE 3000

# Start Next.js app
CMD ["npm", "start"]
