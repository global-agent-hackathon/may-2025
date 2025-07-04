# Mails
This app is all about Mails. With the `Gmail` API, the reading of the mail is done and it needs configurations and it is done in the `authentication` part of the app. While login, the user will accept the request of reading the mail from the app. To send the mail via our app, we use `Mailtrap` platform

## Setup
* Create an account in the Mailtrap
* Create a domain or sandbox domain (this will be as `demomailtrap.co`)
* Head over to the dashboard page, **Sandbox > Inboxes > Integrations** and copy the following values and store it in `.env` file, `MAILTRAP_SMTP_HOST`, `MAILTRAP_SMTP_PORT`, `MAILTRAP_SMTP_USERNAME`
, `MAILTRAP_SMTP_PASSWORD`, `MAIL_FROM_ADDRESS`

## Endpoint
| Endpoints | Description |
| --- | --- | 
| `/api/sync-mails` | To sync the mail from Gmail |
| `/api/mails//send` | To send the mail via MailTrap |
| `/api/{category}` | To send the category of the mail to the front end of the app like Inbox, Important, Archive, Sent |