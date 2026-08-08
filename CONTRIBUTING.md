# Guía de Contribución (CONTRIBUTING.md)

¡Gracias por tu interés en contribuir al **Gateway Actas de Entrega**!

## Estándares de Commits
Este proyecto utiliza la convención de [Conventional Commits](https://www.conventionalcommits.org/es/v1.0.0/). Todos los mensajes de commit deben tener la siguiente estructura:

```
<tipo>[ámbito opcional]: <descripción>
```

**Tipos permitidos:**
- `feat`: Un nuevo endpoint o soporte para una nueva plataforma de mensajería.
- `fix`: Una corrección en el parseo de webhooks o errores de API.
- `docs`: Cambios en este README o documentación de la API.
- `style`: Formateo de código (PEP 8).
- `refactor`: Limpieza o reestructuración en `app/services/` o `app/api/`.
- `test`: Añadir tests unitarios.

## Convenciones de Ramas
- `main` / `master`: Rama estable que se despliega automáticamente a Cloud Run.
- `feat/nueva-red-social`: Para añadir soporte a nuevos canales (ej. Slack, Discord).
- `fix/error-parseo-whatsapp`: Para arreglos específicos.

## Cómo hacer un Pull Request (PR)
1. **Crea una rama** en el repositorio a partir de `main`.
2. **Desarrolla tus cambios** asegurándote de no exponer variables de entorno en el código.
3. **Pasa las pruebas locales** usando `pytest` si hay tests configurados.
4. **Haz commit y push** de tus cambios usando los estándares.
5. **Abre el Pull Request** explicando claramente si el cambio requiere una actualización en la configuración de la Service Account o de los Webhooks en Meta/Telegram.
