# Odoo Restaurante con Docker y lista de espera

Proyecto para la instalacion local de Odoo usando Docker Compose y una
personalizacion funcional sobre el modulo de Restaurante.

## Arquitectura local

- `db`: contenedor PostgreSQL 15 usado por Odoo.
- `web`: contenedor principal con la imagen oficial `odoo:19.0`.
- `odoo-init`: servicio temporal que inicializa la base de datos e instala los
  modulos necesarios.
- `./config`: configuracion de Odoo.
- `./addons`: addons personalizados montados en `/mnt/extra-addons`.
- `odoo_pg_pass`: archivo usado como secret local para la contrasena de
  PostgreSQL.

## Personalizacion implementada

El addon `restaurant_waitlist` agrega una lista de espera para restaurante.
Permite registrar clientes que esperan mesa, guardar telefono, cantidad de
personas, prioridad, tiempo estimado, restaurante, mesa asignada y estado del
turno.

Estados disponibles:

- `Waiting`: cliente en espera.
- `Notified`: cliente avisado.
- `Seated`: cliente sentado en una mesa asignada.
- `Cancelled`: turno cancelado.

La funcionalidad se demuestra creando una entrada en la lista de espera,
notificando al cliente, asignando una mesa y marcando el turno como sentado.

## Requisitos

- Docker Desktop instalado y en ejecucion.
- Docker Compose disponible desde el comando `docker compose`.

## Instalacion y ejecucion

1. Levantar PostgreSQL:

   ```bash
   docker compose up -d db
   ```

2. Inicializar la base e instalar Odoo Restaurante y el addon personalizado:

   ```bash
   docker compose --profile setup run --rm odoo-init
   ```

3. Levantar Odoo:

   ```bash
   docker compose up -d web
   ```

4. Verificar contenedores:

   ```bash
   docker compose ps
   ```

5. Abrir Odoo:

   ```text
   http://localhost:8069
   ```

## Datos de configuracion

- Base de datos: `odoo_restaurante`
- Usuario web de Odoo: `reyessamayoa8@gmail.com`
- Contrasena web de Odoo: `Buenas123$`
- Usuario PostgreSQL: `odoo`
- Password PostgreSQL: `OdooRestauranteDB2026!`
- Master password Odoo: `OdooRestauranteAdmin2026!`
- Puerto local: `8069`

## Evidencia sugerida para el video

1. Mostrar la carpeta del proyecto y el archivo `docker-compose.yml`.
2. Ejecutar `docker compose ps` para evidenciar los contenedores.
3. Abrir `http://localhost:8069` y mostrar que Odoo corre localmente.
4. Mostrar el modulo base de Restaurante / Point of Sale.
5. Abrir el menu `Restaurant Waitlist`.
6. Crear un registro con cliente, telefono y numero de personas.
7. Cambiar estado a `Notified`.
8. Asignar una mesa y usar `Seat Customer`.

## Archivos importantes

- `docker-compose.yml`: servicios de PostgreSQL, Odoo y setup inicial.
- `odoo_pg_pass`: secret local usado por Docker Compose para PostgreSQL.
- `config/odoo.conf`: configuracion principal de Odoo.
- `addons/restaurant_waitlist`: codigo fuente del addon personalizado.
- `docs/informe_entrega.md`: documento base para generar el PDF de entrega.
