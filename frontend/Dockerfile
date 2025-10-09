# Use official Node.js 18 Alpine image
FROM node:18-alpine

# Set working directory inside container
WORKDIR /app

# Copy package.json and package-lock.json first (for caching)
COPY package*.json ./

# Install all dependencies (including devDependencies)
RUN npm ci

# Copy project files into container
COPY . .

# Build Next.js app
RUN npm run build

# Remove dev dependencies to optimize image size
RUN npm prune --production

# Expose Next.js port
EXPOSE 3000

# Start Next.js app
CMD ["npm", "start"]
