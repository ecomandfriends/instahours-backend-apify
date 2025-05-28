# InstaHours Backend (Final con actor válido de Apify)

Este backend utiliza el actor público y actualizado `apify/instagram-scraper`.

### 🚀 Instrucciones

1. Conecta este backend en Render como Web Service.
2. Verifica que el token de Apify es válido.
3. Usa el endpoint:

```
/analyze/USERNAME
```

y obtendrás la frecuencia por hora de las últimas publicaciones de la cuenta indicada.

### ⚙️ Comandos Render

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
python app.py
```
