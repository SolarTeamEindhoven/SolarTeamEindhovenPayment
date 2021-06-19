---
layout: page
title: Authentication
permalink: /authentication/
nav_order: 2
---

# Authentication

StellaPay uses an authentication backend to be able to make calls. To authenticate to the backend, you'll need credentials. If you are unsure about your credentials, ask the [maintainers](/about).

To make requests to the backend, you'll need to authenticate only once using a special endpoint. From there one, your session is valid for quite a while. It might be a good idea to keep your session open for a bit by periodically polling.

This means that for each request you sent, you must include a cookie you receive from the backend after authenticating.

### Request interface (POST)

This is a POST request with a JSON body. Use the following arguments:

| Arguments | Description                                                  |
| --------- | ------------------------------------------------------------ |
| username  | Username to authenticate with.  **This is not the same as a user that can make transactions!** |
| password  | Password to use                                              |

*Remember: store the cookies you receive from the response and send them again with each new request so the server can identify you!*

### Example request

An example body of the request looks like this:

```json
{
    "username": "test",
    "password": "test12"
}
```

