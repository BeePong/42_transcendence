FROM alpine:3.18.6

RUN apk update && apk add --no-cache nginx openssl

RUN adduser -D -g 'www' www && \
	mkdir /www && chown -R www:www /var/lib/nginx && \
	chown -R www:www /www

RUN mkdir /etc/nginx/ssl && \
	sed -i 's/user nginx;/user www;/' /etc/nginx/nginx.conf

RUN openssl req -x509 -newkey rsa:2048 -nodes -days 365 \
	-out /etc/nginx/ssl/beepong.csr \
	-keyout /etc/nginx/ssl/beepong.key \
	-subj "/C=FI/ST=Helsinki/L=Helsinki/O=beepong/OU=beepong/CN=nginx"

RUN openssl x509 -in /etc/nginx/ssl/beepong.csr -out /etc/nginx/ssl/beepong.pem -outform PEM


COPY ./nginx.conf /etc/nginx/http.d/default.conf

EXPOSE 443

CMD ["nginx", "-g", "daemon off;"]