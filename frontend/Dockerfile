# Build stage
FROM node:18-alpine AS build-stage

WORKDIR /app

# Copy package files
COPY package*.json ./

# Remove stale lockfile to force resolution of updated vue-tsc & typescript versions
RUN rm -f package-lock.json

# Install dependencies
RUN npm install

# Copy project files
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine AS production-stage

# Copy built files from build stage
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
