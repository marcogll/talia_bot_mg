# 🤖 Talia Bot: Asistente Personal & Orquestador de Negocio

Talia es un **Middleware de Inteligencia Artificial** diseñado para orquestar operaciones de negocio a través de Telegram. Funciona como un asistente personal que responde a roles de usuario específicos, conectando servicios externos como **Vikunja (Gestión de Proyectos)** y **Google Calendar** en una única interfaz conversacional.

---

## 🚀 Concepto Central: Arquitectura de Agente Autónomo

El bot opera como un agente que sigue un ciclo de **Recepción -> Identificación -> Enrutamiento -> Ejecución**.

1.  **Recepción de Mensajes**: `main.py` actúa como el punto de entrada que recibe todos los inputs (texto, botones, comandos, documentos) desde Telegram.
2.  **Identificación de Usuario**: Al recibir un mensaje, el módulo `identity.py` consulta la base de datos (`users.db`) para obtener el rol del usuario (`admin`, `crew`, `client`).
3.  **Enrutamiento de Acciones**:
    *   **Si el usuario está en una conversación activa**, el `flow_engine.py` toma el control y procesa la respuesta según la definición del flujo JSON correspondiente.
    *   **Si el usuario no está en una conversación**, el sistema le muestra un menú de botones. Estos menús se generan dinámicamente a partir de los archivos de flujo en `talia_bot/data/flows/` que tienen una clave `"trigger_button"`.
4.  **Ejecución de Módulos**: Dependiendo de la acción, se invocan módulos específicos para interactuar con APIs externas:
    *   `sales_rag.py` para generar respuestas de ventas con IA.
    *   `printer.py` para enviar correos de impresión.
    *   `vikunja.py` para gestionar tareas.
    *   `calendar.py` para consultar la agenda.

| Rol     | Icono | Descripción         | Permisos Clave                                                              |
| :------ | :---: | :------------------ | :-------------------------------------------------------------------------- |
| **Admin** |  👑   | Dueño / Gerente     | Control total: gestión de proyectos, agenda, impresión y configuración del sistema. |
| **Crew**  |  👷   | Equipo Operativo    | Funciones limitadas: solicitud de agenda y consulta de tareas.              |
| **Cliente** |  👤   | Usuario Externo     | Embudo de ventas: captación de datos y generación de propuestas con IA.     |

---

## 📋 Flujos de Trabajo y Funcionalidades Clave

El comportamiento del bot se define a través de **flujos de conversación modulares** gestionados por un motor central (`flow_engine.py`). Cada flujo es un archivo `.json` que define una conversación paso a paso, permitiendo una fácil personalización.

### 1. 🤖 Flujo de Ventas RAG (Retrieval-Augmented Generation)

Este es el embudo de ventas principal para nuevos clientes. El bot inicia una conversación para entender las necesidades del prospecto y luego utiliza un modelo de IA para generar una propuesta personalizada.

*   **Recopilación de Datos**: El flujo (`client_sales_funnel.json`) guía al usuario a través de una serie de preguntas para recopilar su nombre, industria y la descripción de su proyecto.
*   **Recuperación de Conocimiento (Retrieval)**: El sistema consulta una base de datos de servicios (`servicios.json`) para encontrar las soluciones más relevantes basadas en las palabras clave del cliente.
*   **Generación Aumentada (Augmented Generation)**: Con la información del cliente y los servicios relevantes, el bot construye un *prompt* detallado y lo envía al `llm_engine` (conectado a OpenAI). El modelo de lenguaje genera una respuesta que conecta las necesidades del cliente con los servicios y ejemplos de trabajo concretos.
*   **Llamada a la Acción**: La respuesta siempre termina sugiriendo el siguiente paso, como agendar una llamada.

### 2. 🖨️ Servicio de Impresión Remota

Permite a los usuarios autorizados (`admin`) enviar documentos a una impresora física directamente desde Telegram.

