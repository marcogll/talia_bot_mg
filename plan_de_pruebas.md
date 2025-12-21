# Plan de Pruebas: Estabilización de Talia Bot

Este documento describe el plan de pruebas paso a paso para verificar la correcta funcionalidad del sistema Talia Bot después de la fase de reparación.

---

### 1. Configuración y Entorno

-   **Qué se prueba**: La correcta carga de las variables de entorno.
-   **Pasos a ejecutar**:
    1.  Asegurarse de que el archivo `.env` existe y contiene todas las variables definidas in `.env.example`.
    2.  Prestar especial atención a `WORK_GOOGLE_CALENDAR_ID` y `PERSONAL_GOOGLE_CALENDAR_ID`.
    3.  Iniciar el bot.
-   **Resultado esperado**: El bot debe iniciarse sin errores relacionados con variables de entorno faltantes. Los logs de inicio deben mostrar que la aplicación se ha iniciado correctamente.
-   **Qué indica fallo**: Un crash al inicio, o errores en los logs indicando que una variable de entorno `None` o vacía está siendo utilizada donde no debería.

---

### 2. Routing por Rol de Usuario

-   **Qué se prueba**: Que cada rol de usuario (`admin`, `crew`, `client`) vea el menú correcto y solo las opciones que le corresponden.
-   **Pasos a ejecutar**:
    1.  **Como Admin**: Enviar el comando `/start`.
    2.  **Como Crew**: Enviar el comando `/start`.
    3.  **Como Cliente**: Enviar el comando `/start`.
-   **Resultado esperado**:
    -   **Admin**: Debe ver el menú de administrador, que incluirá las opciones "Revisar Pendientes", "Agenda", y las nuevas opciones reparadas ("Imprimir Archivo", "Capturar Idea").
    -   **Crew**: Debe ver el menú de equipo con "Proponer actividad" y "Ver estatus de solicitudes".
    -   **Cliente**: Debe ver el menú de cliente con "Agendar una cita" y "Información de servicios".
-   **Qué indica fallo**: Cualquier rol viendo un menú que no le corresponde, o la ausencia de las opciones esperadas.

---

### 3. Flujos de Administrador Faltantes

-   **Qué se prueba**: La visibilidad y funcionalidad de los flujos de "Imprimir Archivo" y "Capturar Idea".
-   **Pasos a ejecutar**:
    1.  **Como Admin**: Presionar el botón "Imprimir Archivo" (o su equivalente) en el menú.
    2.  **Como Admin**: Presionar el botón "Capturar Idea" en el menú.
-   **Resultado esperado**:
    -   Al presionar "Imprimir Archivo", el bot debe iniciar el flujo de impresión, pidiendo al usuario que envíe un documento.
    -   Al presionar "Capturar Idea", el bot debe iniciar el flujo de captura de ideas, haciendo la primera pregunta definida en `admin_idea_capture.json`.
-   **Qué indica fallo**: Que los botones no existan en el menú, o que al presionarlos no se inicie el flujo de conversación correspondiente.

---

### 4. Lógica de Agenda y Calendario

-   **Qué se prueba**: La correcta separación de agendas y el tratamiento del tiempo personal.
-   **Pasos a ejecutar**:
    1.  **Preparación**: Crear un evento en el `PERSONAL_GOOGLE_CALENDAR_ID` que dure todo el día de hoy, llamado "Día Personal". Crear otro evento en el `WORK_GOOGLE_CALENDAR_ID` para hoy a las 3 PM, llamado "Reunión de Equipo".
    2.  **Como Admin**: Presionar el botón "Agenda" en el menú.
-   **Resultado esperado**: El bot debe responder mostrando *únicamente* el evento "Reunión de Equipo" a las 3 PM. El "Día Personal" no debe ser visible, pero el tiempo que ocupa debe ser tratado como no disponible si se intentara agendar algo.
-   **Qué indica fallo**: La agenda muestra el evento "Día Personal", o muestra eventos de otros calendarios que no son el de trabajo del admin.

---

### 5. Persistencia en Rechazo de Actividades

-   **Qué se prueba**: Que una actividad propuesta por el equipo y rechazada por el admin no vuelva a aparecer como pendiente.
-   **Pasos a ejecutar**:
    1.  **Como Crew**: Iniciar el flujo "Proponer actividad" y proponer una actividad para mañana.
    2.  **Como Admin**: Ir a "Revisar Pendientes". Ver la actividad propuesta.
    3.  **Como Admin**: Presionar el botón para "Rechazar" la actividad.
    4.  **Como Admin**: Volver a presionar "Revisar Pendientes".
-   **Resultado esperado**: La segunda vez que se revisan los pendientes, la lista debe estar vacía o no debe incluir la actividad que fue rechazada.
-   **Qué indica fallo**: La actividad rechazada sigue apareciendo en la lista de pendientes.

---

### 6. RAG (Retrieval-Augmented Generation) y Whisper

-   **Qué se prueba**: La regla de negocio "sin contexto, no hay respuesta" del RAG y la nueva funcionalidad de transcripción de voz.
-   **Pasos a ejecutar**:
    1.  **RAG**:
        a. **Como Cliente**: Iniciar el flujo de ventas.
        b. Cuando se pregunte por la idea de proyecto, responder con un texto que no contenga ninguna palabra clave relevante de `services.json` (ej: "quiero construir una casa para mi perro").
    2.  **Whisper**:
        a. **Como Cliente**: Iniciar el flujo de ventas.
        b. Cuando se pregunte por el nombre, responder con un mensaje de voz diciendo tu nombre.
-   **Resultado esperado**:
    -   **RAG**: El bot debe responder con un mensaje indicando que no puede generar una propuesta con esa información, en lugar de dar una respuesta genérica.
    -   **Whisper**: El bot debe procesar el mensaje de voz, transcribirlo, y continuar el flujo usando el nombre transcrito como si se hubiera escrito.
-   **Qué indica fallo**:
    -   **RAG**: El bot da un pitch de ventas genérico o incorrecto.
    -   **Whisper**: El bot responde con el mensaje "Voice message received (transcription not implemented yet)" o un error.

---

### 7. Comandos Slash

-   **Qué se prueba**: La funcionalidad de los comandos básicos, incluyendo el inexistente `/abracadabra`.
-   **Pasos a ejecutar**:
    1.  Enviar el comando `/start`.
    2.  Iniciar una conversación y luego enviar `/reset`.
    3.  Enviar un comando inexistente como `/abracadabra`.
-   **Resultado esperado**:
    -   `/start`: Muestra el menú de bienvenida correspondiente al rol.
    -   `/reset`: El bot responde "Conversación reiniciada" y borra el estado actual del flujo.
    -   `/abracadabra`: Telegram o el bot deben indicar que el comando no es reconocido.
-   **Qué indica fallo**: Que los comandos `/start` o `/reset` no funcionen como se espera. (No se espera que `/abracadabra` funcione, por lo que un fallo sería que *hiciera* algo).
