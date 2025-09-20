## Endpoint

`DELETE /api/v1/plans/{plan_id}`

## Description

Delete an existing subscription plan. Plans with active subscriptions cannot be deleted.

## Request

### URL Parameters

| Name      | Type   | Required | Description                      |
| --------- | ------ | -------- | -------------------------------- |
| `plan_id` | string | Yes      | The ID of the subscription plan. |

### Headers

| Name           | Type   | Required | Description                 |
| -------------- | ------ | -------- | --------------------------- |
| `Content-Type` | string | Yes      | Must be `application/json`. |
| `Accept`       | string | Yes      | Must be `application/json`. |

## Response

### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object confirming the deletion of the subscription plan.

```json
{
  "status": "success",
  "message": "Plan deleted successfully",
  "data": null
}
```

### Error Responses

- **Status Code:** `404 Not Found`

  - **Detail:** Plan not found.
  - **Example:**
    ```json
    {
      "detail": "Plan not found"
    }
    ```

- **Status Code:** `400 Bad Request`
  - **Detail:** Cannot delete a plan with active subscriptions.
  - **Example:**
    ```json
    {
      "detail": "Cannot delete plan with active subscriptions"
    }
    ```

---
