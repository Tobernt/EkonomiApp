# Ekonomihantering

## 📦 Installation

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

2. **Run in development**

```bash
python app.py
```

3. **Run in production (with Gunicorn)**

```bash
gunicorn wsgi:app --bind 0.0.0.0:8000 --workers 4
```

4. **Docker-based deployment (optional)**

```bash
docker build -t ekonomihantering .
docker run -p 8000:8000 ekonomihantering
```

## 📁 File Descriptions

- `app.py`: Main Flask application.
- `wsgi.py`: Production entry point for WSGI servers like Gunicorn.
- `key.json`: Password key file (required).
- `budget.db`: SQLite database.
- `uploads/`, `static/`, `templates/`: Supporting folders.
