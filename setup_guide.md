# Guía de Configuración: Sincronización de Sheets, Calendar y Gmail

Este documento te guiará paso a paso para configurar tu entorno en Google Cloud, habilitar las APIs necesarias y preparar el entorno local en Visual Studio Code para ejecutar el script de automatización.

## 1. Configurar el Proyecto en Google Cloud Console

1. Dirígete a [Google Cloud Console](https://console.cloud.google.com/).
2. Haz clic en el selector de proyectos (arriba a la izquierda, junto al logo de Google Cloud) y selecciona **Nuevo Proyecto**.
3. Asigna un nombre descriptivo a tu proyecto (por ejemplo, `Sincronizador Workspace`) y haz clic en **Crear**.
4. Una vez creado (tomará unos segundos), asegúrate de tener este nuevo proyecto seleccionado.

## 2. Habilitar las APIs necesarias

1. En el menú de navegación de la izquierda, ve a **APIs y servicios** > **Biblioteca**.
2. Necesitarás buscar y habilitar tres APIs. Búscalas una por una y haz clic en **Habilitar**:
   *   **Google Sheets API**
   *   **Google Calendar API**
   *   **Gmail API**

## 3. Configurar la Pantalla de Consentimiento de OAuth

*Antes de crear tus credenciales, Google requiere que configures una pantalla de consentimiento (lo que ven los usuarios al iniciar sesión).*

1. Ve a **APIs y servicios** > **Pantalla de consentimiento de OAuth**.
2. Selecciona el tipo de usuario como **Externo** (a menos que uses una cuenta empresarial de Google Workspace, en cuyo caso puedes usar Interno) y haz clic en **Crear**.
3. Completa los campos obligatorios:
   *   **Nombre de la aplicación**: Ej. *App de Sincronización*
   *   **Correo electrónico de asistencia al usuario**: Selecciona tu correo.
   *   **Información de contacto del desarrollador**: Ingresa tu correo electrónico.
4. Haz clic en **Guardar y continuar**.
5. En la sección de **Permisos (Scopes)**, no es estrictamente necesario añadirlos aquí para un entorno de pruebas, puedes simplemente hacer clic en **Guardar y continuar**.
6. En la sección **Usuarios de prueba**, haz clic en **Agregar users** y **escribe el correo electrónico de tu cuenta de Google** (la que usarás para ejecutar el script). *Si no haces esto, recibirás un error al intentar iniciar sesión*. Guarda y continúa.

## 4. Crear Credenciales (`credentials.json`)

1. En el menú de la izquierda, ve a **APIs y servicios** > **Credenciales**.
2. Haz clic en el botón superior **+ Crear credenciales** y selecciona **ID de cliente de OAuth**.
3. En **Tipo de aplicación**, elige **App de escritorio**.
4. Ponle un nombre (ej. *Cliente Desktop*) y haz clic en **Crear**.
5. Aparecerá una ventana modal con tu ID y Secreto de cliente. Haz clic en el botón **Descargar JSON** (el ícono de la flecha hacia abajo).
6. **Importante:** Renombra el archivo recién descargado a **`credentials.json`** y muévelo a la misma carpeta donde vas a guardar tu script de Python en Visual Studio Code.

## 5. Preparar el Entorno en Visual Studio Code

1. Abre Visual Studio Code y carga la carpeta de tu proyecto.
2. Abre la terminal en VS Code (`Ctrl + ñ` o `Terminal > New Terminal`).
3. Instala las librerías oficiales de Google para Python ejecutando el siguiente comando:

```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## 6. Primer Uso y Archivo `token.json`

1. Abre tu archivo `sync_script.py` y asegúrate de actualizar las constantes `SPREADSHEET_ID` y `RANGE_NAME` con los datos de tu hoja de Google Sheets.
2. Ejecuta el script.
3. Como es la primera vez, **se abrirá una pestaña en tu navegador web** pidiéndote iniciar sesión con Google.
4. Selecciona la cuenta que agregaste como "Usuario de prueba".
5. Es posible que Google te muestre una advertencia de seguridad indicando que "Google no verificó esta app". Haz clic en **Configuración avanzada** y luego en **Ir a [Nombre de tu App] (no seguro)**.
6. Otorga los permisos solicitados (ver y editar tus hojas de cálculo, administrar tu calendario y enviar correos).
7. Una vez completado, puedes cerrar la pestaña.
8. En tu carpeta de VS Code, notarás que apareció un nuevo archivo llamado **`token.json`**. Este archivo guarda tus permisos de acceso de forma segura para que no tengas que volver a iniciar sesión en futuras ejecuciones.

*Nota: Si alguna vez modificas la variable `SCOPES` en tu código Python para añadir más permisos, deberás eliminar manualmente el archivo `token.json` y volver a ejecutar el script para que Google te solicite los nuevos permisos.*

