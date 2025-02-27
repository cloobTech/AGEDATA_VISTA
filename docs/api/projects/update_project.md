### 3. Update Project

#### Endpoint

`PUT /projects/{project_id}`

#### Description

Updates an existing project with the provided data.

#### Request

- **Request Body:**

```json
{
  "title": "Updated AI Research",
  "description": "An updated project description.",
  "visibility": "private"
}
```

#### Response

- **Successful Response Body:**

```json
{
  "status": "success",
  "message": "Project updated",
  "data": {
    "id": "1",
    "title": "Updated AI Research",
    "description": "An updated project description.",
    "owner_id": "12345",
    "visibility": "private"
  }
}
```
