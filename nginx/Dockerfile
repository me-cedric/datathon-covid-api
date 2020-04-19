FROM node:12 as BUILDER

RUN git clone https://github.com/me-cedric/datathon-covid-gui.git

WORKDIR /datathon-covid-gui

RUN npm i
RUN npm run build

FROM nginx:1.17.4-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d
COPY .htpasswd /etc/nginx/
COPY --from=BUILDER /datathon-covid-gui/dist/datathon-covid-gui-frontend /opt
