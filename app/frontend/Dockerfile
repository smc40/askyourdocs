FROM node:14 as ayd-frontend

# Set the working directory in the container to /app
WORKDIR /app

# Copy package.json and yarn.lock into the container at /app
COPY package.json .

# Install project dependencies
RUN npm install

# Copy the rest of the frontend source code into the container at /app
COPY . .

# Expose the port the app runs on (if needed)
EXPOSE 3000

# Run the frontend application
RUN npm run build

COPY entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]
