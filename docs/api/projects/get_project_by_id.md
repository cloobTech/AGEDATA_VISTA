### 2. Get Project by ID

#### Endpoint
`GET /projects/{project_id}`

#### Description
Retrieves a specific project by its ID.

#### Response

- **Status Code:** `200 OK`
- **Body:**

```json
{
  "status": "success",
  "message": "Project found",
  "data": {
    "id": "1",
    "title": "AI Research",
    "description": "A project focused on AI advancements.",
    "owner_id": "12345",
    "visibility": "public"
  }
}
