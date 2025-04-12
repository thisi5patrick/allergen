[![CI Status](https://github.com/thisi5patrick/allergen/actions/workflows/ci.yml)](https://github.com/thisi5patrick/allergen/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/thisi5patrick/allergen/graph/badge.svg?token=N0TJKV66JJ)](https://codecov.io/gh/thisi5patrick/allergen)

# Allergies Tracker

A web application built with Django and HTMX for tracking daily allergies and symptoms. 
Users can select symptoms, rate their intensity for a given day, and view their history via a calendar interface. 
This project utilizes Docker for containerized development and deployment, and `uv` for fast Python package management.


## Installation & Running (Docker Recommended)

This is the recommended method for development and consistency.

1. Clone the repository:
```shell
git clone git@github.com:thisi5patrick/allergen.git
cd allergen
```

2. Create `.env` file: Create a file named `.env` in the project root. Copy the contents from `.env.example` or create it with the following essential variables:
```shell
DEBUG=True

# Database Configuration (adjust if needed, matches docker-compose defaults)
DATABASE_URL=postgres://postgres:postgres@postgres:5432/postgres
# Or individual variables:
# POSTGRES_DB=postgres
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=postgres
# POSTGRES_HOST=postgres # Service name from docker-compose
# POSTGRES_PORT=5432

# Port mapping for PostgreSQL container (must match docker-compose)
# Allows connecting from host machine if needed, e.g. 5433:5432
POSTGRES_PORT=5432

# Google reCAPTCHA Keys (Get from https://www.google.com/recaptcha/admin)
# Use v2 Checkbox keys. The test keys below ONLY work for local testing.
RECAPTCHA_PUBLIC_KEY='6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
RECAPTCHA_PRIVATE_KEY='6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'
```
3. Build Docker Images:
```shell
docker compose up
```

4. Run Database Migrations
```shell
docker compose run --rm web python manage.py migrate
```

5. Create Superuser (Optional):
```shell
docker compose run --rm web python manage.py createsuperuser
```

6. Start Services:
```shell
docker compose up
```

7. Access Application: Open your browser to http://localhost:8000

## Installation & Running (Local)

1. Clone: As above.

2. Create .env file: As above, but ensure POSTGRES_HOST is set to localhost or the address of your manually running PostgreSQL instance.

3. Install Python: Ensure you have Python >=3.13 installed.

4. Install UV: Follow instructions at Astral UV Documentation.

5. Create Virtual Environment:
```shell
uv venv .venv
source .venv/bin/activate # Or .venv\Scripts\activate on Windows
```

6. Install Dependencies: Install project and development dependencies
```shell
uv sync --dev
```

7. Setup Database: Ensure PostgreSQL >= 16 is installed, running, and configured according to your .env file (create the user and database if needed).

8. Apply Migrations:
```shell
python manage.py migrate
```

9. Create Superuser (Optional):
```shell
python manage.py createsuperuser
```

10. Run Server:
```shell
python manage.py runserver
```

Usage:

1. Access: Navigate to http://localhost:8000.
2. Register/Login: Use the authentication system. reCAPTCHA will be active on relevant forms.
3. Dashboard: View the calendar and symptom tracking interface.
4. Navigate Calendar: Use arrows to change months, click days to load data.
5. Track Symptoms: Click symptom buttons to toggle selection. Click intensity numbers (1-10) to save/update.


## Testing & Code Quality

This project uses several tools to ensure code quality and correctness.

- Pre-commit: Automatically runs checks before commits. Install hooks with pre-commit install. You can run checks manually:
```shell
pre-commit run --all-files
```

- Testing Framework: pytest with pytest-django.
```shell
pytest # Or `uv run pytest`
```

- Test Data: factory-boy is used for generating model instances in tests.
- Test Coverage: coverage measures test coverage. Run tests with coverage and view the report:
```shell
coverage run -m pytest
coverage report
coverage html # For an HTML report in htmlcov/
```

- Linting/Formatting: Ruff checks for a wide range of issues.
```shell
ruff check .
ruff format .
```

- Type Checking: mypy with django-stubs performs static type analysis
```shell
mypy .
```

- Template Linting: djLint checks Django templates
```shell
djlint --check .
djlint --reformat .
```

## Contributing

Contributions are welcome! 
Please fork the repository, create a feature branch, and submit a pull request. 
Ensure your changes include tests and pass all quality checks (linting, type checking).
