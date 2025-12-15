# Talía Development Tasks

This file tracks the development tasks for the Talía project.

## Phase 1: Project Scaffolding

- [x] Create `tasks.md` to track project development.
- [x] Create the basic directory structure (`app`, `app/modules`).
- [x] Create placeholder files in the root directory (`docker-compose.yml`, `Dockerfile`, `.env.example`).
- [x] Create placeholder files in the `app` directory.
- [x] Create placeholder files in the `app/modules` directory.

## Phase 2: Core Logic Implementation

- [x] Implement `main.py` as the central orchestrator.
- [x] Implement `config.py` to handle environment variables.
- [x] Implement `permissions.py` for role-based access control.
- [x] Implement `webhook_client.py` for n8n communication.

## Phase 3: Module Implementation

- [x] Implement `onboarding.py` module.
- [x] Implement `agenda.py` module.
- [x] Implement `citas.py` module.
- [x] Implement `equipo.py` module.
- [x] Implement `aprobaciones.py` module.
- [ ] Implement `servicios.py` module.
- [ ] Implement `admin.py` module.

## Phase 4: Integrations

- [ ] Implement `calendar.py` for Google Calendar integration.
- [ ] Implement `llm.py` for AI-powered responses.
- [ ] Implement `scheduler.py` for daily summaries.

## Log

### 2024-05-22

- Created `tasks.md` to begin tracking development.
- Completed initial project scaffolding.
- Implemented the core logic for the bot, including the central orchestrator, permissions, and onboarding.
- Implemented the `agenda` and `citas` modules.
- Implemented the conversational flow for proposing and approving activities.
