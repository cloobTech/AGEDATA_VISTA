# Project API Documentation

## Endpoints

### 1. Get All Projects

#### Endpoint

```
POST /projects/
```

#### Description

Retrieves all projects from the database.

#### Response

- **Status Code:** `200 OK`
- **Body:**

```json
{
  "status": "success",
  "message": "Projects found",
  "data": [
    {
      "id": "1",
      "title": "AI Research",
      "description": "A project focused on AI advancements.",
      "owner_id": "12345",
      "visibility": "public"
    }
  ]
}
```

### If no projects exist:

```json
{
  "status": "success",
  "message": "No projects found",
  "data": []
}
```
