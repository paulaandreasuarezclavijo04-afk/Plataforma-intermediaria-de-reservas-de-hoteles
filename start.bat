@echo off
cd C:\Users\Cristofer\Documents\PAULA\Universidad\WebServices\Plataforma intermediaria de reservas de hoteles
call .\venv\Scripts\activate.bat
python -m uvicorn main:app --reload