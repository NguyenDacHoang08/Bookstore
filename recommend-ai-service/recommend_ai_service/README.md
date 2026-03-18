# Recommend AI Service

A Django REST API service for book recommendations using collaborative filtering.

## Features

- Collaborative filtering based recommendations
- Fallback to content-based (author) recommendations
- User rating and interaction tracking
- RESTful API endpoints

## Endpoints

- `GET /health/` - Health check
- `GET /recommend/<book_id>/?user_id=<user_id>` - Get book recommendations
- `POST /rating/` - Add a book rating
- `POST /interaction/` - Add user interaction

## Models

- BookRating: Stores user ratings for books
- UserInteraction: Stores user interactions (view, purchase, etc.)

## Running

1. Install dependencies: `pip install -r requirements.txt`
2. Run migrations: `python manage.py migrate`
3. Start server: `python manage.py runserver`

## Docker

Build and run with Docker Compose from the root directory.