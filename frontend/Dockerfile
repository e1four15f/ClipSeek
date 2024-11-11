FROM node:22 AS build

COPY config.yaml ./

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./

RUN npm install
COPY frontend ./
RUN npm run build

FROM node:22

WORKDIR /app
COPY --from=build /app .

CMD ["npm","run", "preview","--", "--host", "0.0.0.0"]
