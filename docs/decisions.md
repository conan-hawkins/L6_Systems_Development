# Decision log

A record of the main technical decisions in HelpBot: the options
considered, what was chosen and why, and the trade-offs accepted. Newest
decisions are added at the end.

## Summary

| # | Decision | Choice | Date | Marking criterion |
|---|----------|--------|------|-------------------|
| 1 | Web framework | | | |
| 2 | SQL database | | | |
| 3 | NoSQL database | | | |
| 4 | LLM provider | | | |
| 5 | Vehicle data API | | | |

<!--
To add a decision: copy the template at the end of this file, give it
the next number, and add a row to the summary table.
-->

## 1. Web framework

**Date:**
04/10/26
**Context:**
The web app needs a framework to allow for easier development. Frameworks can provide routing, reusable components, database tooling, API tooling, and built-in security features. Some have a lot of features out the box, others offer expansion using librarys. The learning curve and comunity support offered is also a factor.
**Options considered:**
Flask, Django, Express, FastAPI
**Decision:**
Flask
**Reasons:**
Python is a requirement set out in the unit brief, and the unit labs also teach Flask, making it a sensible choice. This rules out Express, which is Node.js based. I've got experience with Express using TypeScript, so this would've been ideal for reducing my personal learning curve. Express offers a lot of the features I'll be needing for this web app, such as routing and middleware, with a large Node.js library ecosystem to support it.   

Flask is a lean microframework, so it is easy to learn compared to FastAPI. Flask has limited native async support, but this small university project's load is low and I/O-bound, so a threaded server will be enough for this use case. Options available to Flask if traffic were higher are gevent workers or Quart, the async version of Flask from the same maintainers. Flask wins because it will be faster to develop with and lacks the extra setup required by FastAPI for sessions, login and form handling.  

Django might have been easier to configure because it offers a lot of the tools this web app needs out of the box. However, Django's out the box ORM, admin controls, auth, and migrations would only work for half of the data required in this project. This is because Django's features are built for a single relational SQL database and not for the unstructured conversation and message data stored within MongoDB. This is in contrast to flask that treats both data stores the same. The reason Flask has been chosen over Django is because it's simple and beginer friendly. Under this project's time constraints it was decided to go with the easier-to-learn, lab-supported framework. Flasks simplicity compared to Dfango offers some advantages as well. <!-- Examples of reasons that hold up: control and understanding of each part, or fit with your app factory, blueprints and Alembic setup. --> -- Add tomorrow.
**Trade-offs accepted:**
It is a minimalist framework that does not offer a lot of features out of the box. This means tasks like authentication, API docs, request validation, and setting up an admin panel will need to be manually configured using Flask-Login, Flask-WTF, and other libraries. It also lacks a built-in ORM, so Flask-SQLAlchemy will need to be used to make database interactions easier. 

## 2. SQL database

**Date:**
04/10/26
**Context:**
An SQL database is a unit requirement, so the most suitable one for the chosen task must be found.
**Options considered:**
Neon - Free Tier, Supabase - Free Tier, Supabase - Pro, Neon - Launch
**Decision:**
Neon - Free Tier
**Reasons:**
The other options were locked behind a paywall. 

In the case of the closest competitor, Supabase, the no-cold-starts rule worked against it because it shuts down the database after a period of inactivity (1 week), which would require a manual restart. For a low-traffic chatbot with limited users, this could bring down the app. 

Another reason Neon - Free Tier was chosen is that the service supports branching on its free tier. This allows test branches of the codebase to run code in a completely production-realistic environment without risking the live production database, which would be essential for working and testing in a real-world scenario.  
**Trade-offs accepted:**
Cold starts will make the database slow at first when the system has not been used in a while. The free tier also offers a 1GB maximum storage limit. Having data hosted by an external provider presents data security and compliance risks.

## 3. NoSQL database

**Date:**
04/10/26
**Context:**
A NoSQL database is needed as part of the assignment brief for unstructured data.
**Options considered:**
MongoDB
**Decision:**
MongoDB
**Reasons:**
Widely used in industry, with a large support community, and well documented. The free options offered all the required features for this project.
**Trade-offs accepted:**
The limited storage space of the free tier. Having data hosted by an external provider presents data security and compliance risks.

## 4. LLM provider

**Date:**

**Context:**

**Options considered:**

**Decision:**

**Reasons:**

**Trade-offs accepted:**

## 5. Vehicle data API

**Date:**

**Context:**

**Options considered:**

**Decision:**

**Reasons:**

**Trade-offs accepted:**

<!--
## N. Title

**Date:**

**Context:**

**Options considered:**

**Decision:**

**Reasons:**

**Trade-offs accepted:**
-->
