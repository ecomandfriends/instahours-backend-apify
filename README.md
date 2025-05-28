# InstaHours Backend (Debug con Apify)

Este backend usa Apify y añade `print()` para depurar la respuesta de la API.

- Verás la respuesta completa del intento de lanzar el actor en los logs de Render.
- Si no se puede extraer `run_id`, devuelve el JSON original para ayudarte a depurar.

### Build
```
pip install -r requirements.txt
```

### Start
```
python app.py
```
