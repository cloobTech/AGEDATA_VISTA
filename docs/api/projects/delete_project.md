### 4. Delete Project

#### Endpoint
`DELETE /projects/{project_id}`

#### Description
Deletes a project by its ID.

#### Response

- **Status Code:** `200 OK`
- **Body:**

```json
{
  "status": "success",
  "message": "Project deleted",
  "data": "1"
}
