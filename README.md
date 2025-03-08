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

# Diferencias con v1
Hemos actualizado el bot para que sea más cómodo de utilizar en general.

## Cambios mayores:
- Ahora todos los comandos funcionan con `/`. Si tienes dudas utiliza las el comando `/ayuda` para entender como funcionan todos los comandos.
- Si quieres crear una partida puedes usar `/crear id:<tu_id> nombre:<nombre_partida> fecha:<dd-mm>` para iniciar una partida.
- Debajo de las partidas aparecen botones para apuntarse o salir de la partida. Si diriges también puedes anular.
- Los nombres de los comandos son los mismos, eso incluye `/apuntar id:<tu_id>`, `/quitar id:<tu_id>`, `/listar`, `/anular id:<tu_id>`.
- Ya no existe el comando `+plantilla` y no se puede copiar-pegar el mensaje ( :[ )

## Otros detalles
- Listar da un fichero csv tambien, asi como un enlace permanente a la partida para apuntarse fácilmente.
- Pulido general del comando ayuda y todo lo que dice el bot.
- Si pulsas ↑ abrirás el último comando.
- Si tecleas `/crear` y pulsas tabulador, te aparecerán campos como `id`, `nombre`, pero tambien `incio`, `fin`, `notas` etc.

## Ejemplos de uso
```
/apuntar id:D&D jugador:Alberto
/apuntar id:D&D
/quitar id:D&D jugador:Alberto 
/quitar id:D&D
/crear id:D&D nombre:La maldicion dia:Jueves
/crear id:D&D nombre:La maldicion dia:Jueves notas:¡Venid antes de las 6 para hacer fichas!
/modificar id:D&D nombre:Piratas nueva_id:Path
/modificar id:Path maximo:6 notas:Ahora solo se pueden anotar 6 jugadores
/mover id:D&D id:Pathfinder
/mover id:D&D id:Pathfinder jugador:Alberto
/anular id:D&D
```