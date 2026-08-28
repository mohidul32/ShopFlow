# Authentication API

All paths below are prefixed with `/api/v1/auth/`. Access tokens are passed in
the `Authorization: Bearer <access-token>` header.

| Endpoint | Method | Access | Purpose |
| --- | --- | --- | --- |
| `register/` | POST | Public | Create a customer account. Public registration never assigns seller/admin roles. |
| `login/` | POST | Public | Exchange email/password for access and refresh tokens. |
| `refresh/` | POST | Public | Rotate a valid refresh token. |
| `verify/` | POST | Public | Validate an access or refresh token. |
| `logout/` | POST | Authenticated | Blacklist the supplied refresh token. |
| `me/` | GET, PATCH | Authenticated | Read/update the user's first and last name. |
| `password/change/` | POST | Authenticated | Change password and invalidate earlier tokens. |
| `password/reset/` | POST | Public | Request a reset link. Always returns `202` to avoid account enumeration. |
| `password/reset/confirm/` | POST | Public | Set a new password using a reset `uid` and token. |

## Request examples

```json
POST /api/v1/auth/register/
{
  "email": "customer@example.com",
  "password": "ClearPass!9031",
  "password_confirmation": "ClearPass!9031",
  "first_name": "Ava",
  "last_name": "Customer"
}
```

```json
POST /api/v1/auth/login/
{
  "email": "customer@example.com",
  "password": "ClearPass!9031"
}
```

The development email backend should be configured to a console backend before
manual password-reset testing. A production email provider and asynchronous
delivery are introduced with the notification/background-job phase.
