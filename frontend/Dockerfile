FROM --platform=linux/amd64 node:lts

WORKDIR /opt/frontend

COPY package.json /opt/frontend/package.json
COPY package-lock.json /opt/frontend/package-lock.json

RUN npm ci --dev

COPY /bundles-src /opt/frontend/bundles-src

CMD ./node_modules/.bin/parcel build ./bundles-src/index.js --dist-dir ../backend/bundles --public-url "./"
