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
# Stage 3

## Query Analysis

Given Query:

```sql
SELECT * FROM notifications
WHERE studentID = 1042
AND isRead = false
ORDER BY createdAt DESC;
```

---

## Is The Query Accurate?

Yes.

The query correctly retrieves all unread notifications belonging to a specific student and returns them in descending order of creation time.

---

## Why Can The Query Become Slow?

As the notifications table grows to millions of records, the database may need to scan a large portion of the table before filtering records.

Potential causes:

1. Full table scans
2. Missing indexes
3. Large dataset size
4. Expensive sorting operations

---

## Recommended Indexing Strategy

Instead of indexing every column, a composite index should be created based on the query pattern.

```sql
CREATE INDEX idx_notifications_student_read_created
ON notifications(studentID, isRead, createdAt DESC);
```

### Benefits

- Faster filtering by studentID
- Faster filtering by isRead
- Faster ordering by createdAt
- Reduced disk reads

---

## Why Not Create Indexes On Every Column?

Although indexes improve read performance, excessive indexing introduces several problems:

### Increased Storage Usage

Each index consumes additional disk space.

### Slower Insert Operations

Every insert must update all related indexes.

### Slower Update Operations

Updating indexed columns requires index maintenance.

### Higher Maintenance Cost

Large numbers of indexes increase database overhead.

Therefore, indexes should only be created for frequently queried columns.

---

## notificationType: ENUM vs VARCHAR

### ENUM

Advantages:

- Better storage efficiency
- Restricts values to valid notification types
- Prevents invalid data

Disadvantages:

- Schema changes required when adding new notification types

### VARCHAR

Advantages:

- Flexible
- Easier to extend

Disadvantages:

- Allows invalid values unless validated

---

## Recommendation

I would use ENUM because the notification types are limited and predefined:

- Placement
- Event
- Result

This improves data consistency and reduces storage overhead.

---

## Logging Middleware Usage

```text
Log("backend","info","db","Notification query executed")

Log("backend","warn","db","Query execution time increasing")

Log("backend","error","db","Missing index detected")

Log("backend","fatal","db","Database performance degradation")
```
# Stage 4

## Problem Statement

The notification system may experience extremely high traffic when thousands of notifications are generated simultaneously. Directly processing every notification request can overload the application server and increase response times.

---

## Proposed Solution

I would introduce a Message Queue between notification producers and notification consumers.

### Architecture

```text
Client
   |
   v
Notification API
   |
   v
Message Queue
   |
   v
Notification Workers
   |
   v
Database / Email Service / Push Service
```

---

## How It Works

### Step 1

The client sends a notification request to the Notification API.

### Step 2

Instead of processing the notification immediately, the API pushes the request into a Message Queue.

### Step 3

Worker services continuously consume messages from the queue.

### Step 4

Workers process notifications asynchronously and deliver them through the required channels.

---

## Benefits

### Improved Scalability

The queue can handle sudden traffic spikes without overwhelming the application.

### Faster Response Time

The API responds quickly after placing the request into the queue.

### Reliability

Notifications remain in the queue even if workers temporarily fail.

### Load Distribution

Multiple worker instances can process notifications in parallel.

---

## Recommended Technologies

- RabbitMQ
- Apache Kafka
- AWS SQS

For this use case, RabbitMQ would be sufficient due to its simplicity and reliability.

---

## Fault Tolerance

If a worker crashes:

1. Notification remains in queue.
2. Another worker processes it.
3. Message loss is minimized.

---

## Logging Middleware Usage

```text
Log("backend","info","service","Notification added to queue")

Log("backend","info","service","Worker processing notification")

Log("backend","warn","service","Queue length increasing")

Log("backend","error","service","Worker processing failed")

Log("backend","fatal","service","Queue unavailable")
```
