# Agent_skills.md

Este documento detalla las capacidades técnicas, reglas de negocio y límites de cada agente definido en `AGENTS.md`.

---

### 1. Agente Recepcionista (`main.py`)

-   **Capacidades Técnicas**:
    -   **Framework**: `python-telegram-bot`.
    -   **Manejo de Eventos**: Utiliza `CommandHandler`, `CallbackQueryHandler`, `MessageHandler` para registrar y procesar diferentes tipos de actualizaciones de Telegram.
    -   **Inyección de Dependencias**: Almacena instancias compartidas (como `FlowEngine`) en el `bot_data` del contexto de la aplicación para que estén disponibles globalmente.

-   **Reglas de Negocio**:
    -   El comando `/start` siempre debe borrar cualquier estado de conversación previo del usuario para asegurar un inicio limpio.
    -   Los documentos (`filters.Document.ALL`) se enrutan exclusivamente al manejador de impresión.
    -   Los mensajes de texto y voz se enrutan al `text_and_voice_handler`, que a su vez los delega al motor de flujos.

-   **Límites Claros**:
    -   No implementa lógica de reintentos para comandos fallidos.
    -   No contiene estado. El estado se gestiona en la base de datos a través de otros agentes.

---

### 2. Agente de Identidad (`identity.py`, `db.py`)

-   **Capacidades Técnicas**:
    -   **Base de Datos**: `SQLite`.
    -   **Conexión**: Utiliza `sqlite3` para conectarse a la base de datos `users.db`.
    -   **Modelo de Datos**: La tabla `users` contiene `chat_id` (INTEGER, PRIMARY KEY) y `role` (TEXT).

-   **Reglas de Negocio**:
    -   Un `chat_id` solo puede tener un rol.
    -   Si un usuario no se encuentra en la base de datos, se le asigna el rol de `client` por defecto.
    -   Los roles válidos son `admin`, `crew`, y `client`. Cualquier otro valor se trata como `client`.

-   **Límites Claros**:
    -   No gestiona la adición o eliminación de usuarios. Esto debe hacerse manualmente en la base de datos por ahora.
    -   No ofrece permisos granulares, solo los tres roles definidos.

---

### 3. Agente de Motor de Flujos (`flow_engine.py`)

-   **Capacidades Técnicas**:
    -   **Serialización**: Lee y parsea archivos `.json` para definir la estructura de las conversaciones.
    -   **Persistencia de Estado**: Utiliza `SQLite` para almacenar y recuperar el estado de la conversación de cada usuario en la tabla `conversations`.
    -   **Arquitectura**: Máquina de estados finitos donde cada paso de la conversación es un estado.

-   **Reglas de Negocio**:
    -   Cada flujo debe tener un `id` único y una clave `role` que restringe su acceso.
    -   Los pasos se ejecutan en orden secuencial según su `step_id`.
    -   Al final de un flujo, se puede invocar una función de "finalización" (ej. `generate_sales_pitch`) para procesar los datos recopilados.

-   **Límites Claros**:
    -   No soporta bifurcaciones complejas (condicionales) en los flujos. La lógica es estrictamente lineal.
    -   No tiene un mecanismo de "timeout". Las conversaciones pueden permanecer activas indefinidamente hasta que el usuario las complete o las reinicie.

---

### 4. Agente de Onboarding y Menús (`onboarding.py`)

-   **Capacidades Técnicas**:
    -   **Framework**: `python-telegram-bot`.
    -   **UI**: Construye menús utilizando `InlineKeyboardMarkup` y `InlineKeyboardButton`.

-   **Reglas de Negocio**:
    -   Debe mostrar un menú específico para cada uno de los tres roles (`admin`, `crew`, `client`).
    -   **Fallo Actual**: Los menús son estáticos y no se generan a partir de los flujos disponibles, lo que impide el acceso a flujos que sí existen.

