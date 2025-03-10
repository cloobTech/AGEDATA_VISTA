## Endpoint

`POST /api/v1/file-upload/`

## Description

This endpoint handles file uploads for a specific user.

## Request

The request should be made with `Content-Type: multipart/form-data` and include the following parameters:

### Form Data Parameters

| Name      | Type      | Required | Description                |
| --------- | --------- | -------- | -------------------------- |
| `user_id` | string    | Yes      | The ID of the user.        |
| `file`    | UploadFile | Yes      | The file to be uploaded.   |

## Response

### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object containing the following keys:

```json
{
    "status": "success",
    "message": "string",
  "data": {
    "id": "string",
    "name": "string",
    "size": "string",
    "extension": "string (csv, xls ...)", 
    "url": "string"
  }
}
```
### Error Response

- **Status Code:** `500 Internal Server Error`
- **Body:** A JSON object containing the following keys:

```json
{
  "details": {
    "message": "string"
  }
}
```

## Example Request

## Example Success Response

## Example Error Response
