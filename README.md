# 🤍 Talía — Asistente Ejecutiva Inteligente

Talía es una asistente ejecutiva digital diseñada para centralizar, ordenar y coordinar la agenda, solicitudes y actividades de Marco. Actúa como un punto único de entrada para clientes, equipo y administradores, cuidando el tiempo, validando contexto y ejecutando automatizaciones mediante integraciones externas.

Talía no toma decisiones arbitrarias: consulta, valida, confirma y ejecuta.

---

## 🎯 Objetivo del Sistema

Talía existe para reducir fricción operativa y proteger el tiempo ejecutivo. Sus objetivos principales son:

* Centralizar todas las solicitudes de agenda y trabajo
* Validar disponibilidad real antes de comprometer tiempo
* Priorizar clientes sin romper compromisos existentes
* Delegar lógica compleja de negocio a n8n
* Mantener trazabilidad total mediante webhooks
* Permitir crecimiento modular y escalable

---

## 🧠 Personalidad y Actitud

Talía se comporta como una asistente ejecutiva profesional:

* Educada, clara y precisa
* Proactiva, pero nunca invasiva
* Siempre confirma antes de agendar
* No improvisa ni asume disponibilidad
* Comunica decisiones con calma y orden

No es informal, no es robótica y no es sassy. Su rol es ordenar el día, no interrumpirlo.

---

## 👥 Roles y Permisos

### Marco (Owner)

* Consulta agenda y pendientes
* Recibe resumen diario automático a las 7:00 AM
* Aprueba o rechaza solicitudes del equipo
* Puede interactuar desde su número privado
* Tiene prioridad absoluta en decisiones

### Clientes

* Solicitan citas de 30 minutos
* Solo ven horarios disponibles
* No acceden a la agenda completa

### Equipo Autorizado

* Puede proponer actividades de mayor duración
* Puede solicitar acciones operativas
* Requiere aprobación para agendar tiempo

### Administradores

* Ejecutan acciones sensibles
* Requieren doble validación
* Acceso a datos internos

---

## 🏗️ Arquitectura General

Talía está construida en capas claramente definidas:

1. Interfaz conversacional (Telegram / WhatsApp)
2. Cerebro central en Python
3. Automatización y reglas de negocio en n8n
4. Servicios externos (Google Calendar, APIs, IA)

Cada capa es desacoplada y se comunica mediante eventos y webhooks.

---

## 📁 Estructura del Proyecto

```text
talia-bot/
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── README.md
└── app/
    ├── main.py              # Cerebro del bot
    ├── config.py            # Configuración global
    ├── permissions.py       # Validación de roles
    ├── scheduler.py         # Resumen diario y recordatorios
    ├── webhook_client.py    # Comunicación con n8n
    ├── calendar.py          # Google Calendar
    ├── llm.py               # Respuestas inteligentes
    └── modules/
        ├── onboarding.py
        ├── agenda.py
        ├── citas.py
        ├── equipo.py
        ├── aprobaciones.py
        ├── servicios.py
        └── admin.py
```

---

## 🧠 Cerebro del Sistema (`main.py`)

`main.py` es el orquestador principal. Sus responsabilidades son:

* Recibir mensajes y callbacks de Telegram
* Identificar al usuario y su rol
* Mantener contexto de conversación
* Delegar acciones a los módulos
* Enviar y recibir eventos vía webhook

`main.py` no contiene lógica de negocio compleja; solo coordina.

---

## 🧩 Módulos Funcionales

Cada módulo ejecuta una responsabilidad clara:

* **onboarding.py**: bienvenida, `/start`, menú inicial
* **agenda.py**: consulta de agenda y pendientes
* **citas.py**: flujo de citas con clientes
* **equipo.py**: solicitudes del equipo
* **aprobaciones.py**: aceptar o rechazar solicitudes
* **servicios.py**: información y cotización de servicios
* **admin.py**: acciones administrativas

---

## 🔁 Flujo General de Datos

1. Usuario envía mensaje o presiona botón
2. Talía valida rol y contexto
3. Se ejecuta el módulo correspondiente
4. Si requiere lógica externa, se envía webhook a n8n
5. n8n responde con decisión
6. Talía comunica el resultado
7. Si aplica, se agenda en Google Calendar

---

## 📆 Gestión de Agenda

### Citas con Clientes

* Duración fija: 30 minutos
* Disponibilidad definida por n8n
* Confirmación explícita

### Actividades del Equipo

* Duración flexible
* Requieren aprobación de Marco
* Solo usuarios autorizados

---

## ⏰ Resumen Diario

Todos los días a las 7:00 AM, Talía envía a Marco:

* Agenda del día
* Pendientes activos
* Recordatorios importantes

---

## 🔌 Webhooks

Toda acción relevante genera o responde un webhook.

Ejemplo de solicitud:

```json
{
  "event": "request_activity",
  "from": "team",
  "duration_hours": 4,
  "description": "Grabación proyecto"
}
```

---

## 🔐 Variables de Entorno

```env
TELEGRAM_BOT_TOKEN=
OWNER_CHAT_ID=
ADMIN_CHAT_IDS=
TEAM_CHAT_IDS=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REFRESH_TOKEN=
N8N_WEBHOOK_URL=
OPENAI_API_KEY=
TIMEZONE=America/Mexico_City
```

---

## 🐳 Despliegue con Docker

```yaml
version: "3.9"
services:
  talia-bot:
    build: .
    container_name: talia-bot
    env_file:
      - .env
    restart: unless-stopped
```

---

## 🛠️ Guía de Desarrollo

1. Clonar el repositorio
2. Crear archivo `.env`
3. Configurar bot de Telegram
4. Configurar flujos en n8n
5. Conectar Google Calendar
6. Ejecutar con Docker Compose

---

## ✨ Filosofía Final

Talía no es un bot que responde mensajes.
Es un sistema de criterio, orden y respeto por el tiempo.

Si algo no está claro, pregunta.
Si algo invade agenda, protege.
Si algo importa, lo prioriza.
