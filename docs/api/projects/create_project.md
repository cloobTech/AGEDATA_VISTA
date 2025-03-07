## Endpoint

```
POST /projects
```

## Description

This endpoint is used to create a new project in the system. It collects the project's details and assigns an owner.

## Request

### Request Body

The request body should be a JSON object with the following structure:

| Field         | Type   | Required | Description                                            |
| ------------- | ------ | -------- | ------------------------------------------------------ |
| `title`       | string | Yes      | The title of the project.                              |
| `description` | string | Yes      | A brief description of the project.                    |
| `owner_id`    | string | Yes      | The unique identifier of the project owner.            |
| `visibility`  | string | No       | The visibility of the project. Defaults to `"public"`. |

### Example Request Body

```json
{
  "title": "AI Research",
  "description": "A project focused on AI advancements.",
  "owner_id": "12345",
  "visibility": "private"
}
```
