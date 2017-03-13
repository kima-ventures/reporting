Kima Reporting
==================

Kima Reporting is an opensource reporting tool for VCs.

Features
----------
- Manage reporting emails
- Tag them so you can keep trace of all conversations
- Assign members and handle conflicts of interests
- Relay emails

Setup with Heroku
-------------------
**1. Create your project on Heroku**

**2. Type the following commands**

     heroku login
     heroku git:remote -a name-of-your-project
     git push heroku master

**3. Setup sendgrid**

First, create a Sendgrid account. Setup an inbound hook that will go to the url :

     https://name-of-your-project.herokuapp.com/!callback/mail/a-secret-password-you-choose/

Please take care of setting up the hook in RAW mode.

**4. Configure the project**

In the Settings tab, reveal the config variables. Then add the following configuration variables :

    FUND_NAME -> The name of your fund

    ADMIN_EMAIL -> Your e-mail address
    ADMIN_NAME -> Your name

    CALLBACK_EMAIL_PASSWORD -> The password you've entered for Sendgrid's inbound hook
    SENDGRID_USERNAME -> Your sendgrid username
    SENDGRID_PASSWORD -> Your sendgrid password

    SECRET_KEY -> A long random string of characters of your choice
    APP_DEPLOYED -> 1

**5. Migrate the database and create the initial user**

Type the following commands :

    heroku run ./manage.py migrate
    heroku run ./manage.py createsuperuser

You can now launch the service :

    heroku ps:scale web=1

## Setup with Docker

**1. [Install `docker` and `docker-compose`](https://docs.docker.com/engine/installation/)**

**2. Configure the project**

Create a file named `.env` with your settings, i.e.:
```ini
FUND_NAME="The name of your fund"
ADMIN_EMAIL="Your e-mail address"
ADMIN_NAME="Your name"
CALLBACK_EMAIL_PASSWORD="The password you've entered for Sendgrid's inbound hook"
SENDGRID_USERNAME="Your sendgrid username"
SENDGRID_PASSWORD="Your sendgrid password"
SECRET_KEY="A long random string of characters of your choice"
APP_DEPLOYED="1"
```

You can refer to Heroku's guide in order to setup your Sendgrid's account, and Sendgrid's inbound hook.

**3. Start it**

Type `docker-compose up` to start it

**4. Create the initial user**

Type the following command in order to create your first admin user :

    docker-compose run web python manage.py createsuperuser 

**5. Use it**

Just open your browser at [http://localhost:8000](http://localhost:8000) and enjoy :)

