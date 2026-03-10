# WebSocket Real-Time Chat

## Обзор

Real-time чат между студентами и менторами через WebSocket.

## Возможности

- ✅ Двусторонний real-time обмен сообщениями
- ✅ JWT аутентификация для WebSocket
- ✅ Индикатор печати (typing indicator)
- ✅ Отметки о прочтении (read receipts)
- ✅ Онлайн статус пользователей
- ✅ Сохранение истории сообщений в БД
- ✅ Автоматическая обработка отключений

## WebSocket Endpoint

```
ws://localhost:8000/ws/chat?token=YOUR_JWT_TOKEN
```

### Подключение

```typescript
// Frontend example (TypeScript)
const token = localStorage.getItem('access_token');
const ws = new WebSocket(`ws://localhost:8000/ws/chat?token=${token}`);

ws.onopen = () => {
  console.log('✅ Connected to chat');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('📨 Received:', data);
  handleMessage(data);
};

ws.onerror = (error) => {
  console.error('❌ WebSocket error:', error);
};

ws.onclose = () => {
  console.log('🔌 Disconnected from chat');
};
```

## Message Types

### 1. Client → Server

#### Send Message
```json
{
  "type": "message",
  "recipient_id": 123,
  "content": "Hello! How are you?"
}
```

#### Typing Indicator
```json
{
  "type": "typing",
  "recipient_id": 123
}
```

#### Mark as Read
```json
{
  "type": "read",
  "message_id": 456
}
```

#### Keep-Alive Ping
```json
{
  "type": "ping"
}
```

### 2. Server → Client

#### Connection Established
```json
{
  "type": "connected",
  "user_id": 789,
  "username": "john_doe",
  "online_users": [1, 5, 7, 123]
}
```

#### Incoming Message
```json
{
  "type": "message",
  "id": 456,
  "sender_id": 123,
  "sender_username": "mentor_bob",
  "sender_avatar": "https://...",
  "recipient_id": 789,
  "content": "Hello! I'm good, thanks!",
  "timestamp": "2025-12-04T12:34:56"
}
```

#### Someone is Typing
```json
{
  "type": "typing",
  "user_id": 123,
  "username": "mentor_bob"
}
```

#### Message Read
```json
{
  "type": "read",
  "message_id": 456,
  "reader_id": 789
}
```

#### Pong (Keep-Alive)
```json
{
  "type": "pong"
}
```

#### Error
```json
{
  "type": "error",
  "message": "Missing recipient_id or content"
}
```

## Frontend Integration

### React Hook Example

```typescript
// hooks/useChat.ts
import { useEffect, useState, useRef } from 'react';

interface Message {
  id: number;
  sender_id: number;
  sender_username: string;
  content: string;
  timestamp: string;
}

export function useChat(token: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [onlineUsers, setOnlineUsers] = useState<number[]>([]);
  const [connected, setConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Подключение
    ws.current = new WebSocket(`ws://localhost:8000/ws/chat?token=${token}`);

    ws.current.onopen = () => {
      setConnected(true);
      console.log('✅ Chat connected');
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'connected') {
        setOnlineUsers(data.online_users);
      } else if (data.type === 'message') {
        setMessages((prev) => [...prev, data]);
      }
    };

    ws.current.onclose = () => {
      setConnected(false);
      console.log('🔌 Chat disconnected');
    };

    // Cleanup
    return () => {
      ws.current?.close();
    };
  }, [token]);

  const sendMessage = (recipientId: number, content: string) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        type: 'message',
        recipient_id: recipientId,
        content
      }));
    }
  };

  const sendTyping = (recipientId: number) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        type: 'typing',
        recipient_id: recipientId
      }));
    }
  };

  const markAsRead = (messageId: number) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        type: 'read',
        message_id: messageId
      }));
    }
  };

  return {
    messages,
    onlineUsers,
    connected,
    sendMessage,
    sendTyping,
    markAsRead
  };
}
```

### React Component Example

```tsx
// components/Chat.tsx
import { useState, useEffect } from 'react';
import { useChat } from '../hooks/useChat';

