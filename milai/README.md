# Milai Bot WebSocket API Documentation

## WebSocket Endpoint

The WebSocket endpoint is available at `/chat` and can be used for real-time chat interactions.

### Connecting

1. Connect to the WebSocket endpoint:
   ```
   ws://<server-address>/chat
   ```

2. Send messages in JSON format:
   ```json
   {
     "query": "Your message here",
     "session_id": "unique-session-id"
   }
   ```

### Message Format

#### Client to Server
- Must be valid JSON
- Required fields:
  - `query`: The user's message/query
  - `session_id`: Unique session identifier for maintaining chat history

Example:
```json
{
  "query": "What is the Austrian School of Economics?",
  "session_id": "12345-abcde"
}
```

#### Server to Client
The server streams responses in real-time with these message types:

1. Normal response chunks:
```json
{
  "message": "Response text chunk"
}
```

2. Full response (sent at end):
```json
{
  "message": "Complete response text",
  "end": true
}
```

3. Error responses:
```json
{
  "error": "Error message"
}
```

### REST Endpoints

#### GET /chat/history/{session_id}
Retrieve chat history for a specific session in reversed order.

Parameters:
- `session_id`: The session ID to retrieve history for (required)

Example Request:
```bash
GET /chat/history/abc123
```

Example Response:
```json
{
  "status": "success",
  "data": [
    {
      "message": "Hi there!",
      "sender": "bot", 
      "created_at": "2025-01-23T12:34:56"
    },
    {
      "message": "Hello!",
      "sender": "user",
      "created_at": "2025-01-23T12:34:50"
    }
  ]
}
```

Error Response:
```json
{
  "status": "error",
  "message": "Error description"
}
```

### Content Filtering
The API includes content filtering for:
- Child protection (CP) violations
- NSFW content

If content is flagged, the response will be:
```json
{
  "message": "¿Qué carajo?",
  "end": true
}
```
