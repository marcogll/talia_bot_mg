# 🤖 Talia Bot: Asistente Personal & Orquestador de Negocio

Talia es un **Middleware de Inteligencia Artificial** diseñado para orquestar operaciones de negocio a través de Telegram. Funciona como un asistente personal que responde a roles de usuario específicos, conectando servicios externos como **Vikunja (Gestión de Proyectos)** y **Google Calendar** en una única interfaz conversacional.

---

## 🚀 Concepto Central: Arquitectura Modular y Roles de Usuario

La funcionalidad del bot se basa en dos pilares:

1.  **Enrutamiento por Identidad**: El bot identifica a cada usuario por su Telegram ID y le asigna un rol (`admin`, `crew`, `client`). Cada rol tiene acceso a un conjunto diferente de funcionalidades y menús, definidos en una base de datos SQLite.
2.  **Motor de Flujos de Conversación**: En lugar de código rígido, las conversaciones se definen como "flujos" en archivos **JSON** (`talia_bot/data/flows/`). Un motor central (`flow_engine.py`) interpreta estos archivos para guiar al usuario a través de una serie de preguntas y respuestas, haciendo que el sistema sea altamente escalable y fácil de mantener.

| Rol     | Icono | Descripción         | Permisos Clave                                                              |
| :------ | :---: | :------------------ | :-------------------------------------------------------------------------- |
| **Admin** |  👑   | Dueño / Gerente     | Control total: gestión de proyectos, agenda, y configuración del sistema.   |
| **Crew**  |  👷   | Equipo Operativo    | Funciones limitadas: solicitud de agenda, impresión de documentos.          |
| **Cliente** |  👤   | Usuario Externo     | Embudo de ventas: captación de datos y presentación de servicios.           |

---

## 🛠️ Arquitectura Técnica Simplificada

El sistema opera con el siguiente flujo:

1.  **Recepción de Mensajes**: `main.py` recibe todos los inputs (texto, botones, comandos) desde Telegram.
2.  **Identificación de Usuario**: Se consulta la base de datos (`users.db`) para obtener el rol del usuario.
3.  **Dispatching de Acciones**:
    *   Si el usuario no está en una conversación, se le muestra un menú de botones basado en los flujos JSON disponibles para su rol.
    *   Si el usuario ya está en una conversación, el `flow_engine.py` gestiona la respuesta.
4.  **Ejecución de Módulos**: El motor de flujos invoca módulos específicos (`vikunja.py`, `calendar.py`, etc.) para interactuar con APIs externas según sea necesario.

---

## ⚙️ Instalación y Configuración

### Prerrequisitos

*   Python 3.9+
*   Docker y Docker Compose
*   Cuenta de Telegram Bot (@BotFather)
*   Instancia de Vikunja (Self-hosted)
*   Credenciales de Cuenta de Servicio de Google Cloud (para Calendar API)

### 1. Clonar y Configurar el Entorno

```bash
# Clona el repositorio oficial
git clone https://github.com/marcogll/talia_bot.git
cd talia_bot

# Copia el archivo de ejemplo para las variables de entorno
cp .env.example .env
```

### 2. Variables de Entorno (`.env`)

Abre el archivo `.env` y rellena las siguientes variables. **No subas este archivo a Git.**

```env
# Token de tu bot de Telegram
TELEGRAM_TOKEN=tu_token_telegram

# Tu Telegram ID numérico para permisos de administrador
ADMIN_ID=tu_telegram_id

# Clave de API de OpenAI (si se usa)
OPENAI_API_KEY=sk-...

# URL y Token de tu instancia de Vikunja
VIKUNJA_API_URL=https://tu_vikunja.com/api/v1
VIKUNJA_TOKEN=tu_token_vikunja

# ID del Calendario de Google a gestionar
CALENDAR_ID=tu_id_de_calendario@group.calendar.google.com

# Ruta al archivo de credenciales de Google Cloud.
# Este archivo debe estar en el directorio raíz y se llama 'google_key.json' por defecto.
GOOGLE_SERVICE_ACCOUNT_FILE=./google_key.json
```

### 3. Estructura de Datos y Credenciales

*   **Base de Datos**: La base de datos `users.db` se creará automáticamente si no existe. Para asignar roles, debes agregar manualmente los Telegram IDs en la tabla `users`.
*   **Credenciales de Google**: Coloca tu archivo de credenciales de la cuenta de servicio de Google Cloud en el directorio raíz del proyecto y renómbralo a `google_key.json`. **El archivo `.gitignore` ya está configurado para ignorar este archivo y proteger tus claves.**
*   **Flujos de Conversación**: Para modificar o añadir flujos, edita los archivos JSON en `talia_bot/data/flows/`.

### 4. Ejecución con Docker

La forma más sencilla de levantar el bot es usando Docker Compose:

```bash
docker-compose up --build
```

---

## 📂 Estructura del Proyecto

```text
talia_bot/
├── .env                       # (Local) Variables de entorno y secretos
├── .env.example               # Plantilla de variables de entorno
├── .gitignore                 # Archivos ignorados por Git
├── Dockerfile                 # Define el contenedor de la aplicación
├── docker-compose.yml         # Orquesta el servicio del bot
├── google_key.json            # (Local) Credenciales de Google Cloud
├── requirements.txt           # Dependencias de Python
├── talia_bot/
│   ├── __init__.py
│   ├── main.py                # Entry point, dispatcher y handlers de Telegram
│   ├── db.py                  # Lógica de la base de datos SQLite
│   ├── config.py              # Carga y validación de variables de entorno
│   ├── scheduler.py           # (Futuro) Tareas programadas
│   ├── webhook_client.py      # (Futuro) Cliente para webhooks externos
│   ├── data/
│   │   ├── flows/             # Directorio con flujos de conversación en JSON
│   │   ├── services.json      # Base de conocimiento para ventas
│   │   └── users.db           # Base de datos de usuarios
│   └── modules/
│       ├── __init__.py
│       ├── flow_engine.py     # Motor que interpreta los flujos JSON
│       ├── calendar.py        # Integración con Google Calendar API
│       ├── vikunja.py         # Integración con Vikunja API
│       ├── onboarding.py      # Lógica para el alta de nuevos usuarios
│       ├── llm_engine.py      # (Opcional) Cliente para OpenAI/Gemini
│       └── ... (otros módulos)
└── ...
```

---

## 🗓️ Roadmap

- [ ] Implementar Wizard de creación de Tags NFC (Base64).
- [ ] Conectar Loop de Impresión (SMTP/IMAP).
- [ ] Migrar de OpenAI a Google Gemini 1.5 Pro.
- [ ] Implementar soporte para fotos en impresión.

---

Desarrollado por: Marco G.
Asistente Personalizado v1.0
