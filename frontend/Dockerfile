FROM node:22 AS build

ARG BACKEND_URL
ENV VITE_BACKEND_URL=$BACKEND_URL

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./

RUN npm install
COPY frontend ./
RUN npm run build

FROM node:22

WORKDIR /app
COPY --from=build /app .

CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "4173"]
