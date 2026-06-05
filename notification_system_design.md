# Stage 1

## Objective

Design a notification platform that allows students to receive real-time updates regarding Placements, Events, and Results.

## Assumptions

- Students are authenticated before accessing the platform.
- Notifications are stored persistently in a database.
- Notifications can be categorized as Placement, Event, or Result.
- Every notification has a unique identifier.
- Logging Middleware will be used to record important application events and failures.

## Core Actions

1. Create Notification
2. Retrieve All Notifications
3. Retrieve Notification By ID
4. Mark Notification As Read
5. Delete Notification
6. Filter Notifications By Type
7. Send Notification To Students

## Authentication

All endpoints are protected using Bearer Token Authentication.

Example Header:

Authorization: Bearer <access_token>

## API Design

### Create Notification

**Endpoint**

POST /notifications

**Request**

```json
{
  "type": "Placement",
  "message": "New notification message"
}
```

**Response**

```json
{
  "id": "notification_id",
  "status": "created"
}
```

**Logging**

```text
Log("backend","info","service","Notification created successfully")
```

### Retrieve All Notifications

**Endpoint**

GET /notifications

**Response**

```json
[
  {
    "id": "notification_id",
    "type": "Placement",
    "message": "Notification message",
    "isRead": false,
    "createdAt": "timestamp"
  }
]
```

**Logging**

```text
Log("backend","info","handler","Retrieved notifications")
```

### Retrieve Notification By ID

**Endpoint**

GET /notifications/{id}

**Response**

```json
{
  "id": "notification_id",
  "type": "Placement",
  "message": "Notification message",
  "isRead": false,
  "createdAt": "timestamp"
}
```

### Mark Notification As Read

**Endpoint**

PUT /notifications/{id}/read

**Response**

```json
{
  "status": "success"
}
```

### Delete Notification

**Endpoint**

DELETE /notifications/{id}

**Response**

```json
{
  "status": "deleted"
}
```

**Logging**

```text
Log("backend","warn","service","Notification deleted")
```

### Filter Notifications

**Endpoint**

GET /notifications?type=Placement

**Response**

```json
[
  {
    "id": "notification_id",
    "type": "Placement",
    "message": "Notification message"
  }
]
```

## Notification Data Model

| Field | Description |
|---------|------------|
| id | Unique notification identifier |
| type | Placement, Event, Result |
| message | Notification content |
| isRead | Read status |
| createdAt | Creation timestamp |

## Persistence Strategy

Notifications will be stored in a persistent database to ensure:

- Data durability
- Historical notification retrieval
- Filtering support
- Read/unread tracking
- Scalability for future growth

## Logging Middleware Usage

The reusable logging middleware will be integrated across the application lifecycle.

Examples:

```text
Log("backend","info","service","Notification created")
Log("backend","warn","handler","Invalid notification request")
Log("backend","error","repository","Database connection failed")
Log("backend","fatal","service","Notification service unavailable")
```
# Stage 2

## Database Selection

I would choose PostgreSQL as the persistent storage solution for the notification platform.

### Reasons

1. Relational structure fits notification data well.
2. Strong ACID compliance ensures data consistency.
3. Supports indexing for fast retrieval.
4. Handles large datasets efficiently.
5. Provides scalability through partitioning and replication.

---

## Database Schema

### notifications

| Column | Data Type | Description |
|----------|----------|-------------|
| id | UUID | Primary Key |
| type | VARCHAR(20) | Placement, Event, Result |
| message | TEXT | Notification content |
| is_read | BOOLEAN | Read status |
| created_at | TIMESTAMP | Notification creation time |

---

## Indexing Strategy

To improve query performance, the following indexes will be created:

### Primary Index

```sql
CREATE INDEX idx_notification_id
ON notifications(id);
```

### Type Index

```sql
CREATE INDEX idx_notification_type
ON notifications(type);
```

### Read Status Index

```sql
CREATE INDEX idx_notification_read
ON notifications(is_read);
```

### Timestamp Index

```sql
CREATE INDEX idx_notification_created
ON notifications(created_at DESC);
```

---

## Potential Scalability Challenges

As the number of notifications grows into millions of records, the following issues may occur:

### Large Table Size

Query execution may become slower due to increased table size.

### Index Maintenance Cost

Additional indexes improve reads but increase write overhead.

### Storage Growth

Historical notifications will continuously increase storage requirements.

---

## Proposed Solutions

### Table Partitioning

Partition notifications based on creation date to reduce scan size.

### Archival Strategy

Move old notifications to archive tables after a defined retention period.

### Read Replicas

Use read replicas to distribute heavy read traffic.

### Pagination

Retrieve notifications using pagination instead of loading all records at once.

Example:

```text
GET /notifications?page=1&size=20
```

---

## Logging Middleware Usage

Examples of logs generated during database operations:

```text
Log("backend","info","repository","Notification stored successfully")

Log("backend","warn","repository","Large notification dataset detected")

Log("backend","error","db","Database query timeout")

Log("backend","fatal","db","Database unavailable")
```