*   **Envío (SMTP)**: Al recibir un archivo, el bot lo adjunta a un correo electrónico y lo envía a la dirección de la impresora preconfigurada usando credenciales SMTP.
*   **Monitoreo de Estado (IMAP)**: Un comando `/check_print_status` permite al administrador consultar la bandeja de entrada de la impresora. El bot se conecta vía IMAP, busca correos no leídos y reporta el estado de los trabajos de impresión basándose en palabras clave en el asunto (ej. "completed", "failed").

### 3. 📅 Gestión de Agenda y Tareas

*   **Consulta de Agenda**: Se integra con **Google Calendar** para mostrar los eventos del día.
*   **Gestión de Tareas**: Se conecta a **Vikunja** para permitir la creación y seguimiento de tareas desde Telegram.

### 4. 🛂 Sistema de Roles y Permisos

*   El acceso a las funcionalidades está restringido por roles (`admin`, `crew`, `client`), los cuales se gestionan en una base de datos **SQLite**.
*   Los menús y opciones se muestran dinámicamente según el rol del usuario, asegurando que cada quien solo vea las herramientas que le corresponden.

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

Asegúrate de tener los archivos y directorios base en `talia_bot/data/`:
*   `servicios.json`: Catálogo de servicios para el RAG de ventas.
*   `credentials.json`: Credenciales de Google Cloud.
*   `users.db`: Base de datos SQLite que almacena los roles de los usuarios.
*   `flows/`: Directorio que contiene las definiciones de los flujos de conversación en formato JSON. Cada archivo representa una conversación completa para un rol específico.

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
│   ├── main.py              # Entry Point y dispatcher principal
│   ├── db.py                # Gestión de la base de datos SQLite
│   ├── config.py            # Carga de variables de entorno
│   ├── modules/
│   │   ├── flow_engine.py   # Motor de flujos de conversación (lee los JSON)
│   │   ├── identity.py      # Lógica de Roles y Permisos
│   │   ├── llm_engine.py    # Cliente OpenAI/Gemini
│   │   ├── vikunja.py       # API Manager para Tareas
│   │   ├── calendar.py      # Google Calendar Logic & Rules
│   │   ├── printer.py       # SMTP/IMAP Loop
│   │   └── sales_rag.py     # Lógica de Ventas y Servicios
│   └── data/
│       ├── flows/           # Directorio con los flujos de conversación en JSON
│       ├── servicios.json   # Base de conocimiento para ventas
│       ├── credentials.json # Credenciales de Google
│       └── users.db         # Base de datos de usuarios
├── .env.example             # Plantilla de variables de entorno
├── requirements.txt         # Dependencias
├── Dockerfile               # Configuración del contenedor
└── docker-compose.yml       # Orquestador de Docker
```

---

## 🗓️ Roadmap y Funcionalidades Completadas

### Funcionalidades Implementadas
- **✅ Motor de Flujos Conversacionales (JSON)**: Arquitectura central para conversaciones dinámicas.
- **✅ Gestión de Roles y Permisos**: Sistema de `admin`, `crew`, y `client`.
- **✅ Integración con Vikunja**: Creación y consulta de tareas.
- **✅ Integración con Google Calendar**: Consulta de agenda.
- **✅ Servicio de Impresión Remota (SMTP/IMAP)**: Envío de documentos y monitoreo de estado.
- **✅ Flujo de Ventas RAG**: Captura de leads y generación de propuestas personalizadas con IA.

### Próximos Pasos
- [ ] **Wizard de Creación de Tags NFC (Base64)**: Implementar el flujo completo para registrar nuevos colaboradores.
- [ ] **Soporte para Fotos en Impresión**: Añadir la capacidad de enviar imágenes al servicio de impresión.
- [ ] **Migración a Google Gemini 1.5 Pro**: Evaluar y migrar el motor de IA para optimizar costos y capacidades.

---

Desarrollado por: Marco G.
Asistente Personalizado v1.0
