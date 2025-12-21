# Plan de Reparación vs. Refactorización

Este documento distingue entre las reparaciones críticas ya implementadas y propone un plan de refactorización incremental para estabilizar y mejorar la arquitectura del sistema Talia Bot a largo plazo.

---

### Parte 1: Reparaciones Críticas (Ya Implementadas)

Las siguientes acciones se tomaron como medidas de reparación inmediata para solucionar los problemas más urgentes y restaurar la funcionalidad básica.

1.  **Visibilidad de Flujos de Admin**:
    -   **Fix**: Se modificó `onboarding.py` para generar el menú de administrador de forma dinámica, leyendo los flujos disponibles del `FlowEngine`. Se añadieron las claves `name` y `trigger_button` a los archivos JSON de los flujos para permitir esto.
    -   **Impacto**: Los administradores ahora pueden ver y acceder a todos los flujos que tienen asignados, incluyendo "Capturar Idea" e "Imprimir Archivo".

2.  **Lógica de Agenda y Privacidad**:
    -   **Fix**: Se actualizó `agenda.py` para que utilice las variables de entorno `WORK_GOOGLE_CALENDAR_ID` y `PERSONAL_GOOGLE_CALENDAR_ID`.
    -   **Impacto**: El bot ahora muestra correctamente solo los eventos de la agenda de trabajo del administrador, mientras que trata el tiempo en la agenda personal como bloqueado, protegiendo la privacidad y asegurando que la disponibilidad sea precisa.

3.  **Implementación de Transcripción (Whisper)**:
    -   **Fix**: Se añadió una función `transcribe_audio` a `llm_engine.py` y se integró en el `text_and_voice_handler` de `main.py`.
    -   **Impacto**: El bot ya no ignora los mensajes de voz. Ahora puede transcribirlos y usarlos como entrada para los flujos de conversación, sentando las bases para una interacción multimodal completa.

4.  **Guardarraíl del RAG de Ventas**:
    -   **Fix**: Se eliminó la lógica de fallback en `sales_rag.py`. Si no se encuentran servicios relevantes para la consulta de un cliente, el agente se detiene.
    -   **Impacto**: El bot ya no genera respuestas de ventas genéricas o irrelevantes. Ahora cumple la regla obligatoria de "sin contexto, no hay respuesta", mejorando la calidad y la fiabilidad de sus interacciones con clientes.

---

### Parte 2: Plan de Refactorización Incremental (Propuesta)

Las reparaciones anteriores han estabilizado el sistema, pero la auditoría reveló debilidades arquitectónicas que deben abordarse para asegurar la mantenibilidad y escalabilidad futuras. Se propone el siguiente plan incremental.

#### Incremento 1: Gestión de Estado y Base de Datos

-   **Problema**: La lógica de la base de datos está dispersa. La persistencia del estado de las aprobaciones es frágil, lo que causa que actividades rechazadas reaparezcan.
-   **Propuesta**:
    1.  **Centralizar Acceso a DB**: Crear un gestor de contexto en `db.py` para manejar las conexiones y cursores, asegurando que las conexiones siempre se cierren correctamente.
    2.  **Refactorizar Aprobaciones**: Rediseñar la lógica en `aprobaciones.py`. Introducir una tabla `activity_proposals` en la base de datos con un campo `status` (ej. `pending`, `approved`, `rejected`).
    3.  **Implementar DAO (Data Access Object)**: Crear clases o funciones específicas para interactuar con cada tabla (`users`, `conversations`, `activity_proposals`), en lugar de escribir consultas SQL directamente en la lógica de negocio.
-   **Riesgos**: Mínimos. Este cambio es interno y no debería afectar la experiencia del usuario, pero requiere cuidado para no corromper la base de datos.
-   **Beneficios**: Solucionará permanentemente el bug de las actividades rechazadas. Hará que el manejo de la base de datos sea más robusto y fácil de mantener.

#### Incremento 2: Abstracción de APIs Externas (Fachada)

-   **Problema**: Las llamadas directas a APIs externas (Google, OpenAI, Vikunja) están mezcladas con la lógica de negocio, lo que hace que el código sea difícil de probar y de cambiar.
-   **Propuesta**:
    1.  **Crear un Módulo `clients`**: Dentro de `modules`, crear un nuevo directorio `clients`.
    2.  **Implementar Clientes API**: Mover toda la lógica de interacción directa con las APIs a clases dedicadas dentro de este nuevo módulo (ej. `google_calendar_client.py`, `openai_client.py`). Estas clases manejarán la autenticación, las solicitudes y el formato de las respuestas.
    3.  **Actualizar Módulos de Negocio**: Modificar los módulos como `agenda.py` y `llm_engine.py` para que usen estos clientes, en lugar de hacer llamadas directas.
-   **Riesgos**: Moderados. Requiere refactorizar una parte significativa del código. Se deben realizar pruebas exhaustivas para asegurar que las integraciones no se rompan.
-   **Beneficios**: Desacopla la lógica de negocio de las implementaciones de las API. Permite cambiar de proveedor (ej. de OpenAI a Gemini) con un impacto mínimo. Facilita enormemente las pruebas unitarias al permitir "mockear" los clientes API.

#### Incremento 3: Sistema de Routing y Comandos Explícito

-   **Problema**: El `button_dispatcher` en `main.py` es un monolito que mezcla lógica de flujos, acciones simples y lógica de aprobación. Es difícil de seguir y propenso a errores a medida que se añaden más botones. El comando `/abracadabra` no funciona porque no hay un sistema claro para registrar comandos "secretos" o de un solo uso.
-   **Propuesta**:
    1.  **Registro de Comandos**: Crear un patrón de registro explícito. Cada módulo podría tener una función `register_handlers(application)` que se llama desde `main.py`.
    2.  **Separar Despachador**: Dividir el `button_dispatcher` en funciones más pequeñas y específicas. Una podría manejar los callbacks de los flujos, otra los de acciones simples, etc.
    3.  **Implementar `/abracadabra`**: Usando el nuevo sistema de registro, crear un comando simple en `admin.py` para la funcionalidad de `/abracadabra` y registrarlo en `main.py`.
-   **Riesgos**: Bajos. Los cambios son principalmente organizativos.
-   **Beneficios**: Mejora radicalmente la legibilidad y mantenibilidad del `main.py`. Crea un sistema claro y escalable para añadir nuevos comandos y botones.

---

### Orden Recomendado

Se recomienda seguir el orden de los incrementos propuestos:

1.  **Gestión de Estado y DB**: Es la base. Un manejo de datos sólido es fundamental para todo lo demás.
2.  **Abstracción de APIs**: Abordar esto primero hará que el siguiente paso sea más limpio.
3.  **Sistema de Routing**: Con la lógica de negocio y los datos bien estructurados, refactorizar el enrutamiento será mucho más sencillo.
