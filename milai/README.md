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
  "message": "Complete response text"
}
```

3. Error responses:
```json
{
  "error": "Error message"
}
```

### Content Filtering
The API includes content filtering for:
- Child protection (CP) violations
- NSFW content

If content is flagged, the response will be:
```json
{
  "message": "¿Qué carajo?"
}
```