export function Chat({ token, recipientId }: Props) {
  const [input, setInput] = useState('');
  const { messages, connected, sendMessage, sendTyping } = useChat(token);

  const handleSend = () => {
    if (input.trim()) {
      sendMessage(recipientId, input);
      setInput('');
    }
  };

  const handleTyping = () => {
    sendTyping(recipientId);
  };

  return (
    <div className="chat-container">
      <div className="status">
        {connected ? '🟢 Online' : '🔴 Offline'}
      </div>

      <div className="messages">
        {messages.map((msg) => (
          <div key={msg.id} className="message">
            <strong>{msg.sender_username}:</strong> {msg.content}
            <span className="timestamp">{msg.timestamp}</span>
          </div>
        ))}
      </div>

      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyUp={handleTyping}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Type a message..."
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}
```

## REST API Endpoints

### Get Online Users

```http
GET /api/v1/ws/online-users
```

**Response:**
```json
{
  "online_users": [1, 5, 7, 123],
  "count": 4
}
```

## Architecture

### Connection Manager

```python
class ConnectionManager:
    def __init__(self):
        # user_id -> set of websockets
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """Подключение нового клиента"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

    async def send_personal_message(self, message: dict, user_id: int):
        """Отправка сообщения конкретному пользователю"""
        if user_id in self.active_connections:
            for websocket in self.active_connections[user_id]:
                await websocket.send_json(message)
```

### Message Flow

```
┌─────────┐              ┌─────────┐              ┌─────────┐
│ Client  │              │ Server  │              │   DB    │
│  (WS)   │              │  (WS)   │              │         │
└────┬────┘              └────┬────┘              └────┬────┘
     │                        │                        │
     │ {"type": "message"}    │                        │
     │───────────────────────>│                        │
     │                        │ Save message           │
     │                        │───────────────────────>│
     │                        │                        │
     │                        │<───────────────────────│
     │                        │ message_id             │
     │                        │                        │
     │ Confirmation           │                        │
     │<───────────────────────│                        │
     │                        │                        │
     │                        │ Send to recipient      │
     │                        │───────────────────────>│
     │                        │                        │
```

## Features

### 1. Typing Indicator

```typescript
let typingTimeout: NodeJS.Timeout;

input.addEventListener('input', () => {
  clearTimeout(typingTimeout);
  sendTyping(recipientId);
  
  typingTimeout = setTimeout(() => {
    // Stop typing indicator after 2s
  }, 2000);
});
```

### 2. Read Receipts

```typescript
// When message is visible on screen
useEffect(() => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const messageId = parseInt(entry.target.dataset.messageId);
        markAsRead(messageId);
      }
    });
  });

  messageElements.forEach((el) => observer.observe(el));
}, [messages]);
```

### 3. Reconnection Logic

```typescript
function connectWithRetry() {
  let retries = 0;
  const maxRetries = 5;

  function connect() {
    const ws = new WebSocket(`ws://localhost:8000/ws/chat?token=${token}`);

    ws.onclose = () => {
      if (retries < maxRetries) {
        retries++;
        const delay = Math.min(1000 * Math.pow(2, retries), 30000);
        console.log(`Reconnecting in ${delay}ms...`);
        setTimeout(connect, delay);
      }
    };

    ws.onopen = () => {
      retries = 0; // Reset on successful connection
    };
  }

  connect();
}
```

## Security

✅ **JWT Authentication:**
- Токен проверяется при подключении
- Невалидные токены отклоняются
- Refresh токены НЕ работают для WebSocket

✅ **Message Validation:**
- Content sanitization
- Recipient ID проверка
- Rate limiting (через middleware)

✅ **Connection Security:**
- WSS (WebSocket Secure) в production
- CORS настройки применяются

## Production Deployment

### Nginx Configuration

```nginx
map $http_upgrade $connection_upgrade {
    default upgrade;
    '' close;
}

server {
    listen 443 ssl;
    server_name api.mentorhub.com;

    location /ws/ {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
    }
}
```

### Frontend SSL

```typescript
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const ws = new WebSocket(`${protocol}//api.mentorhub.com/ws/chat?token=${token}`);
```

## Monitoring

### Logs

```bash
# Connection
✅ User 123 connected via WebSocket

# Message
📨 Message 456 from 123 to 789

# Disconnection
❌ User 123 disconnected from WebSocket
```

### Metrics

```python
# Prometheus metrics
websocket_connections_total = Counter('ws_connections_total')
websocket_messages_sent = Counter('ws_messages_sent')
websocket_active_connections = Gauge('ws_active_connections')
```

## Testing

### Manual Test

```bash
# Install wscat
npm install -g wscat

# Connect
wscat -c "ws://localhost:8000/ws/chat?token=YOUR_JWT_TOKEN"

# Send message
{"type": "message", "recipient_id": 2, "content": "Hello!"}

# Typing
{"type": "typing", "recipient_id": 2}

# Ping
{"type": "ping"}
```

### Pytest

```python
from fastapi.testclient import TestClient

def test_websocket_chat(client: TestClient):
    token = get_test_token()
    
    with client.websocket_connect(f"/ws/chat?token={token}") as ws:
        # Receive connection confirmation
        data = ws.receive_json()
        assert data["type"] == "connected"
        
        # Send message
        ws.send_json({
            "type": "message",
            "recipient_id": 2,
            "content": "Test"
        })
        
        # Receive confirmation
        data = ws.receive_json()
        assert data["type"] == "message"
        assert data["content"] == "Test"
```

## FAQ

**Q: Можно ли использовать с Socket.IO?**

A: Сейчас используется нативный WebSocket. Для Socket.IO используйте `python-socketio` библиотеку.

**Q: Как масштабировать на несколько серверов?**

A: Используйте Redis Pub/Sub для синхронизации:

```python
# При получении сообщения
await redis.publish('chat', json.dumps(message_data))

# В подписчике
async for message in redis.subscribe('chat'):
    await manager.broadcast(message)
```

**Q: Есть ли лимиты на сообщения?**

A: Да, через Rate Limiting middleware. По умолчанию 100 req/min.

**Q: Поддержка групповых чатов?**

A: Сейчас только 1-to-1. Для групп добавьте room_id вместо recipient_id.
