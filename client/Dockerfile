FROM node:18.15.0 AS build

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm install

COPY . .

RUN npm run build --prod

FROM nginx:alpine
COPY --from=build /usr/src/app/dist/rhetorical-framing-explorator /usr/share/nginx/html

# 80: the default port for serving static files with Nginx
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
