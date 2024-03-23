# Простое веб приложение

Сделано в целях изучить детальнее создание полноценного веб приложения

## Запуск

```sh
# Copy and change values
cp postgres_password.txt.example postgres_password.txt
cp .env.example .env

# Get cert for SSL
export Dynu_ClientId="Dynu_ClientId"
export Dynu_Secret="Dynu_Secret"
acme.sh --issue -d kotaz.ddnsfree.com --dns dns_dynu
# kotaz - user
# kotaz.ddnsfree.com - domain
cp /home/kotaz/.acme.sh/kotaz.ddnsfree.com_ecc/kotaz.ddnsfree.com.key certs/domain.key
cp /home/kotaz/.acme.sh/kotaz.ddnsfree.com_ecc/fullchain.cer certs/domain.crt
```
