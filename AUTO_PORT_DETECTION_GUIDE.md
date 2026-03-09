# Автоматическое определение портов

## Проблема

Ошибка `[Errno 98] Address already in use` возникает, когда:
- Несколько процессов пытаются использовать один порт
- Предыдущий процесс не освободил порт
- Supervisord и ручной запуск конфликтуют

## Решение

### 1. Python модуль (port_finder.py)

```python
from port_finder import find_free_port, get_port_with_fallback, get_port_from_env

# Найти свободный порт начиная с 8000
port = find_free_port(start_port=8000)
print(f"Свободный порт: {port}")

# Получить порт с fallback (если 8000 занят, найдёт следующий)
port = get_port_with_fallback(preferred_port=8000)

# Получить порт из переменной окружения PORT
port = get_port_from_env("PORT", default=8000)
```

### 2. В main.py

```python
# Добавить в начало main.py
import socket

def is_port_available(port: int, host: str = "0.0.0.0") -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
            return True
    except OSError:
        return False

def find_free_port(start_port: int = 8000) -> int:
    for port in range(start_port, start_port + 100):
        if is_port_available(port):
            return port
    raise RuntimeError("No free port found")

# При запуске
if __name__ == "__main__":
    import uvicorn
    
    # Автоматически определяем порт
    preferred_port = int(os.environ.get("PORT", 8000))
    port = preferred_port if is_port_available(preferred_port) else find_free_port(preferred_port + 1)
    
    uvicorn.run(app, host="0.0.0.0", port=port)
```

### 3. В shell скрипте (start.sh)

```bash
#!/bin/bash

# Функция поиска свободного порта
find_free_port() {
    local start_port=$1
    local port=$start_port
    
    while [ $port -lt $((start_port + 100)) ]; do
        if ! lsof -i :$port > /dev/null 2>&1; then
            echo $port
            return 0
        fi
        port=$((port + 1))
    done
    return 1
}

# Определяем порт
if [ -n "$PORT" ]; then
    PREFERRED_PORT=$PORT
else
    PREFERRED_PORT=8000
fi

# Ищем свободный порт
if lsof -i :$PREFERRED_PORT > /dev/null 2>&1; then
    BACKEND_PORT=$(find_free_port $((PREFERRED_PORT + 1)))
else
    BACKEND_PORT=$PREFERRED_PORT
fi

echo "Using port: $BACKEND_PORT"
export PORT=$BACKEND_PORT
```

## Файлы

| Файл | Описание |
|------|----------|
| `port_finder.py` | Python модуль для поиска портов |
| `main_auto_port.py` | Пример main.py с авто-определением |
| `start_auto_port.sh` | Пример start.sh с авто-определением |

## CLI утилита

```bash
# Проверить порт
python port_finder.py --check 8000

# Найти свободный порт с 8000
python port_finder.py --start 8000

# Получить порт из переменной окружения
PORT=9000 python port_finder.py --env PORT
```

## Облачные платформы

Большинство облачных платформ (Render, Railway, Heroku) устанавливают переменную `PORT`:

```bash
# Render/Railway/Heroku автоматически устанавливают PORT
# Наш код автоматически использует его и fallback при необходимости
```

## Диагностика

```bash
# Показать все занятые порты
netstat -tlnp

# Показать процесс на порту
lsof -i :8000

# Убить процесс на порту
fuser -k 8000/tcp
```
