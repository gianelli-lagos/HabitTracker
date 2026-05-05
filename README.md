# HabitTracker 🌱

HabitTracker is a full-stack web app that helps users stay consistent through simple habit tracking and lightweight social accountability. Users can create habits, log daily progress, visualize consistency with GitHub-style heatmaps, manage personal calendar events, connect with friends, and receive automated reminders to stay on track.

Built as a modern cloud-based application, HabitTracker combines personal productivity with simple social features in a clean, engaging experience.

🎥 **Demo Video:** [Click here to watch](#)  
🌐 **Live App:** [Click here to try HabitTracker](https://habittracker-io.vercel.app/)

---

## Features ✨

- Create habits and log daily progress
- Track consistency with GitHub-style heatmaps
- View habit activity and progress insights
- Add personal events to a calendar
- Invite friends to calendar events
- Send and receive friend requests
- Keep event invites limited to approved friends
- View profile stats, name, and profile picture
- Receive daily reminders, streak-loss notifications, and weekly summaries

---

## Tech Stack 🛠️

**Frontend:** React, TypeScript, Chart.js, React Calendar Heatmap, Vercel  
**Backend:** FastAPI, Python, REST APIs, JWT Authentication  
**Database:** PostgreSQL  
**Cloud & DevOps:** Docker, GitHub Actions, AWS RDS, AWS Lambda, AWS EventBridge, AWS CloudWatch

---

## AWS Architecture ☁️

HabitTracker uses a cloud-native AWS architecture designed for scalability, automation, and reliability:

- **AWS RDS (PostgreSQL)** stores user, habit, friend, and event data
- **AWS Lambda** handles automated background jobs
- **AWS EventBridge** schedules reminders, streak checks, and weekly summaries
- **AWS CloudWatch** monitors logs, errors, and system health

This architecture keeps the application lightweight on the frontend while offloading storage, automation, and observability to managed cloud services.

---

## Notifications & Automation 🔔

HabitTracker uses AWS Lambda for automated background tasks, including:

- Daily habit reminders
- Streak-loss notifications
- Weekly progress summaries

These scheduled jobs run through EventBridge, allowing the app to deliver updates automatically without manual intervention.

---

## DevOps Highlights ⚙️

- Deployed on Vercel for fast frontend delivery
- Containerized backend with Docker
- Automated CI/CD pipelines with GitHub Actions
- PostgreSQL hosted on AWS RDS
- Profile images stored in local static file
- Scheduled background jobs with AWS Lambda + EventBridge
- Monitoring and logs with AWS CloudWatch

---

## Team 👥

Built by:

- **Gianelli Lagos** — [LinkedIn](https://www.linkedin.com/in/gianellil/)
- **Danica Lacuesta** — [LinkedIn](https://www.linkedin.com/in/danica-lacuesta/)
- **Jocelyn Mo** — [LinkedIn](https://www.linkedin.com/in/jocelyn-mo-435585344/)
- **Samantha York** — [LinkedIn](https://www.linkedin.com/in/samantha-york-56b099232/)

---

## Resume Highlights 📌

HabitTracker demonstrates experience with full-stack development, cloud deployment, CI/CD automation, serverless workflows, authentication, and scalable application design.
