# Guía de Despliegue en Streamlit Community Cloud

Esta guía explica cómo desplegar la aplicación de forma segura utilizando una **Cuenta de Servicio (Service Account)** de Google Cloud y `st.secrets`.

## 📧 Configuración de Correos (Para Gmail Personal)
Como creaste tu proyecto en una cuenta personal de Gmail, **la API de Gmail con Cuenta de Servicio no funcionará**. Por ello, el código ahora utiliza `smtplib` (un protocolo nativo de envío de correos).
Para que funcione:
1. Ve a los ajustes de seguridad de tu cuenta de Google: [Seguridad de Google](https://myaccount.google.com/security)
2. Asegúrate de tener activada la **Verificación en 2 pasos**.
3. Busca la opción **Contraseñas de aplicaciones** (App passwords).
4. Crea una nueva contraseña (selecciona "Otra", ponle nombre "Streamlit App"). 
5. Google te dará una contraseña de 16 letras. Guárdala, la usaremos en el paso 3.

---

## 1. Crear la Cuenta de Servicio en Google Cloud

1. Entra a [Google Cloud Console](https://console.cloud.google.com/) en tu proyecto.
2. En el menú de navegación, ve a **IAM y administración** > **Cuentas de servicio**.
3. Haz clic en **+ CREAR CUENTA DE SERVICIO**.
4. Ponle un nombre (ej. `streamlit-backend`) y haz clic en **Crear y continuar** y luego en **Listo**.
5. Verás tu cuenta en la lista. Fíjate en su correo electrónico (termina en `.iam.gserviceaccount.com`). **Cópialo**.
6. Haz clic en los tres puntos a la derecha de esa cuenta > **Administrar claves**.
7. Clic en **AGREGAR CLAVE** > **Crear clave nueva**. Selecciona el formato **JSON** y descárgala.
8. **Paso Clave para Google Sheets:** Abre tu archivo de Google Sheets en el navegador web, dale a **Compartir** y comparte el archivo (como Editor) con el correo electrónico de la cuenta de servicio que copiaste en el paso 5.

## 2. Preparar el Repositorio de GitHub

Para subir la app a la nube, necesitas versionarla en GitHub.
*Asegúrate de NO subir nunca el archivo JSON de tu Service Account, ni `credentials.json`, ni `token.json` a un repositorio público.*

1. El archivo `requirements.txt` ya ha sido creado en tu carpeta. Este le dice a Streamlit qué dependencias instalar en sus servidores.
2. Sube los archivos `app.py` y `requirements.txt` a un repositorio nuevo en tu cuenta de [GitHub](https://github.com/).

## 3. Despliegue y Configuración de st.secrets

1. Inicia sesión en [Streamlit Community Cloud](https://share.streamlit.io/).
2. Haz clic en **New app** y da permisos para conectar tu cuenta de GitHub si es la primera vez.
3. Selecciona tu repositorio, tu rama (`main` o `master`) y el archivo `app.py`.
4. **ANTES DE DESPLEGAR:** Haz clic en **Advanced settings**.
5. En la ventana de configuración, verás una caja de texto llamada **Secrets**. Aquí debes pegar el contenido del archivo JSON de tu cuenta de servicio formateado como TOML. Debería verse exactamente así:

```toml
[gcp_service_account]
type = "service_account"
project_id = "TU_PROYECTO_ID"
private_key_id = "TU_PRIVATE_KEY_ID"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "TU_CUENTA@TU_PROYECTO.iam.gserviceaccount.com"
client_id = "123456789..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
universe_domain = "googleapis.com"

[email]
sender_email = "tu_correo_personal@gmail.com"
app_password = "las_16_letras_de_tu_app_password"
```
*(Nota: Pega los valores literales del archivo JSON, prestando especial atención a que los saltos de línea `\n` en la `private_key` se mantengan como caracteres `\n`)*

6. Haz clic en **Save** y luego en **Deploy!**

Una vez que termine el despliegue de dependencias, tu app estará disponible online de forma persistente.