-   **Límites Claros**:
    -   No puede mostrar menús que dependan del estado del usuario (ej. un botón diferente si el usuario ya ha completado una tarea).

---

### 5. Agente de Agenda (`calendar.py`, `agenda.py`, `aprobaciones.py`)

-   **Capacidades Técnicas**:
    -   **Integraciones**: API de Google Calendar (`googleapiclient`).
    -   **Autenticación**: Utiliza una cuenta de servicio de Google Cloud con un archivo `google_key.json`.
    -   **Manejo de Fechas**: Utiliza la librería `datetime` para manejar zonas horarias y rangos de tiempo.

-   **Reglas de Negocio**:
    -   El tiempo personal (del `PERSONAL_GOOGLE_CALENDAR_ID`) es prioritario y se considera "ocupado" e inamovible.
    -   Los eventos propuestos por el `crew` solo deben enviarse a Google Calendar después de ser aprobados por un `admin`.
    -   Una vez que una actividad es rechazada, su estado debe persistir y no debe volver a mostrarse como "pendiente".
    -   **Fallo Actual**: El código ignora los diferentes IDs de calendario y solo usa uno genérico, rompiendo la separación entre personal y trabajo.

-   **Límites Claros**:
    -   No puede modificar eventos existentes, solo crearlos.
    -   La lógica de aprobación es binaria (aprobar/rechazar) y no permite re-programación o negociación.

---

### 6. Agente de Impresión (`printer.py`)

-   **Capacidades Técnicas**:
    -   **Protocolos de Red**: `SMTP` para enviar correos y `IMAP` para leerlos.
    -   **Librerías**: `smtplib` y `imaplib` de la biblioteca estándar de Python.
    -   **Manejo de Archivos**: Descarga temporalmente los archivos de Telegram al disco antes de enviarlos.

-   **Reglas de Negocio**:
    -   Solo los usuarios con rol `admin` pueden usar esta función (verificación de permisos).
    -   El estado se determina buscando palabras clave (ej. "completed", "failed") en los asuntos de los correos no leídos.

-   **Límites Claros**:
    -   No maneja la impresión de imágenes, solo documentos.
    -   No tiene un sistema de cola. Las solicitudes se procesan de forma síncrona.

---

### 7. Agente de RAG y Ventas (`sales_rag.py`, `llm_engine.py`)

-   **Capacidades Técnicas**:
    -   **Integraciones**: API de OpenAI.
    -   **Procesamiento de Lenguaje Natural (PLN)**: Realiza una búsqueda simple de palabras clave en `services.json` para encontrar contexto relevante.
    -   **Generación de Prompts**: Construye un prompt detallado para el LLM a partir de una plantilla y los datos recopilados del usuario.

-   **Reglas de Negocio**:
    -   La regla "sin contexto, no hay respuesta" es obligatoria. Si la búsqueda en `services.json` no arroja resultados, el agente debe detenerse.
    -   **Fallo Actual**: Esta regla no se está aplicando, lo que resulta in respuestas genéricas.

-   **Límites Claros**:
    -   El mecanismo de "retrieval" (recuperación) es una búsqueda de palabras clave, no un sistema de embeddings vectoriales. Su precisión es limitada.
    -   No mantiene memoria de interacciones pasadas con el cliente.

---

### 8. Agente de Transcripción (Whisper)

-   **Capacidades Técnicas**:
    -   **Integraciones Futuras**: API de OpenAI (Whisper).
    -   **Manejo de Medios**: Deberá poder descargar archivos de audio de Telegram y enviarlos como una solicitud `multipart/form-data`.

-   **Reglas de Negocio**:
    -   Debe ser capaz de manejar diferentes formatos de audio si Telegram los proporciona.
    -   Debe tener un manejo de errores para cuando la transcripción falle.

-   **Límites Claros**:
    -   **Estado Actual**: No implementado. El `text_and_voice_handler` contiene una respuesta placeholder.
    -   No está diseñado para la traducción, solo para la transcripción del idioma hablado.
