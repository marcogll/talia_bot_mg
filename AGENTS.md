# AGENTS.md

Este documento define los agentes que componen el sistema Talia Bot y sus responsabilidades. Un "agente" es un componente de software con un propósito claro y un conjunto de responsabilidades definidas.

---

### 1. Agente Recepcionista (`main.py`)

Es el punto de entrada principal del sistema. Actúa como el primer filtro para todas las interacciones del usuario.

-   **Responsabilidades**:
    -   Recibir todas las actualizaciones de Telegram (mensajes de texto, comandos, clics en botones, documentos, mensajes de voz).
    -   Inicializar y registrar todos los manejadores de comandos y mensajes.
    -   Delegar las actualizaciones al agente o manejador correspondiente.
    -   Gestionar el ciclo de vida de la aplicación.

-   **Flujos que Maneja**:
    -   Comandos (`/start`, `/reset`, `/check_print_status`).
    -   Recepción de documentos para el Agente de Impresión.
    -   Mensajes de texto y voz para el Agente de Motor de Flujos.
    -   Clics en botones para el Despachador de Botones.

-   **Flujos que NO Debe Manejar**:
    -   No debe contener lógica de negocio compleja. Su única función es enrutar.
    -   No debe gestionar el estado de una conversación.

---

### 2. Agente de Identidad (`identity.py`, `db.py`)

Este agente es responsable de conocer "quién" es el usuario y qué permisos tiene.

-   **Responsabilidades**:
    -   Consultar la base de datos `users.db` para obtener el rol de un usuario (`admin`, `crew`, `client`) a partir de su `chat_id`.
    -   Proporcionar esta información a otros agentes para que puedan tomar decisiones de enrutamiento y acceso.

-   **Flujos que Maneja**:
    -   Verificación de rol en el comando `/start`.
    -   Verificación de permisos para acceder a flujos específicos.

-   **Flujos que NO Debe Manejar**:
    -   No gestiona la lógica de las conversaciones.
    -   No interactúa con APIs externas.

---

### 3. Agente de Motor de Flujos (`flow_engine.py`)

Es el cerebro de las conversaciones de múltiples pasos. Orquesta la interacción con el usuario basándose en definiciones declarativas.

-   **Responsabilidades**:
    -   Cargar todas las definiciones de flujo desde los archivos `.json` en el directorio `data/flows/`.
    -   Gestionar el estado de la conversación de cada usuario (qué flujo está activo, en qué paso está y qué datos ha recopilado).
    -   Persistir y recuperar el estado de la conversación desde la base de datos.
    -   Ejecutar acciones de finalización cuando un flujo se completa (ej. generar un pitch de ventas).

-   **Flujos que Maneja**:
    -   Cualquier conversación definida en un archivo `.json` (ej. `client_sales_funnel`, `admin_create_nfc_tag`).

-   **Flujos que NO Debe Manejar**:
    -   Acciones simples que no requieren una conversación de varios pasos (ej. `view_agenda`).
    -   La generación del menú inicial de opciones.

---

### 4. Agente de Onboarding y Menús (`onboarding.py`)

Este agente es responsable de la primera impresión y de la navegación principal del usuario.

-   **Responsabilidades**:
    -   Presentar el mensaje de bienvenida y el menú de opciones principal al usuario cuando ejecuta `/start`.
    -   Generar los menús de botones específicos para cada rol (`admin`, `crew`, `client`).
    -   **Observación (Fallo Detectado)**: Actualmente, los menús son estáticos y hardcodeados, contrario a la documentación.

-   **Flujos que Maneja**:
    -   La experiencia inicial del usuario.
    -   La visualización de las opciones de primer nivel.

-   **Flujos que NO Debe Manejar**:
    -   La ejecución de los flujos de conversación. Solo debe proporcionar los botones para iniciarlos.

---

### 5. Agente de Agenda (`calendar.py`, `agenda.py`, `aprobaciones.py`)

Gestiona toda la lógica relacionada con la programación, consulta y aprobación de eventos.

-   **Responsabilidades**:
    -   Interactuar con la API de Google Calendar.
    -   Diferenciar entre la agenda de trabajo y la agenda personal. El tiempo personal debe ser tratado como bloqueado e inamovible por defecto.
    -   Mostrar al administrador únicamente sus propios eventos.
    -   Gestionar el estado de las solicitudes de actividades (pendiente, aprobada, rechazada).
    -   Asegurar que las actividades rechazadas no vuelvan a aparecer como pendientes.

-   **Flujos que Maneja**:
    -   `view_agenda`
    -   `view_pending`
    -   `propose_activity`
    -   Aprobación y rechazo de eventos.

-   **Flujos que NO Debe Manejar**:
    -   Gestión de tareas (esa es responsabilidad del Agente de Tareas).
    -   Conversaciones no relacionadas con la agenda.

---

### 6. Agente de Impresión (`printer.py`)

Este agente gestiona la funcionalidad de impresión remota.

-   **Responsabilidades**:
    -   Recibir un archivo desde Telegram.
    -   Enviar el archivo como adjunto por correo electrónico (SMTP) a la dirección de la impresora.
    -   Consultar el estado de los trabajos de impresión mediante la revisión de una bandeja de entrada de correo (IMAP).
    -   Informar al usuario sobre el estado de la impresión.

-   **Flujos que Maneja**:
    -   Recepción de documentos.
    -   `/check_print_status`

-   **Flujos que NO Debe Manejar**:
    -   Cualquier interacción que no sea enviar un archivo o consultar el estado.

---

### 7. Agente de RAG y Ventas (`sales_rag.py`, `llm_engine.py`)

Es responsable del embudo de ventas para nuevos clientes, utilizando un modelo de lenguaje para generar respuestas personalizadas.

-   **Responsabilidades**:
    -   Ejecutar el flujo de conversación `client_sales_funnel`.
    -   Recuperar información relevante de la base de conocimiento (`services.json`).
    -   Construir un prompt enriquecido con el contexto del cliente y la información de los servicios.
    -   Invocar al modelo de lenguaje (OpenAI) para generar una propuesta de ventas.
    -   **Regla Obligatoria**: Si no se encuentra contexto relevante en la base de conocimiento, NO debe generar una respuesta genérica. Debe informar que no puede ayudar.

-   **Flujos que Maneja**:
    -   `client_sales_funnel`

-   **Flujos que NO Debe Manejar**:
    -   Conversaciones que no estén relacionadas con el proceso de ventas.

---

### 8. Agente de Transcripción (Whisper)

**Estado: Inexistente.** Este agente es requerido pero no está implementado.

-   **Responsabilidades Futuras**:
    -   Recibir un archivo de audio (mensaje de voz) de Telegram.
    -   Enviar el audio a la API de Whisper para su transcripción.
    -   Devolver el texto transcrito al `text_and_voice_handler` para que sea procesado por el Agente de Motor de Flujos.

-   **Flujos que Maneja**:
    -   La conversión de voz a texto dentro de cualquier flujo de conversación.

-   **Flujos que NO Debe Manejar**:
    -   La lógica de la conversación en sí.
