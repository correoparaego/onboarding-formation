# Despliegue — MVP Formación Inicial

Guía para desplegar el MVP (Django + React/Vite + PostgreSQL) en infraestructura de la UE.
El cambio SDD `mvp-formacion-inicial` está completo, verificado (56 tests, PASS) y archivado.

## 1. Prerrequisitos

- Cuenta en un PaaS de la UE para el backend Django (p. ej. Render, Railway o Fly.io, región EU).
- Hosting estático de la UE para el front React (p. ej. Vercel, Netlify o Cloudflare Pages, región EU).
- Instancia PostgreSQL en la UE (la del PaaS o externa tipo Neon/Supabase EU).
- Cuenta de email transaccional (Resend o SMTP) para el envío de magic-links.
- Git remoto con acceso para push (este entorno no tiene `gh`/auth).

## 2. Push de ramas y PRs (stacked-to-main)

Las 7 ramas están en local, apiladas. Súbelas y abre los PRs en orden contra `main`:

```bash
git push -u origin mvp/pr1-scaffold-models
git push -u origin mvp/pr2-auth-import
git push -u origin mvp/pr3-courses-enroll-ai
git push -u origin mvp/pr4-reading-test
git push -u origin mvp/pr5-secure-cert-badges-expediente
git push -u origin mvp/pr6-audit-qa
git push -u origin mvp/fix-w1-dni-crypto
```

Luego crea los PRs (cada uno contra `main`; al fusionar PR1, PR2 pasa a ser el diff incremental):

```bash
gh pr create --base main --head mvp/pr1-scaffold-models --title "PR1: scaffold + modelos/migraciones" --body "..."
# ... y así con las 7, en orden.
```

## 3. Variables de entorno (backend Django)

Define al menos estas en el PaaS (nunca en el repo):

| Variable | Descripción |
|----------|-------------|
| `SECRET_KEY` | Clave de Django. Fuertes y únicas en producción. |
| `DNI_ENCRYPTION_KEY` | Clave de cifrado del DNI en reposo (32 bytes en hex/base64). **Obligatoria y secreta.** |
| `DATABASE_URL` | URL de PostgreSQL UE (p. ej. `postgres://user:pass@host:5432/db`). |
| `DEBUG` | `False` en producción. |
| `ALLOWED_HOSTS` | Dominio del backend. |
| `FRONTEND_URL` | Origen del SPA para CORS (p. ej. `https://formacion.example.eu`). |
| `EMAIL_BACKEND` / `RESEND_API_KEY` o `EMAIL_HOST`/`EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD` | Transporte de email (Resend o SMTP). |
| `AI_USE_FAKE_LLM` | `False` en producción para usar el cliente real; la API key la introduce el admin en la UI (BYO), no es env global. |

> La API key del modelo de IA la introduce **cada admin en la propia UI** ( BYO-key, cifrada en servidor). No se configura como variable global.

## 4. Despliegue del backend (Django)

1. Build: `pip install -r backend/requirements.txt`.
2. Migraciones: `python manage.py migrate`.
3. Recolección de estáticos (si aplica): `python manage.py collectstatic --noinput`.
4. Arranque con gunicorn: `gunicorn mvp_project.wsgi:application --bind 0.0.0.0:$PORT`.
5. Comando de salud: `python manage.py check`.

## 5. Despliegue del frontend (React/Vite)

1. En `frontend/`, define `VITE_API_BASE_URL` = URL pública del backend Django.
2. Build: `npm install && npm run build` (genera `dist/`).
3. Publica `dist/` en el hosting estático EU (Vercel/Netlify/Cloudflare).
4. E2E (opcional): `RUN_E2E=1 npm run e2e` requiere navegador; omítelo si no hay entorno gráfico.

## 6. Verificación post-despliegue

- `python manage.py test` → 56 tests OK.
- `python manage.py check` → sin issues.
- Recorrido feliz: importar Excel → empleado recibe magic-link → lee PDF (gate server-authoritative) → test (≤3 intentos) → certificado PDF → insignias → expediente filtrable.
- Auditoría: `GET /api/audit` (solo admin) devuelve eventos append-only, sin DNI.

## 7. Notas no bloqueantes (dejar para fase 2 / producción)

- **Email real**: solo se verificó el transporte `console`; configura Resend/SMTP con credenciales reales.
- **E2E Playwright**: no ejecutado en este entorno (sin navegador); el spec es opt-in.
- **Cliente LLM real**: los tests usan `FakeLLMClient`; el proveedor real se ejercita con la key del admin.
- **CSRF**: exento en `/api/auth/*` y `/api/import` para el MVP; añadir flujo CSRF completo al cablear el SPA.
- **Umbral de aprobación**: `TEST_PASS_THRESHOLD=1.0` (100% acierto) — decisión de producto, ajustable.

## 8. Seguridad

- `DNI_ENCRYPTION_KEY` y `SECRET_KEY` deben ser fuertes, únicas y secretas (gestor de secretos del PaaS).
- El cifrado del DNI usa nonce aleatorio por registro + token HMAC para dedupe (W1 resuelto). No revertir a un esquema determinista.
- La auditoría y los logs nunca contienen el DNI ni tokens crudos.
