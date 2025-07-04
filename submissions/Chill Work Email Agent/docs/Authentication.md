# Authentication
In this document, I will discuss about the authentication part of the app.
## Setup
* Visit the [Google Console Window](https://console.cloud.google.com/)
* Create a new project 
* Enable the Gmail API that will be under **APIs and Services > Library**
* Create the **APIs & Services > Credentials** and **Create Credentials > OAuth Client ID**
* Select the **Desktop App** 
* Provide the name for the client and create 
* Store the credentials such as `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in the `.env` file inside the `backend/` directory
* Configure the **APIs & Services > OAuth Consent Screen**, select **External** as the user type and **Create** 
* Fill the required fields like App name, User support email, Developer contact email
## End points
| URL | Description |
| --- | --- |
| `/login` | For getting log-in form values |
| `/auth/callback` | Using Google API to authenticate the user |
| `/get-user-data` | To get the user name, mail ID and profile picture |
| `/logout` | To clear the session information in the browser |