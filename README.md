# 🎬 Movie Hub

[![Python](https://img.shields.io/badge/Python-3.x-blue)](https://www.python.org/) 
[![Django](https://img.shields.io/badge/Django-5.x-green)](https://www.djangoproject.com/) 
[![Render](https://img.shields.io/badge/Live%20Demo-Render-brightgreen)](https://your-render-url.onrender.com)

**Live Demo:** [https://movie-hub-a4gn.onrender.com](https://movie-hub-a4gn.onrender.com)

A Django web application that allows users to **discover, track, and interact with movies and TV shows**. Users can search for any movie or show, check IMDb ratings, view trailers, and manage their watch lists, favorites, and watched content. Admins, editors, and moderators have special permissions to manage content, while all users can explore what others are watching. 
It combines content discovery with **gamification**, **quizzes**, **badges**, and **asynchronous notifications** to keep users engaged.

---

## ✨ Motivation

This project was inspired by my love for movies and my desire to track the movies and shows I’ve watched, as well as mark the ones I want to watch in the future. It reflects my passion for cinema and storytelling, and my goal was to build a platform that organizes content in a **personal and interactive way** This project was inspired by my love for movies and my desire to track what I’ve watched, what I want to watch, and to explore what others are enjoying.

Beyond entertainment, Movie Hub was built as a **learning-driven project** to apply real-world backend concepts such as:
- Asynchronous background processing
- Scheduled tasks
- Email notifications
- Production deployment and scaling

---

## 🛠 Features

- **🔍 Search and Discovery**  
  Search for any movie or show and view detailed information including IMDb ratings and trailers.  

- **📌 Watchlist & Favorites**  
  Add movies/shows to your watchlist, mark them as watched, or save them as favorites.  

- **🔥 Trending & Popular Content**  
  Home page displays trending, popular, and user-added content dynamically. Switch between movies and shows easily.  

- **🧠 Quizzes & Gamification**
  - Weekly rotating quizzes
  - Earn **badges** by interacting with content
  - Encourages consistent user engagement

- **🏅 Badges System**
  - Users earn badges based on activity
  - Tracks latest badge achievements
  - Inactivity is detected automatically

- **🔔 Notifications System**
  - **In-app notifications** for:
    - Weekly quiz updates
    - System messages
  - **Email notifications (async)** for:
    - Inactive users
      - Users who haven’t earned a badge in a while
      - Welcome emails on signup

- **⚡ Asynchronous Background Tasks**
  - Built using **Celery + Redis**
  - Tasks include:
    - Weekly quiz rotation
    - Scheduled notifications
    - Async email delivery with retries
  - Managed via **django-celery-beat**

- **👥 User Interaction**  
  Discover other users, see their watched content, and interact through reviews and ratings.  

- **🛡 Admin & Moderator Panel**  
  - Admins, editors, and moderators have specific permissions.  
  - Moderators can view user media, check ratings/reviews, and manage content efficiently.  

- **🔎 Advanced Searching & Filtering**  
  Extensive search, filtering, and ordering options for fast content discovery.  

- **💻 Responsive & Intuitive UI**  
  Designed for usability and clean presentation of movies and shows.

---

## ⚙️ Tech Stack

### Backend
- Python 3.x  
- Django 5.x  
- Django REST Framework (optional for APIs)   
- Celery (background tasks)
- Redis (message broker & result backend)
- django-celery-beat
- django-celery-results

### Email
- Brevo (Transactional Email API)
- Async email delivery with retry logic

### Database
- MySQL (local development)
- PostgreSQL / Neon (production)

### Other
- TMDB API
- Cloudinary (media storage)
- Whitenoise (static files)
- Bootstrap / CSS
- Git & GitHub

---

## 🚀 Deployment

- **Web App:** Render  
- **Database:** Neon  
- **Async Tasks:** Celery + Redis (production-ready configuration)

The project is live on Render: [https://movie-hub-a4gn.onrender.com](https://movie-hub-a4gn.onrender.com)

---

## Steps to run locally:

```bash
git clone https://github.com/YOUR_USERNAME/movie_site.git

cd movie_site

python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt

python manage.py runserver
```

---

## 🎯 Learning Outcomes

- Building a full-stack web application with Django
- Handling user authentication and permissions
- Advanced search, filtering, and ordering of content
- Managing static files and media in production
- CRUD operations for user-generated content and admin moderation
- Working with APIs (TMDB) for movie data and trailers
- Asynchronous task processing with Celery & Redis
- Scheduled background jobs with django-celery-beat
- Clean separation of concerns and scalable architecture

---

## 👩‍💻 About the Developer

Hi! I’m Sofi, a Software Engineering student at **AASTU** and an **ALX Backend Program participant**.  
I’m passionate about Python, web development, and creating full-stack applications that are both functional and user-friendly.

### 🤳 Connect with me:
[<img align="left" alt="LinkedIn" width="22px" src="https://cdn.jsdelivr.net/npm/simple-icons@v3/icons/linkedin.svg" />][linkedin]
[<img align="left" alt="GitHub" width="22px" src="https://cdn.jsdelivr.net/npm/simple-icons@v3/icons/github.svg" />][github]  

[linkedin]: https://linkedin.com/in/sofoniyas-alebachew-bb876b33b?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app
[github]: https://github.com/sofi391