# Wasend SDK

A powerful SDK for managing WhatsApp sessions across multiple programming languages. This SDK provides a simple and intuitive interface for creating, managing, and interacting with WhatsApp sessions.

## Features

* Create and manage WhatsApp sessions
* QR code authentication
* Session status management (start, stop, restart)
* Account protection features
* Message logging
* Webhook support
* Multi-language support (TypeScript/JavaScript, Python, Java, .NET, Go)

## Installation

### TypeScript/JavaScript (npm)

```bash
npm install @wasend/core
# or
yarn add @wasend/core
```

### Python (pip)

```bash
pip install wasend-dev
```

### Java (Maven)

```xml
<dependency>
    <groupId>com.wasend</groupId>
    <artifactId>wasend-core</artifactId>
    <version>1.0.0</version>
</dependency>
```

### .NET (NuGet)

```bash
dotnet add package Wasend.Core
```

### Go

```bash
go get github.com/wasenddev/wasend-sdk-go
```

## Quick Start

### TypeScript/JavaScript Example

```python
import { WasendClient } from '@wasend/core';

// Initialize the client
const client = new WasendClient({
    apiKey: 'your-api-key',
    baseUrl: 'https://api.wasend.dev'
});

// Create a new session
const session = await client.sessions.createSession({
    sessionName: 'my-whatsapp-session',
    phoneNumber: '+919876543210', // Example phone number
    enableAccountProtection: true,
    enableMessageLogging: true,
    enableWebhook: false
});

// Get QR code for authentication
const qrCode = await client.sessions.getQRCode(session.uniqueSessionId);
console.log('Scan this QR code with WhatsApp:', qrCode.data);

// Start the session
await client.sessions.startSession(session.uniqueSessionId);

// Get session information
const sessionInfo = await client.sessions.getSessionInfo(session.uniqueSessionId);
console.log('Session status:', sessionInfo.status);
```

## Session Management

### Creating a Session

```python
const session = await client.sessions.createSession({
    sessionName: 'my-whatsapp-session',
    phoneNumber: '+919876543210',
    enableAccountProtection: true,
    enableMessageLogging: true,
    enableWebhook: true,
    webhookUrl: 'https://your-webhook-url.com/callback'
});
```

### Session Configuration Options

* `sessionName`: A unique name for your session
* `phoneNumber`: The WhatsApp phone number to use (format: +[country code][number])
* `enableAccountProtection`: Enable additional security features
* `enableMessageLogging`: Enable message history logging
* `enableWebhook`: Enable webhook notifications
* `webhookUrl`: URL for receiving webhook notifications (required if enableWebhook is true)

### Managing Sessions

```python
// Get all sessions
const allSessions = await client.sessions.getAllSessions();

// Get specific session info
const sessionInfo = await client.sessions.getSessionInfo(sessionId);

// Start a session
await client.sessions.startSession(sessionId);

// Stop a session
await client.sessions.stopSession(sessionId);

// Restart a session
await client.sessions.restartSession(sessionId);

// Delete a session
await client.sessions.deleteSession(sessionId);
```

## Group Management

The SDK provides comprehensive group management features for WhatsApp groups.

### Creating a Group

```python
const group = await client.createGroup(sessionId, {
    name: "My Group",
    participants: [{ id: "+919876543210" }],
    description: "Group description"
});
```

### Group Configuration Options

* `name`: The name of the group
* `participants`: Array of participants with their phone numbers
* `description`: Optional group description
* `pictureUrl`: Optional URL for group picture
* `tags`: Optional array of tags for the group

### Managing Groups

```python
// Get all groups
const groups = await client.getGroups(sessionId);

// Get specific group info
const groupInfo = await client.getGroup(sessionId, groupId);

// Get group participants
const participants = await client.getGroupParticipants(sessionId, groupId);

// Add participants to group
await client.addGroupParticipants(sessionId, groupId, {
    participants: ["+919876543210"],
    notify: true
});

// Remove participants from group
await client.removeGroupParticipants(sessionId, groupId, {
    participants: ["+919876543210"],
    notify: true
});

// Promote participants to admin
await client.promoteGroupParticipants(sessionId, groupId, {
    participants: ["+919876543210"],
    notify: true
});

// Demote participants from admin
await client.demoteGroupParticipants(sessionId, groupId, {
    participants: ["+919876543210"],
    notify: true
});
```

