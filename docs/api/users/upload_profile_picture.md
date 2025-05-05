### Upload User Profile Picture

**Endpoint:**  
`POST /api/v1/users/{user_id}/profile_picture`

---

**Description:**  
Upload a profile picture for a specific user.

---

**Parameters:**

- **Path Parameters:**

  - `user_id` (string): The ID of the user whose profile picture is being uploaded.

- **Request Body (Form Data):**
  - `file` (UploadFile): The profile picture file to be uploaded. This must be sent as `multipart/form-data`.

---

**Responses:**

- **200 OK:**  
  Profile picture uploaded successfully.  
  **Response Body:**

  ```json
  {
    "message": "Profile picture uploaded successfully",
    "data": {
      "user_id": "12345",
      "file_url": "https://example.com/uploads/profile.jpg"
    }
  }
  ```

- **409 Conflict:**  
  The user was not found.  
  **Response Body:**

  ```json
  {
    "detail": "User not found"
  }
  ```

- **500 Internal Server Error:**  
  An unexpected error occurred.  
  **Response Body:**
  ```json
  {
    "detail": "Internal server error"
  }
  ```

---

**Example Request:**

```http
POST /api/v1/users/12345/profile_picture HTTP/1.1
Content-Type: multipart/form-data

--boundary
Content-Disposition: form-data; name="file"; filename="profile.jpg"
Content-Type: image/jpeg

(binary image data)
--boundary--
```
