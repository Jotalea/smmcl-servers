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
- **Like a level**
```bash
curl -X POST \
  http://127.0.0.1:14984/api/stage/like \
  -H 'Content-Type: application/json' \
  -d '{
    "auth": "YourServerPasscode",
    "session": "UserSessionHash",
    "stageid": "StageID",
    "userid": "UserID"
}'
```
- **Dislike a level**
```bash
curl -X POST \
  http://127.0.0.1:14984/api/stage/dislike \
  -H 'Content-Type: application/json' \
  -d '{
    "auth": "YourServerPasscode",
    "session": "UserSessionHash",
    "stageid": "StageID",
    "userid": "UserID"
}'
```
## Accounts
- **Register an account**
This can also be done via Discord through the bot (recommended)
```bash
curl -X POST \
  http://127.0.0.1:14984/api/account/register \
  -H 'Content-Type: application/json' \
  -d '{
    "auth": "YourServerPasscode",
    "username": "NewUsername",
    "password": "NewPassword",
    "discord": "DiscordID"
}'
```
- **Log in**
```bash
curl -X POST \
  http://127.0.0.1:14984/api/account/login \
  -H 'Content-Type: application/json' \
  -d '{
    "auth": "YourServerPasscode",
    "username": "Username",
    "password": "Password"
}'
```
## Misc.
- **Example endpoint**
```bash
curl -X POST \
  http://127.0.0.1:14984/api/example \
  -H 'Content-Type: application/json' \
  -d '{
    "auth": "YOUR_AUTH_CODE"
}'
```