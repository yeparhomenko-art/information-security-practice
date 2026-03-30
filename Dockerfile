FROM python:3.11-slim
 
WORKDIR /app_code
 
# Копіюємо залежності окремим шаром (кешування)
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt
 
# Копіюємо весь код
COPY . .
 
# Створюємо директорію для бази даних
RUN mkdir -p /app_code/data
 
EXPOSE 3010

# Запускаємо сервер
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3010", "--reload"]