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
    "data": "binary data"
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
    "task_id": "same to user's id",
    "status": true or false,
    "html": "html text"
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
    "html": "html text"
}
```
