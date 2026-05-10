# Travelloop

## Project Overview

Travelloop is a web-based travel planning platform designed to help users create, manage, and share personalized trips. The application offers authenticated user journeys, day-by-day itinerary building, packing lists, community sharing, and AI-assisted trip suggestions.

## Key Features

- User registration and login with secure password hashing
- Create and manage multiple trips with start/end dates, traveler count, and descriptions
- Build and view rich itineraries grouped by day with cost tracking
- Add and manage packing lists with category grouping and completed status
- Share trips publicly through a community feed with likes and comments
- Search and browse curated travel destinations and local places
- AI-enabled itinerary generation and smart planning using OpenAI

## What the Project Solves

Travelloop helps travelers move beyond static checklists and spreadsheets by offering a centralized platform for:
- organizing travel plans,
- generating day-wise activity schedules,
- managing packing essentials,
- collaborating with a community of fellow travelers.

## Technical Architecture

- Backend: Python + Flask
- Database: SQLite with SQLAlchemy ORM
- Authentication: Flask-Login + Flask-Bcrypt
- Templates: Jinja2 for dynamic HTML rendering
- File uploads: `uploads/` directory for cover images and media
- AI integration: OpenAI API for smart itinerary generation

## Folder Structure

- `app.py` — main Flask application and route definitions
- `requirements.txt` — Python dependencies
- `templates/` — page templates including dashboard, trip builder, community feed, and AI planner
- `static/` — CSS and JavaScript assets for frontend interactivity
- `Datasets/` — imported destination and travel data sources
- `uploads/` — user uploaded images and files

## How It Works

1. A Traveler creates an account and logs in.
2. They create a trip with destination details, dates, and traveler count.
3. In the itinerary builder, they add destinations, hotels, food stops, and activities.
4. The app calculates total costs and organizes items by day.
5. The traveler creates a packing list and marks items as packed.
6. They can publish trip highlights to the community feed.
7. AI planning features suggest a daily schedule or smart travel plan based on destination, interests, and vibe.

## Presentation Notes

Use these talking points for your presentation:

- "Travelloop is a modern travel assistant that combines planning, itinerary creation, packing management, and community sharing in one app."
- "It leverages Flask for the backend and SQLite for lightweight persistence, so the app is easy to run and extend."
- "The platform supports travel-specific workflows like a packing checklist, public trip sharing, and AI-powered itinerary generation."
- "Its community features let users post trips, like them, and comment, which makes travel planning collaborative and social."
- "AI features include smart itinerary generation and travel plan enrichment using OpenAI, with a fallback logic for robust results."

## Run Locally

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set the OpenAI API key in `.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

3. Start the application:

```bash
python app.py
```

4. Visit `http://127.0.0.1:7000` in your browser.

## Best Demo Flow

1. Sign up and log in.
2. Create a new trip with dates and traveler details.
3. Build an itinerary and add activities, food, and accommodation.
4. Open the packing list and add travel essentials.
5. Share a trip in the community feed and like/comment on another post.
6. Show the AI planner screen and describe how it can generate a full itinerary.

---

Thank you for using Travelloop — your travel planning loop for better journeys.

