# El Bukabot 

Este es el bot para gestionar eventos de bukaneros del rol. Sigue las instrucciones para arrancar el bot.

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
Crear el fichero .env y meter los secretos.
```
cd bot-bukaneros
echo "BETA_TOKEN=token_desarrollo_discord" > .env
echo "DEPLOY_TOKEN=token_lanzamiento_discord" >> .env
echo "MONGO_SECRET=password_mongodb" >> .env
echo "MONGO_USER=usuario_mongodb" >> .env
```

## 7. Crear el contenedor y arrancarlo.
Arrancar el servidor así
```
docker compose up -d --build
```

# Uso
El bot tiene el comando `+help` solo para los administradores del servidor (Usuarios 'administrador'). Para poner el bot operativo es nevesario usar el comando `+sync` despues de que el bot entre al servidor.

Además, para consultar el resto de operaciones, los usuarios pueden utilizar el comando `/ayuda`. 
