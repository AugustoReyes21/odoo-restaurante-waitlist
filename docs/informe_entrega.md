# Instalacion local de Odoo con Docker y personalizacion de Restaurante

## Nombre completo

Hilario Galindo

## Arquitectura local utilizada

La solucion utiliza una arquitectura local basada en contenedores Docker. El
proyecto se levanta con Docker Compose y contiene tres servicios principales:

- `db`: base de datos PostgreSQL 15, requerida por Odoo para almacenar la
  informacion del ERP.
- `odoo`: aplicacion principal de Odoo, expuesta localmente en el puerto `8069`.
- `odoo-init`: servicio temporal utilizado para inicializar la base de datos e
  instalar los modulos necesarios.

El archivo `docker-compose.yml` monta dos carpetas locales importantes:

- `config/`: contiene el archivo `odoo.conf`.
- `addons/`: contiene el codigo de la personalizacion desarrollada.

## Descripcion corta de la instalacion realizada

La instalacion se realizo utilizando la imagen oficial de Odoo `odoo:19.0` y
PostgreSQL 15. Primero se levanta la base de datos, luego se ejecuta el servicio
`odoo-init` para crear la base `odoo_restaurante` e instalar los modulos base,
`point_of_sale`, `pos_restaurant` y el modulo personalizado
`restaurant_waitlist`.

Comandos utilizados:

```bash
docker compose up -d db
docker compose --profile setup run --rm odoo-init
docker compose up -d odoo
docker compose ps
```

La aplicacion queda disponible en:

```text
http://localhost:8069
```

Credenciales de acceso a Odoo:

```text
Email: reyessamayoa8@gmail.com
Contrasena: Buenas123$
```

## Explicacion de la personalizacion implementada

La personalizacion implementada se llama `restaurant_waitlist` y agrega un
listado de espera para el modulo de Restaurante de Odoo.

La mejora permite registrar clientes que llegan al restaurante cuando no hay una
mesa disponible inmediatamente. Cada registro permite guardar:

- Nombre del cliente.
- Telefono.
- Numero de personas.
- Hora de llegada.
- Tiempo estimado de espera.
- Prioridad.
- Restaurante o punto de venta relacionado.
- Mesa asignada.
- Notas.
- Estado del turno.

El flujo funcional implementado incluye los estados:

- `Waiting`: el cliente fue agregado a la lista de espera.
- `Notified`: el cliente ya fue avisado.
- `Seated`: el cliente fue sentado en una mesa asignada.
- `Cancelled`: el turno fue cancelado.

Tambien se agrego una secuencia automatica para identificar cada turno con un
codigo como `WL/00001`. La vista incluye lista, formulario, filtros y botones de
accion para cambiar el estado del registro. Si se intenta sentar a un cliente
sin asignar mesa, el sistema muestra una validacion para evitar cerrar el turno
incorrectamente.

## Enlace al video en Google Drive

Pegar aqui el enlace del video con permisos de revision:

```text
ENLACE_GOOGLE_DRIVE
```

## Enlace al repositorio publico de GitHub

Pegar aqui el enlace del repositorio publico:

```text
https://github.com/AugustoReyes21/odoo-restaurante-waitlist
```

## Guion breve del video

1. Mostrar el archivo `docker-compose.yml` y explicar que contiene los servicios
   `db`, `odoo` y `odoo-init`.
2. Ejecutar o mostrar `docker compose ps` para evidenciar que los contenedores
   estan levantados.
3. Abrir `http://localhost:8069` para demostrar que Odoo esta corriendo
   localmente.
4. Mostrar el modulo base de Point of Sale / Restaurante.
5. Abrir el menu `Restaurant Waitlist`.
6. Crear un cliente en espera con cantidad de personas y telefono.
7. Cambiar el estado a `Notified`.
8. Asignar una mesa y presionar `Seat Customer` para demostrar que la
   personalizacion funciona.
