## Endpoint

`GET /api/v1/users/{user_id}`

## Description

This endpoint retrieves a user by their ID and optionally includes related data based on the provided parameters.

## Request

The request should be made with `Content-Type: application/json` and include the following parameters:

### URL Parameters

| Name      | Type   | Required | Description                |
| --------- | ------ | -------- | -------------------------- |
| `user_id` | string | Yes      | The ID of the user.        |

### Query Parameters

| Name    | Type   | Required | Description                                                                 |
| ------- | ------ | -------- | --------------------------------------------------------------------------- |
| `params`| string | No       | A comma-separated list of related data to include (e.g., notifications, projects, owned_projects...). |

### list of valid params
`notifications, projects, owned_projects, files, invitations`

### Sample Request
```json 
"""const options = {
  method: 'GET',
  url: 'http://localhost:8000/api/v1/users/6910717b-db33-4cfd-b6e2-31821e8b2bf8',
  params: {params: 'notifications,projects,owned_projects,files,invitations'},
  headers: {'User-Agent': 'insomnia/10.3.1'}
};

axios.request(options).then(function (response) {
  console.log(response.data);
}).catch(function (error) {
  console.error(error);
});"""
```


## Response

### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object containing the following keys:

```json
{
  "status": "success",
  "message": "User found",
  "data": {
    "id": "string",
    "name": "string",
    "email": "string",
    "created_at": "string",
    "updated_at": "string",
    "notifications": [...],
    "projects": [...],
    "owned_projects": [...],
  }
}