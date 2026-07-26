# Guia de Captura de Pantallas — Plataforma de Onboarding

## Requisitos previos

- Python 3.10+ con el entorno virtual del backend activado
- Node.js 18+ y dependencias del frontend instaladas (`npm install`)
- Playwright instalado (`npx playwright install chromium`)
- Base de datos SQLite con datos de prueba cargados

---

## 1. Cargar datos de prueba

```bash
cd backend
python seed_test_data.py
```

El script es **idempotente** (puede ejecutarse multiples veces sin duplicar datos). Crea:

| Recurso | Detalle |
|---------|---------|
| Admin | `admin` / `admin1234` |
| Posiciones | Operario, Tecnico, Supervisor |
| Cursos | 4 cursos con PDFs, secciones y bancos de preguntas |
| Empleados | 15 empleados distribuidos en las 3 posiciones |
| Matriculaciones | Asignacion automatica por puesto |
| Tokens de acceso | 5 tokens para probar el flujo de empleado |
| Progreso de lectura | Progreso parcial en algunas matriculaciones |
| Expedientes | 2 aprobados, 2 en progreso |
| Certificados | 2 certificados para matriculaciones aprobadas |

Al finalizar, el script imprime una tabla con las credenciales del admin y los tokens/codigos de los empleados para usar en las pruebas.

### Archivo Excel generado

Se genera `backend/test_employees.xlsx` con los 15 empleados de prueba, listo para subirse desde la pantalla de importacion.

---

## 2. Ejecutar la captura de pantallas

```bash
# Terminal 1 — Backend
cd backend
python manage.py runserver

# Terminal 2 — Frontend
cd frontend
npm run dev

# Terminal 3 — Captura de pantallas
cd frontend
TAKE_SCREENSHOTS=1 npx playwright test screenshots.spec.ts
```

En Windows (PowerShell):
```powershell
$env:TAKE_SCREENSHOTS="1"; npx playwright test screenshots.spec.ts
```

Las capturas se guardan en `frontend/screenshots/` con nombres descriptivos:

| Archivo | Pantalla |
|---------|----------|
| `01-landing.png` | Pagina de inicio con enlaces de acceso |
| `02-admin-login.png` | Formulario de login de administracion |
| `03-admin-import-empty.png` | Importacion vacia (sin archivo) |
| `04-admin-import-result.png` | Importacion tras subir Excel |
| `05-admin-courses-list.png` | Listado de cursos |
| `06-admin-course-detail.png` | Detalle del primer curso |
| `07-admin-ai-key.png` | Formulario de clave LLM |
| `08-admin-ai-content.png` | Asistente de contenido IA |
| `09-admin-ai-tests.png` | Generacion de test desde PDF |
| `10-admin-expediente.png` | Tabla de expedientes |
| `11-employee-redeem.png` | Pagina de acceso del empleado |
| `12-employee-mis-cursos.png` | Listado de cursos del empleado |
| `13-pdf-reader-locked.png` | Lector PDF bloqueado (tiempo no cumplido) |
| `14-pdf-reader-progress.png` | Lector PDF con progreso de lectura |

### Usar un token especifico

Para capturar las pantallas de empleado con un token real:

```bash
EMPLOYEE_TEST_TOKEN=<token_del_seed> TAKE_SCREENSHOTS=1 npx playwright test screenshots.spec.ts
```

---

## 3. Descripcion de cada pantalla

### Pagina de inicio (`/`)
Dos enlaces: "Acceso administracion" y "Acceso empleado". Punto de entrada para ambos perfiles.

### Login administracion (`/admin/login`)
Formulario con campos usuario y contrasena. Tras login exitoso redirige al panel de administracion.

### Importar empleados (`/admin/import`)
Zona de arrastre (drag & drop) o seleccion de archivo Excel (.xlsx). Tras la importacion muestra un reporte con filas creadas, duplicadas y rechazadas.

### Gestion de cursos (`/admin/courses`)
Listado de cursos con titulo, posiciones asignadas, numero de secciones y estado del banco de preguntas. Permite crear nuevos cursos y ver el detalle.

### Detalle de curso
Secciones ordenadas, banco de preguntas asociado con opciones y respuesta correcta.

### Clave IA (`/admin/ai/key`)
Formulario para configurar el proveedor LLM (provider, base_url, modelo, clave API). La clave se cifra y nunca se devuelve en claro.

### Contenido IA (`/admin/ai/content`)
Asistente guiado para generar contenido de curso mediante preguntas/respuestas.

### Test desde PDF (`/admin/ai/tests`)
Subida de PDF para generacion automatica de preguntas de comprension.

### Expediente (`/admin/expediente`)
Tabla con resultados por empleado/curso: estado, intentos, puntuacion, fecha de completado.

### Acceso empleado (`/employee/redeem`)
Campo para introducir el codigo/token de acceso recibido por email.

### Mis cursos (`/employee`)
Tarjetas con los cursos asignados, estado (pendiente, en progreso, completado), puntuacion e intentos.

