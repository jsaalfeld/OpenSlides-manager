from nginx:mainline

ARG NGINX_HOST
ARG NGINX_PORT
ARG NGINX_SSL_PORT

RUN rm -f /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/nginx.conf
COPY manager.conf /etc/nginx/conf.d/manager.conf

RUN mkdir /app
WORKDIR /app
ADD run.sh /app/run.sh
RUN sed -i "s/#NGINX_HOST/$NGINX_HOST/g" /app/run.sh
RUN chmod +x run.sh
RUN sed -i "s/#NGINX_HOST/$NGINX_HOST/g" /etc/nginx/conf.d/manager.conf
RUN sed -i "s/#NGINX_PORT/$NGINX_PORT/g" /etc/nginx/conf.d/manager.conf
RUN sed -i "s/#NGINX_SSL_PORT/$NGINX_SSL_PORT/g" /etc/nginx/conf.d/manager.conf

RUN ln -sf /dev/stdout /var/log/cron.log

RUN apt-get update && \
  apt-get -y install wget cron

RUN wget https://dl.eff.org/certbot-auto
RUN chmod a+x certbot-auto
RUN ./certbot-auto --os-packages-only -n

CMD ["./run.sh"]
