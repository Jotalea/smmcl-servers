# Super Mario Maker Creative Land Servers

# Requests
## Stages
All these examples are with localhost, replace "127.0.0.1" with the real IP adress of the server.
- **Upload a stage**
```bash
curl -X POST \
  http://127.0.0.1:14984/api/stage/upload \
  -H 'Content-Type: application/json' \
  -d '{
    "auth": "YourServerPasscode",
    "session": "UserSessionHash",
    "username": "StageUsername",
    "title": "StageTitle",
    "description": "StageDescription",
    "content": "StageContentData"
}'
```
- **Download a stage by its ID**
```bash
curl -X POST \
  http://127.0.0.1:14984/api/stage/id \
  -H 'Content-Type: application/json' \
  -d '{
    "auth": "YourServerPasscode",
    "session": "UserSessionHash",
    "stageid": "StageID"
}'
```
- **Fetch the 10 newest stages**
```bash
curl -X POST \
  http://127.0.0.1:14984/api/stage/getlatest \
  -H 'Content-Type: application/json' \
  -d '{
    "auth": "YourServerPasscode",
    "session": "UserSessionHash",
    "page": 0
}'
```
