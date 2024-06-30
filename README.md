# Sunnylive Livestreaming App

Sunnylive is a demonstration of a simple livestreaming app that features a donation system. Users can watch a video livestream in real-time or host their own. Viewers can donate and give comments to the streamer and other viewers. The donation system implemented in this project utilizes the Midtrans payment gateway.

## Table of Contents

1. [Technologies used](#tech)
2. [Software architecture](#architecture)
3. [Use case diagram](#usecase)
4. [Database class diagram](#class)
5. [Project structure](#structure)
6. [How to run this project locally](#run)
7. [Payment gateway integration](#payment)

<a name="tech"></a>
## Technologies Used

    - Frontend: Next.js
    - Backend: Django REST Framework
    - Database: SQLite
    - Authentication: JSON Web Tokens (JWT)
    - Media streaming: Nginx RTMP module
    - Payment gateway Midtrans SNAP
    - Websocket communications: Django Channels
    - Task queue: Celery
    - In-memory storage: Redis

<a name="architecture"></a>
## Software Architecture

![Software Architecture](SoftwareArchitecture.png?raw=true "Software Architecture")
<a name="usecase"></a>
## Use Case Diagram

![Use Case Diagram](UCD.png?raw=true "Use Case Diagram")

<a name="class"></a>
## Database Class Diagram

![Database Class Diagram](DatabaseCD.png?raw=true "Database Class Diagram")
<a name="structure"></a>

## Project Structure

### Client

```
client
├── app
│   ├── [stream_id]
│   ├── api
│   │   ├── comments
│   │   ├── donations
│   │   │   └── webhook
│   │   ├── login
│   │   ├── logout
│   │   ├── me
│   │   ├── refresh-token
│   │   ├── register
│   │   ├── search
│   │   └── streams
│   │       └── [stream_id]
│   │           ├── end
│   │           ├── key
│   │           └── start
│   ├── login
│   ├── register
│   ├── success
│   ├── layout.tsx
│   └── page.tsx
├── components
│   ├── ...
│   └── ui
│       └── ...
├── components.json
├── config
│   └── site.ts
├── context
│   └── user.context.tsx
├── hooks
│   └── use-key-press.tsx
├── lib
│   ├── fonts.ts
│   └── utils.ts
├── package.json
├── public
│   └── ...
├── styles
│   └── globals.css
└── types
    ├── Stream.ts
    └── User.ts
```

### Server

```
server
├── api
│   ├── apps.py
│   ├── consumers.py
│   ├── middlewares.py
│   ├── midtrans
│   │   └── client.py
│   ├── routings.py
│   ├── serializers.py
│   ├── tasks.py
│   ├── urls.py
│   ├── utils.py
│   └── views.py
├── app
│   ├── asgi.py
│   ├── celery.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   │   └── ...
│   └── models.py
├── db.sqlite3
├── manage.py
└── requirements.txt
```

<a name="run"></a>

## How to run this project locally

- Make sure you have the following software installed on your computer.
	- Python
	- Node.js
	- Nginx
	- Redis
- Begin by cloning this repository into your computer.
- Change into the project directory and create a `.env` file based on `.env.example`
### Server
1. Change directory to `/server`
2. Create a Python virtual environment:
```
python -m venv env
```
3. Activate the virtual environment:
```
source env/bin/activate
```
4. Install the required libraries specified in the requirements.txt file:
```
pip install -r requirements.txt
```
5. Run the migrations:
```
python manage.py migrate
```
6. Finally, run the server:
```
python manage.py runserver
```
###### Starting the Celery task queue worker
1. Open a new terminal, and activate the virtual environment
2. Start the worker process:
```
celery -A app worker -l INFO
```

### Client
1. Change directory to `/client`
2. Install the required libraries:
```
yarn
```
3. Install the [CORS Chrome Extension](https://chrome.google.com/webstore/detail/allow-cors-access-control/lhobafahddgcelffkeicbaginigeejlf)
4. And finally, run the app:
```
yarn dev
```

### Streaming Server
1. Change directory to `/nginx`
2. Copy the contents of `nginx.conf` to the global nginx configuration file located at `/etc/nginx/nginx.conf`:
```
cp nginx.conf /etc/nginx/nginx.conf
```
3. Reload the Nginx service:
```
sudo systemctl reload nginx
```

<a name="payment"></a>
## Payment Gateway Integration

###### Donation Sequence Diagram
![Donation Sequence Diagram](DonationSD.png?raw=true "Donation Sequence Diagram")

This application integrates Snap, Midtrans's Payment API that includes a prebuilt hosted checkout page to help process donations. Midtrans provides sandbox environment as well as a payment simulator to help testing and development. All transaction made within this environment is not "real", and does not require "real payment/fund". This environment is created automatically when you sign up and is free to use.
###### Steps to test the payments integration locally
To utilize Midtrans' notification handler on localhost, you can utilize the services such as [Ngrok](https://ngrok.com/), to expose your localhost server to public Internet. Once you have obtained the Internet accessible URL, you can add it to the _Notification URL_ field on _Dashboard_.
1. Install Ngrok on your computer and sign up for an ngrok account to obtain your auth token.
2. Run the following command in your terminal to install the authtoken and connect the ngrok agent to your account.
```
ngrok config add-authtoken <TOKEN>
```
3. Start ngrok by running the following command.
```
ngrok http 3000
```
4. You will receive a Forwarding URL (e.g. `https://0153-103-171-156-57.ngrok-free.app`) which exposes your localhost to the internet through https.
5. Sign in to your Midtrans account and head into the Merchant Administration Portal (_MAP_) dashboard on sandbox mode: https://dashboard.sandbox.midtrans.com/
6. Head over to Settings > Access Keys, obtain your Server Key which will be stored in the environment variables file of the project.
7. Head to Settings > Payment > Finish Redirect URL
8. Add `https://FORWARDING-URL.ngrok-free.app/success` as the finish redirect URL endpoint and click Save.
9. Head to Settings > Payment > Notification URL
10. Add `https://FORWARDING-URL.ngrok-free.app/api/donations/webhook` as the payment notification URL endpoint and click Save.
