FROM nginx:alpine

# Копируем ваш пользовательский конфиг Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# --key=/home/kotaz/.acme.sh/kotaz.ddnsfree.com_ecc/kotaz.ddnsfree.com.key
# --cert=/home/kotaz/.acme.sh/kotaz.ddnsfree.com_ecc/fullchain.cer
COPY certs/domain.key /etc/nginx/certs/domain.key
COPY certs/domain.crt /etc/nginx/certs/domain.crt
