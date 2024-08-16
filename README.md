# Ili-Services

Respositorio de servicios utiles para interactuar con bases de datos conforme a interlis en PostgreSQL y Geopackage.

## Agradecimientos y Créditos

Este proyecto ha sido posible gracias al trabajo excepcional y la dedicación del equipo detrás de [QgisModelBakerLibrary](https://github.com/opengisch/QgisModelBakerLibrary). Nos gustaría expresar nuestro más sincero agradecimiento a los desarrolladores y colaboradores de este proyecto de código abierto, cuya base ha sido fundamental para la creación de nuestra solución tecnológica personalizada.

## Desarrolladores


### Pruebas unitarias ambiente local

1. Clona el repositorio en tu máquina local:

    ```shell
    git clone https://github.com/ceicol/ili-services.git
    ```

2. Configura un entorno virtual e instala las dependencias requeridas:

    ```shell
    cd ili-services/

    # Se crea el env virtual.
    pip install virtualenv
    python3 -m venv venv

    # Se activa env e instala dependencias
    source venv/bin/activate
    pip install -r requirements.txt

    # Se instala librería de ili2db
    sh scripts/download_dependencies.sh
    ```

3. Establecer variables de entorno (Nota: actualícelas según sea su caso):

    ```shell
    source scripts/config.sh
    ```

4. Ejecutar pruebas unitarias:

    ```shell
    cd iliservices
    nose2-3
    ```


### Pruebas unitarias con docker

```
docker compose -f .docker/docker-compose.yml run --rm iliservices
```
