# Plan de Corrección del Bot

Este plan detalla los pasos necesarios para que el bot sea funcional, responda a los botones y no se bloquee.

## 1. Corrección de Bloqueos (Agenda)
- [ ] **Hacer asíncronas las llamadas a Google Calendar**: En `app/main.py`, usar `asyncio.to_thread` o un ejecutor para las funciones que bloquean el hilo principal (como `get_agenda` que llama a `get_events`).
- [ ] **Optimizar `button_dispatcher`**: Asegurar que el despachador de botones maneje correctamente tanto funciones síncronas como asíncronas sin bloquearse.

## 2. Corrección de Botones y Flujos (ConversationHandlers)
- [ ] **Vincular botones a conversaciones**: Modificar `app/modules/create_tag.py` y otros módulos para que sus `ConversationHandler` tengan como punto de entrada (`entry_points`) el `CallbackQueryHandler` del botón correspondiente.
- [ ] **Limpiar `button_dispatcher`**: Eliminar las llamadas manuales a inicios de conversación dentro del despachador, dejando que los `ConversationHandler` se encarguen de capturar sus propios botones.

## 3. Robustez y Errores
- [ ] **Manejador Global de Errores**: Añadir `application.add_error_handler` en `app/main.py` para capturar cualquier fallo y loguearlo, evitando que el bot se quede "pensando" sin dar respuesta.
- [ ] **Verificación de Roles**: Asegurar que `onboarding.py` siempre entregue el menú correcto y que los IDs en `.env` estén bien cargados.

## 4. Gestión de Procesos
- [ ] **Evitar Conflictos**: Implementar una verificación al inicio de `main.py` para asegurar que no haya otra instancia del bot corriendo con el mismo token.

## 5. Verificación Final
- [ ] Probar cada botón del menú Admin: Agenda, Pendientes, Crear Tag, Más opciones.
- [ ] Verificar que el bot responda "No hay eventos" o la lista de eventos sin colgarse.
