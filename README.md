# Bot Bukaneros

Hice este bot en un finde para aprender python o asi. Si quieres usar el bot instala los requirements.txt y sube un archivo .env con un BETA_TOKEN y un DEPLOY_TOKEN. 

# Instrucciones 
Para Dockerizar el bot en un servidor nuevo seguir estas instrucciones de uso. (thx rafael anier)

## 1. Instalar Docker
```
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

## 2. Permitir rootless user
```
sudo sh -eux << EOF
```

## 3. newuidmap & newgidmap
Instalar newuidmap & newgidmap binaries
```
apt-get install -y uidmap
EOF

dockerd-rootless-setuptool.sh install
```

## 4. Reinicio de docker
Hacer que el servicio de docker rearranque automaticamente.
```
sudo loginctl enable-linger ubuntu
```

## 5. Repositorio
Clonar el repositorio del bot
```
git clone https://github.com/jahuerta92/bot-bukaneros.git
```

## 6. El .env
Crear el fichero .env y meter el token
```
cd bot-bukaneros
echo "BETA_TOKEN=loquesea" > .env
echo "DEPLOY_TOKEN=loquesea" >> .env
```

## 7. Crear el contenedor y arrancarlo.
```
docker compose up -d --build
```