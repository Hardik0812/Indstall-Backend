# Indstall-Backend


````markdown
# Indstall-Backend

Django backend service for **Indstall**.  
This project uses **PostgreSQL** as the database and provides APIs for managing Indstall’s business workflows.

---

## 📦 Requirements

- Python 3.13
- PostgreSQL 13+
- pip (latest)
- virtualenv (optional but recommended)

---

## 🚀 Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-org/Indstall-backend.git
cd Indstall-backend
````

---

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate the virtual environment:

* **Linux / macOS**

  ```bash
  source venv/bin/activate
  ```
* **Windows (PowerShell)**

  ```bash
  venv\Scripts\activate
  ```

---

### 3. Create a `.env` file

In the project root, create a `.env` file:

```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key

# Database
DATABASE_NAME=indstall_db
DATABASE_USER=indstall_user
DATABASE_PASSWORD=yourpassword
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

---

### 4. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 5. Create PostgreSQL database

Login to PostgreSQL:

```bash
psql -U postgres
```

Run:

```sql
CREATE DATABASE Indstall_db;
CREATE USER Indstall_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE Indstall_db TO Indstall_user;
```

Update `.env` accordingly.

---

### 6. Run migrations

```bash
python manage.py migrate
```

---

### 7. Seed master data

```bash
python manage.py seed_master_data
```

This will populate the initial reference/master data required by the system.

---

### 8. Create a superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to set username, email, and password.

---

### 9. Start development server

```bash
python manage.py runserver
```

The app will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## ⚡ Useful Commands

* Run tests

  ```bash
  python manage.py test
  ```

* Check for migrations

  ```bash
  python manage.py makemigrations
  ```

* Apply migrations

  ```bash
  python manage.py migrate
  ```

* Load custom data (if needed)

  ```bash
  python manage.py loaddata <fixture_name>.json
  ```

---

## 🐳 (Optional) Docker Setup

If you prefer running everything via Docker:

```bash
docker-compose up --build
```

This will start:

* Django app
* PostgreSQL database

Make sure to update `.env` with the Docker database credentials.

---

## 📂 Project Structure (high-level)

```
Indstall-backend/
├── apps/                # Django apps
├── manage.py
├── requirements.txt
├── .env                 # Environment variables
├── docker-compose.yml   # (if using Docker)
└── README.md
```

---

## ✅ Done

