FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Vite usually runs on 5173 by default
EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]