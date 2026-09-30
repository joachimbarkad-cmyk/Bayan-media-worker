FROM node:22-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npx vite build && npm prune --omit=dev

FROM node:22-slim
WORKDIR /app
ENV NODE_ENV=production MURAJA_DATA=/data HOST=0.0.0.0 PORT=8787
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
COPY package.json ./
COPY server ./server
COPY web/lib ./web/lib
RUN mkdir -p /data && chown node:node /data
USER node
EXPOSE 8787
CMD ["node", "server/index.ts"]