### Group Settings

```python
// Set group description
await client.setGroupDescription(sessionId, groupId, {
    description: "New group description"
});

// Set group subject/name
await client.setGroupSubject(sessionId, groupId, {
    subject: "New group name"
});

// Set group picture
await client.setGroupPicture(sessionId, groupId, {
    url: "https://example.com/picture.jpg",
    format: "jpeg",
    cropToSquare: true
});

// Delete group picture
await client.deleteGroupPicture(sessionId, groupId);
```

### Group Security Settings

```python
// Set info admin only
await client.setGroupInfoAdminOnly(sessionId, groupId, {
    enabled: true
});

// Set messages admin only
await client.setGroupMessagesAdminOnly(sessionId, groupId, {
    enabled: true
});

// Get current security settings
const infoAdminOnly = await client.getGroupInfoAdminOnly(sessionId, groupId);
const messagesAdminOnly = await client.getGroupMessagesAdminOnly(sessionId, groupId);
```

### Group Invite Management

```python
// Get group invite code
const inviteCode = await client.getGroupInviteCode(sessionId, groupId);

// Revoke group invite code
const newInviteCode = await client.revokeGroupInviteCode(sessionId, groupId);

// Join a group using invite code
const joinInfo = await client.getGroupJoinInfo(sessionId, "https://chat.whatsapp.com/1234567890abcdef");
await client.joinGroup(sessionId, {
    code: "https://chat.whatsapp.com/1234567890abcdef"
});

// Leave a group
await client.leaveGroup(sessionId, groupId);
```

### Group Query Options

When retrieving groups, you can use various query parameters:

```python
const groups = await client.getGroups(sessionId, {
    sortBy: "creation",        // Sort by: 'id', 'subject', 'creation', 'participantsCount'
    sortOrder: "desc",         // Sort order: 'asc' or 'desc'
    limit: 50,                 // Maximum number of results
    offset: 0,                 // Number of results to skip
    exclude: ["participants"], // Fields to exclude from response
    status: "ACTIVE",         // Filter by status: 'ACTIVE', 'ARCHIVED', 'DELETED'
    search: "group name",     // Search by name or description
    tags: ["tag1", "tag2"]    // Filter by tags
});
```

### Group Status

A group can have the following statuses:

* `ACTIVE`: Group is active and can be used
* `ARCHIVED`: Group has been archived
* `DELETED`: Group has been deleted

## Authentication

### QR Code Authentication

1. Create a session
2. Get the QR code
3. Scan the QR code with WhatsApp on your phone
4. The session will automatically connect once scanned

```python
const qrCode = await client.sessions.getQRCode(sessionId);
console.log('QR Code data:', qrCode.data);
```

## Session Status

A session can have the following statuses:

* `CREATED`: Session has been created but not started
* `STARTING`: Session is in the process of starting
* `CONNECTED`: Session is connected and ready to use
* `STOPPED`: Session has been stopped
* `ERROR`: Session encountered an error

## Webhook Integration

To receive notifications about session events:

1. Enable webhooks when creating a session
2. Provide a valid webhook URL
3. Handle incoming webhook notifications on your server

```python
const session = await client.sessions.createSession({
    sessionName: 'webhook-enabled-session',
    phoneNumber: '+919876543210',
    enableWebhook: true,
    webhookUrl: 'https://your-server.com/webhook'
});
```

## Error Handling

```python
try {
    const session = await client.sessions.createSession({
        sessionName: 'test-session',
        phoneNumber: '+919876543210'
    });
} catch (error) {
    console.error('Error creating session:', error);
}
```

## Best Practices

1. Always store the `sessionId` after creating a session
2. Implement proper error handling
3. Use environment variables for API keys
4. Enable account protection for production sessions
5. Implement webhook handling for real-time updates
6. Regularly check session status
7. Clean up unused sessions

## Support

For support, please contact:

* Email: admin@wasend.dev
* Website: https://wasend.dev
* Documentation: https://docs.wasend.dev

## License

This SDK is licensed under the Apache-2.0 License. See the [LICENSE](LICENSE) file for details.
