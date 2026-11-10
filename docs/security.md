# Cloud security design
TODO: password hashing, session handling, CSRF, Google OAuth, secrets management, HTTPS, role-based access, API key protection, risks and trade-offs.

## MongoDB Atlas

### Database users and roles

Each database user on MongoDB Atlas has only the access it needs to do its job. There are two:

- **helpbot-ingest** has the built-in `readWrite` role on the `helpbot` database only. The ingestion script uses it to delete and re-insert a vehicle's manual sections and to create the text index, so it needs full read and write access. It is only used offline during development. Its password is kept in my local `.env` file and is never deployed.
- **helpbot-app** is the user the live app connects as. It has a custom role, `helpbotApp`, which can read `manual_sections` and `conversations`, and can insert, update and remove documents in `conversations` only.

The app uses a custom role instead of the built-in `readWrite` role because `readWrite` can drop collections. With `helpbotApp`, an attacker who compromised the app still could not change the manual data or drop any collections but can still read or delete `conversations`. I tested this: an insert into `manual_sections` as helpbot-app is rejected with a "not authorized" error.

There is no admin database user. The cluster is managed through my Atlas account login, which uses MFA.

### Network access

The Atlas IP Access List only accepts connections from approved IPv4 addresses: my home IP for development and, once deployed, the host server's IP. If the connection string leaked, an attacker on another network still could not connect to the cluster. My ISP can change my home IP, so the list may need updating if that happens. This only affects development, not the live server. If the host I deploy to has no fixed outbound IP, I would prefer to choose a host or add-on that provides one rather than allowing access from anywhere (`0.0.0.0/0`), which would remove this protection.

### Security contact and patching

MongoDB Atlas has a security contact email set in Organization Settings. Atlas is a managed service, so MongoDB applies security patches to the cluster itself. The contact email means I am notified about security incidents and vulnerabilities that affect the project, so I can respond quickly, for example by rotating database credentials.