### Lector PDF (`/employee/read`)
Visualizador del PDF del curso con temporizador de lectura. El heartbeat se envia cada 5 segundos. Las secciones se desbloquean secuencialmente al cumplir el tiempo minimo.

---

## 4. Sugerencias de mejora UI/UX

### Estados vacios
1. **Importar empleados**: Mostrar un mensaje ilustrado cuando no hay empleados importados aun, con un boton de accion claro ("Subir archivo Excel") y un enlace para descargar una plantilla de ejemplo.
2. **Mis cursos (empleado)**: Cuando no hay cursos asignados, mostrar un mensaje amigable ("Aun no tienes formaciones asignadas") en lugar de texto plano.
3. **Expediente**: Incluir un estado vacio con resumen estadistico (total empleados, cursos activos, completados).

### Estados de carga
4. **Skeleton loaders**: Sustituir los textos "Cargando..." por skeleton loaders que reflejen la estructura de la lista/tabla que se esta cargando. Esto reduce la percepcion de lentitud.
5. **Importacion Excel**: Mostrar un spinner con progreso durante la subida y el procesamiento del archivo, especialmente para archivos grandes.

### Feedback de errores
6. **Validacion en tiempo real**: En el formulario de login, validar que los campos no esten vacios antes de habilitar el boton (ya se hace parcialmente). Extender a todos los formularios con mensajes inline debajo de cada campo.
7. **Toast notifications**: Implementar un sistema de notificaciones toast para operaciones exitosas (importacion completada, curso creado, clave guardada) en lugar de depender solo del cambio de contenido en pantalla.
8. **Errores de red**: Mostrar un banner persistente cuando se pierde la conexion con el backend, con opcion de reintentar.

### Navegacion
9. **Sidebar de administracion**: Reemplazar la navegacion horizontal por un sidebar lateral fijo con iconos y etiquetas. Mejora la escalabilidad cuando crecen las secciones y es el patron estandar en paneles de administracion.
10. **Breadcrumb**: Anadir breadcrumbs en las pantallas de detalle (curso, empleado) para facilitar la navegacion de vuelta sin usar el boton "atras" del navegador.

### Accesibilidad
11. **Atributos aria**: Anadir `aria-label` descriptivos a botones sin texto visible (navegacion, iconos). Usar `aria-live="polite"` para regiones que se actualizan dinamicamente (contador de tiempo, progreso).
12. **Navegacion por teclado**: Asegurar que todas las acciones (importar, crear curso, redeem) son accesibles con Tab + Enter. Los botones de accion en las tarjetas de cursos deben tener foco visible.
13. **Contraste de colores**: Verificar que los badges de estado (verde, amarillo, rojo) cumplen WCAG AA de contraste. El amarillo (#fff3cd) sobre texto oscuro puede no cumplir.

### Diseno responsivo
14. **Vista movil del lector PDF**: El lector PDF debe ser usable en movil con zoom, scroll vertical y controles de navegacion accesibles con el pulgar.
15. **Tablas adaptativas**: La tabla de expediente debe colapsar a tarjetas en pantallas pequenas (< 768px) mostrando la informacion esencial (empleado, curso, estado).

### Visualizacion de datos
16. **Dashboard de progreso**: En la pantalla de expediente, anadir graficos de barras con la tasa de completado por curso y por posicion. Un resumen visual rapido es mas efectivo que una tabla para identificar problemas.
17. **Barra de progreso en tarjetas de empleado**: Mostrar una barra de progreso visual (porcentaje de secciones completadas / tiempo acumulado) en cada tarjeta de "Mis cursos".

### Formularios
18. **Confirmacion para acciones destructivas**: Anadir un dialogo de confirmacion antes de eliminar un curso o cancelar una matriculacion. Usar un modal con el nombre del elemento a eliminar para evitar errores.
19. **Autoguardado en formularios largos**: En el asistente de contenido IA, guardar borradores automaticamente en localStorage para no perder el trabajo si se cierra el navegador accidentalmente.

### Busqueda y filtrado
20. **Buscador en la tabla de expediente**: Anadir un campo de busqueda por nombre de empleado o titulo de curso, y filtros por estado y posicion. Con 15+ empleados, la tabla se vuelve dificil de navegar sin filtros.
21. **Paginacion**: Implementar paginacion (o scroll infinito) en las listas de empleados, cursos y expedientes cuando el volumen de datos crezca.

### Experiencia movil
22. **Menu hamburguesa**: En movil, colapsar la navegacion de administracion en un menu hamburguesa para maximizar el espacio de contenido.
23. **Touch targets**: Asegurar que todos los botones y enlaces tengan un area de toque minima de 44x44px (recomendacion de Apple/Google).

### Modo oscuro
24. **Soporte para modo oscuro**: Implementar un toggle de tema claro/oscuro usando CSS custom properties. Es una expectativa creciente en aplicaciones modernas y reduce la fatiga visual en sesiones largas de lectura.
