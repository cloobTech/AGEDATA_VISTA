## Endpoint

`POST /api/v1/ai-agent`

## Description

Send a message to the AI agent and receive a generated response.
The agent maintains conversational context using a session_id, allowing multi-turn conversations across requests.

If the provided session_id already exists, the agent continues the conversation.
If it does not exist, a new conversation session is implicitly started.

| Name           | Type   | Required | Description                 |
| -------------- | ------ | -------- | --------------------------- |
| `Content-Type` | string | Yes      | Must be `application/json`. |
| `Accept`       | string | Yes      | Must be `application/json`. |

| Name         | Type   | Required | Description                                                                  |
| ------------ | ------ | -------- | ---------------------------------------------------------------------------- |
| `session_id` | string | Yes      | Unique identifier for the chat session. Used to preserve conversation state. |
| `message`    | string | Yes      | The user’s message sent to the AI agent.                                     |

### Response

### Success Response

- Status Code: 200 OK

- Body: A JSON object containing the AI agent’s reply.

```json
{
  "reply": "Of course! How can I assist you today?"
}
```


### Example Curl
```json
curl -X POST "http://localhost:8000/api/v1/ai-agent" \
-H "Content-Type: application/json" \
-d '{
  "session_id": "test-session-123",
  "message": "Explain how session-based memory works"
}'
