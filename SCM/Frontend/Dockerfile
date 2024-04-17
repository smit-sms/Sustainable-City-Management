FROM node:20.9.0-alpine as builder

WORKDIR /app

COPY public/ /app/public

COPY src/ /app/src

COPY package.json .env /app/

COPY tailwind.config.js postcss.config.js /app/

RUN npm install --verbose

RUN npm run build

# Bundle static assets with nginx
FROM nginx:1.21.0-alpine as production
ENV NODE_ENV production
# Copy built assets from `builder` image
COPY --from=builder /app/build /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
