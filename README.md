# InstaHours Backend (versión blindada)

Versión definitiva con manejo de errores mejorado y protección contra cuelgues.

## Características:
- Captura errores de red (Apify caído, token inválido, etc).
- Retorna mensajes útiles y controlados.
- Imprime en logs cada paso clave para ver en Render.

## Cómo usar:
- Subir a GitHub
- Crear Web Service en Render
- Build: pip install -r requirements.txt
- Start: python app.py

Luego abre /analyze/{usuario} para ver el resultado.
