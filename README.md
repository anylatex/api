## User

User object format:

```
{
    "user_id": "user id",
    "compiled_pdfs": ["pdf id"]
}
```

### Get a user

Get a user by user's id.

```
GET /users/<id>
```

### Create a user

Create a user.

```
POST /users
```

### Delete a user

Delete a user by user's id.

```
DELETE /users/<id>
```


## Compiled PDF

PDF object format:

```
{
    "pdf_id": "pdf id",
    "compiled_time": "timestamp",
    "data": "base64 encoded string"
}
```

### Get a compiled pdf

Get a compiled pdf by id.

```
GET /pdfs/<id>
```


## Compile Tasks

Task object format:

```
{
    "task_id": "task id",
    "status": "new" or "compiling" or "finished",
    "latex": "latex document",
    "user_id": "user id",
    "pdf_b64": "compiled pdf's content"
}
```

### Get a task's status

Get a compiling task's status by id.

```
GET /tasks/<id>
```

### Create a task

Create a compiling task.

```
POST /tasks

{
    "latex": "latex document",
    "user_id": "user id"
}
```

### Delete a task

Delete a finished task.

DELETE /tasks/<task_id>



