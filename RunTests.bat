call venv\Scripts\activate
prisma generate
pytest -v --tb=short
pause