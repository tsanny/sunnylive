# Livestream App

This is a demonstration of a simple livestreaming app that features a donation system. Users can watch a video livestream in real-time or host their own. Viewers can donate and give comments to the streamer and other viewers. The donation system implemented in this project utilizes the Midtrans Payment Gateway.

# Table of Contents

1. [Technologies used](#tech)
2. [Project structure](#structure)
3. [How to run this project](#run)

<a name="tech"></a>

# Technologies Used

    - Frontend: Next.js
    - Backend: Django REST Framework
    - Database: SQLite
    - Authentication: JSON Web Tokens (JWT)
    - Media streaming: Nginx RTMP module
    - Payment gateway Midtrans SNAP
    - Websocket communications: Django Channels
    - Task queue: Celery
    - In-memory storage: Redis

<a name="structure"></a>

# Project Structure

## Client

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

## Server

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

# How to run this project

## Server

1. You'll need Python installed on your computer
2. Create a new Python project on your machine
3. Install the required libraries specified in the requirements.txt file
4. Type the following commands `python manage.py makemigrations` and `python manage.py migrate`
5. Make sure to run your server with `python manage.py runserver`

## Client

1. For this, you'll need Node.js installed on your computer
2. Install the required libraries with `yarn`
3. Install [CORS Chrome Extension](https://chrome.google.com/webstore/detail/allow-cors-access-control/lhobafahddgcelffkeicbaginigeejlf)
4. And finally, run `yarn dev`
