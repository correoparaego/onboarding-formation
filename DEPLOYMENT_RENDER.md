# Despliegue en Render

Esta guía explica cómo desplegar la aplicación de onboarding en Render.

## Prerrequisitos

1. Cuenta en [Render](https://render.com) (puedes registrarte con GitHub)
2. Repositorio subido a GitHub
3. Tarjeta de crédito/débito para verificación (no se cobra en free tier)

## Pasos de despliegue

### 1. Preparar el repositorio

Asegúrate de que todos los cambios estén commiteados y pusheados a GitHub:

```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### 2. Crear Blueprint en Render

1. Ve a [Render Dashboard](https://dashboard.render.com)
2. Click en "New +" → "Blueprint"
3. Conecta tu repositorio de GitHub
4. Selecciona el repositorio `onboarding-formation`
5. Render detectará automáticamente el archivo `render.yaml`

### 3. Configurar variables de entorno

Render te pedirá que configures las siguientes variables:

#### Backend (onboarding-backend)

| Variable | Valor | Notas |
|----------|-------|-------|
| `DJANGO_ALLOWED_HOSTS` | `<backend-url>.onrender.com` | Reemplaza con la URL de tu backend |
| `FRONTEND_BASE_URL` | `https://<frontend-url>.onrender.com` | Reemplaza con la URL de tu frontend |

#### Frontend (onboarding-frontend)

| Variable | Valor | Notas |
|----------|-------|-------|
| `VITE_API_URL` | `https://<backend-url>.onrender.com` | URL completa del backend |

**Nota**: Las siguientes variables se generan automáticamente:
- `DJANGO_SECRET_KEY`
- `DNI_ENCRYPTION_KEY`
- Credenciales de PostgreSQL (`POSTGRES_DB`, `POSTGRES_USER`, etc.)

### 4. Deploy

1. Click en "Apply" para iniciar el despliegue
2. Render creará los tres servicios:
   - **onboarding-backend**: API Django (Docker)
   - **onboarding-frontend**: Frontend React (Static)
   - **onboarding-db**: PostgreSQL (Managed)
3. Espera a que todos los servicios estén "Live"

### 5. Crear superusuario

Una vez que el backend esté live:

1. Ve al dashboard de Render
2. Click en "onboarding-backend"
3. Ve a "Shell" en el menú lateral
4. Ejecuta:

```bash
python manage.py createsuperuser
```

Sigue las instrucciones para crear el usuario admin.

### 6. Verificar el despliegue

1. **Backend**: `https://<backend-url>.onrender.com/api/health/`
   - Debería devolver: `{"status": "ok", "service": "mvp-formacion-inicial"}`

2. **Frontend**: `https://<frontend-url>.onrender.com`
   - Debería cargar la aplicación

3. **Admin**: `https://<frontend-url>.onrender.com/admin/login`
   - Login con el superusuario creado

### 7. Seed data (opcional)

Si quieres datos de prueba:

1. Ve al Shell del backend
2. Ejecuta:

```bash
python seed_test_data.py
```

Esto creará:
- 15 empleados de ejemplo
- 4 cursos con question banks
- Enrollments y tokens de acceso

## Solución de problemas

### El backend no arranca

1. Revisa los logs en Render → Backend → Logs
2. Verifica que las variables de entorno estén configuradas
3. Asegúrate de que la base de datos PostgreSQL esté "Live"

### Error de CORS

Si ves errores de CORS en la consola del navegador:

1. Verifica que `FRONTEND_BASE_URL` esté configurada correctamente en el backend
2. Asegúrate de que incluya `https://` al principio
3. Reinicia el backend después de cambiar variables

### Error de CSRF

Si ves errores de CSRF:

1. Verifica que `FRONTEND_BASE_URL` esté en `CSRF_TRUSTED_ORIGINS`
2. Asegúrate de que el frontend use HTTPS

### La base de datos no conecta

1. Verifica que el servicio PostgreSQL esté "Live"
2. Verifica que las variables `POSTGRES_*` estén configuradas en el backend
3. Reinicia el backend

## Costos

### Free Tier (primeros 30 días)

- Backend: 750 horas/mes (suficiente para 1 instancia)
- Frontend: 100 GB bandwidth
- PostgreSQL: 256 MB, 90 días

### Después del free tier

- Backend: $7/mes (si excede 750 horas)
- Frontend: $0 (static sites son gratis)
- PostgreSQL: $7/mes (Basic-256mb)
- **Total: ~$14/mes**

## Actualizaciones

Para actualizar la aplicación:

1. Haz cambios en el código
2. Commit y push a GitHub
3. Render detectará automáticamente los cambios y hará redeploy

Para forzar un redeploy manual:

1. Ve al servicio en Render
2. Click en "Manual Deploy" → "Deploy latest commit"

## Monitoreo

Render proporciona:
- Logs en tiempo real
- Métricas básicas (CPU, memoria, requests)
- Health checks automáticos

Para ver logs:
1. Ve al servicio en Render
2. Click en "Logs" en el menú lateral

## Dominio personalizado (opcional)

Para usar tu propio dominio:

1. Ve al servicio en Render
2. Settings → Custom Domain
3. Añade tu dominio
4. Configura los registros DNS según las instrucciones

## Soporte

- [Documentación de Render](https://render.com/docs)
- [Comunidad de Render](https://community.render.com)
- [Status de Render](https://status.render.com)
