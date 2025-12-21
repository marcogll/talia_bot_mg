# 🤖 Talia Bot: Asistente Personal & Orquestador de Negocio

Talia no es un simple chatbot; es un Middleware de Inteligencia Artificial alojado en un VPS que orquesta las operaciones diarias de administración, logística y ventas. Actúa como el puente central entre usuarios en Telegram y servicios críticos como Vikunja (Gestión de Proyectos), Google Calendar y Hardware de Impresión remota.

---

## 🚀 Concepto Central: Enrutamiento por Identidad

La característica core de Talia es su capacidad de cambiar de personalidad y permisos dinámicamente basándose en el Telegram ID del usuario:

| Rol     | Icono | Descripción         | Permisos                                                                          |
| :------ | :---: | :------------------ | :-------------------------------------------------------------------------------- |
| **Admin** |  👑   | Dueño / Gerente     | God Mode: Gestión total de proyectos, bloqueos de calendario, generación de identidad NFC e impresión. |
| **Crew**  |  👷   | Equipo Operativo    | Limitado: Solicitud de agenda (validada), asignación de tareas, impresión de documentos. |
| **Cliente** |  👤   | Usuario Público     | Ventas: Embudo de captación, consulta de servicios (RAG) y agendamiento comercial. |

---

## 🛠️ Arquitectura Técnica

El sistema sigue un flujo modular:

1.  **Input**: Telegram (Texto o Audio).
2.  **STT**: Whisper (Conversión de Audio a Texto).
3.  **Router**: Verificación de ID contra la base de datos de usuarios.
4.  **Cerebro (LLM)**: OpenAI (Fase 1) / Google Gemini (Fase 2).
5.  **Tools**:
    *   **Vikunja API**: Lectura/Escritura de tareas con filtrado de privacidad.
    *   **Google Calendar API**: Gestión de tiempos y reglas de disponibilidad.
    *   **SMTP/IMAP**: Comunicación bidireccional con impresoras.
    *   **NFC Gen**: Codificación Base64 para tags físicos.

---

## 📋 Flujos de Trabajo (Features)

### 1. 👑 Gestión Admin (Proyectos & Identidad)

*   **Proyectos (Vikunja)**:
    *   Resumen inteligente de estatus de proyectos.
    *   Comandos naturales: *"Marca el proyecto de web como terminado y comenta que se envió factura"*.
*   **Wizard de Identidad (NFC)**:
    *   Flujo paso a paso para dar de alta colaboradores.
    *   Genera JSON de registro y String Base64 listo para escribir en Tags NFC.
    *   Inputs: Nombre, ID Empleado, Sucursal (Botones), Telegram ID.

### 2. 👷 Gestión Crew (Agenda & Tareas)

*   **Solicitud de Tiempo (Wizard)**:
    *   Solicita espacios de 1 a 4 horas.
    *   **Reglas de Negocio**:
        *   No permite fechas > 3 meses a futuro.
        *   **Gatekeeper**: Verifica Google Calendar. Si hay evento "Privado" del Admin, rechaza automáticamente.
*   **Modo Buzón (Vikunja)**:
    *   Crea tareas asignadas al Admin.
    *   **Privacidad**: Solo pueden consultar el estatus de tareas creadas por ellos mismos.

### 3. 🖨️ Sistema de Impresión Remota (Print Loop)

*   Permite enviar archivos desde Telegram a la impresora física de la oficina.
*   **Envío (SMTP)**: El bot envía el documento a un correo designado.
*   **Tracking**: El asunto del correo lleva un hash único: `PJ:{uuid}#TID:{telegram_id}`.
*   **Confirmación (IMAP Listener)**: Un proceso en background escucha la respuesta de la impresora y notifica al usuario en Telegram.

### 4. 👤 Ventas Automáticas (RAG)

*   Identifica usuarios nuevos (no registrados en la DB).
*   Captura datos (Lead Magnet).
*   Analiza ideas de clientes usando `servicios.json` (Base de conocimiento).
*   Ofrece citas de ventas mediante link de Calendly.

---

## ⚙️ Instalación y Configuración

### Prerrequisitos

*   Python 3.10+
*   Cuenta de Telegram Bot (@BotFather)
*   Instancia de Vikunja (Self-hosted)
*   Cuenta de Servicio Google Cloud (Calendar API)
*   Servidor de Correo (SMTP/IMAP)

### 1. Clonar y Entorno Virtual

```bash
git clone https://github.com/marcogll/talia_bot_mg.git
cd talia_bot_mg
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Variables de Entorno (`.env`)

Crea un archivo `.env` en la raíz con la siguiente estructura:

```env
# --- TELEGRAM & SECURITY ---
TELEGRAM_BOT_TOKEN=tu_token_telegram
ADMIN_ID=tu_telegram_id

# --- AI CORE ---
OPENAI_API_KEY=sk-...

# --- INTEGRACIONES ---
VIKUNJA_API_URL=https://tuservidor.com/api/v1
VIKUNJA_TOKEN=tu_token_vikunja
GOOGLE_CREDENTIALS_PATH=./data/credentials.json

# --- PRINT SERVICE ---
SMTP_SERVER=smtp.hostinger.com
SMTP_PORT=465
SMTP_USER=print.service@vanityexperience.mx
SMTP_PASS=tu_password_seguro
IMAP_SERVER=imap.hostinger.com
```

### 3. Estructura de Datos

Asegúrate de tener los archivos base en `talia_bot/data/`:
*   `servicios.json`: Catálogo de servicios para el RAG de ventas.
*   `credentials.json`: Credenciales de Google Cloud.
*   `users.db`: Base de datos SQLite.

---

## 📂 Estructura del Proyecto

```text
talia_bot_mg/
├── talia_bot/
│   ├── main.py              # Entry Point y Router de Identidad
│   ├── db.py                # Gestión de la base de datos
│   ├── config.py            # Carga de variables de entorno
│   ├── modules/
│   │   ├── identity.py      # Lógica de Roles y Permisos
│   │   ├── llm_engine.py    # Cliente OpenAI/Gemini
│   │   ├── vikunja.py       # API Manager para Tareas
│   │   ├── calendar.py      # Google Calendar Logic & Rules
│   │   ├── printer.py       # SMTP/IMAP Loop
│   │   └── sales_rag.py     # Lógica de Ventas y Servicios
│   └── data/
│       ├── servicios.json   # Base de conocimiento
│       ├── credentials.json # Credenciales de Google
│       └── users.db         # Base de datos de usuarios
├── .env.example             # Plantilla de variables de entorno
├── requirements.txt         # Dependencias
├── Dockerfile               # Configuración del contenedor
└── docker-compose.yml       # Orquestador de Docker
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
