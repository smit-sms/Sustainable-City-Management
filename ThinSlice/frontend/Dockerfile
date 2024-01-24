FROM node:20.9.0-alpine

WORKDIR /app

COPY public/ /app/public

COPY src/ /app/src

COPY package.json /app/

RUN npm install --verbose

CMD ["npm", "start"]
