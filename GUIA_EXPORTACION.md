# Guía de Exportación y Ejecución de Contenedores Docker con GPU (ROCm/AMD)

Esta guía describe el proceso paso a paso para construir la imagen de Docker del pipeline de traducción de podcasts, exportarla como un archivo comprimido, transferirla al ordenador de destino con potencia de GPU AMD y finalmente ejecutarla.

---

## 1. Construir la Imagen en el Ordenador de Origen

Dado que el archivo `Dockerfile` está configurado con una base para ROCm (`rocm/pytorch:latest`), debes construir la imagen usando Docker:

```bash
# Navega al directorio del proyecto
cd /home/victor/proyectos-ia/podtrad

# Construye la imagen unificada
docker build -t podtrad-pipeline:latest .
```

---

## 2. Exportar la Imagen a un Archivo Comprimido

Una vez construida, puedes empaquetarla en un archivo `.tar.gz` para poder transferirla fácilmente:

```bash
# Guardar y comprimir la imagen en un archivo
docker save podtrad-pipeline:latest | gzip > podtrad-pipeline.tar.gz
```
Este comando generará el archivo `podtrad-pipeline.tar.gz` en tu directorio actual.

---

## 3. Transferir el Archivo al Ordenador con GPU

Utiliza `scp`, un pendrive o cualquier otro método de transferencia de archivos para enviar el archivo al ordenador de destino.

**Ejemplo con `scp`:**
```bash
scp podtrad-pipeline.tar.gz usuario@ip_del_servidor:/ruta/destino/
```

> [!NOTE]
> Asegúrate de transferir también el archivo `docker-compose.yml` y las carpetas `scripts`, `audio` y `modelos` si vas a utilizar volúmenes para persistir datos.

---

## 4. Importar la Imagen en el Ordenador de Destino

En el ordenador donde se ejecutará el pipeline (el que tiene la GPU), carga la imagen en Docker:

```bash
# Cargar la imagen desde el archivo comprimido
gunzip -c podtrad-pipeline.tar.gz | docker load
```

Para verificar que la imagen se haya cargado correctamente, ejecuta:
```bash
docker images
```
Deberías ver `podtrad-pipeline` con el tag `latest` en la lista.

---

## 5. Configurar y Ejecutar con Docker Compose en el Destino

En el ordenador de destino, crea una carpeta para el proyecto y coloca allí el archivo `docker-compose.yml` que ya tienes configurado. 

Como el servidor de destino tiene **GPU AMD con soporte ROCm**, el archivo `docker-compose.yml` ya está optimizado para mapear los dispositivos de la GPU (`/dev/kfd` y `/dev/dri`) al contenedor.

### Estructura de archivos recomendada en el destino:
```text
podtrad/
├── docker-compose.yml
├── scripts/
├── audio/
└── modelos/
```

### Ejecutar los contenedores:
```bash
# Ejecutar los agentes Cora, Siro y Milo en segundo plano
docker compose up -d
```

### Comprobar el estado y uso de la GPU:
Para asegurarte de que el contenedor está utilizando la GPU AMD (ROCm), puedes ejecutar comandos de diagnóstico en el ordenador de destino:
```bash
# Monitorizar el uso de la GPU AMD
rocm-smi
```

---

## Alternativa: Usar un Registro de Docker (Docker Hub / GitHub Packages)

Si prefieres no transferir archivos pesados manualmente:

1. **Subir al registro (Origen):**
   ```bash
   docker tag podtrad-pipeline:latest tu_usuario/podtrad-pipeline:latest
   docker push tu_usuario/podtrad-pipeline:latest
   ```

2. **Descargar desde el registro (Destino):**
   ```bash
   docker pull tu_usuario/podtrad-pipeline:latest
   ```
   *Luego, actualiza la propiedad `image` en tu `docker-compose.yml` para que apunte a `tu_usuario/podtrad-pipeline:latest` en lugar de compilar con `build`.*
