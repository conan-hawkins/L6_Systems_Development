# Decision Log

A record of the main technical decisions in HelpBot: the options considered, what was chosen and why, and the trade-offs accepted. Newest decisions are added at the end.

## Summary

| # | Decision | Choice | Date | Marking Criterion |
|---|----------|----------|----------|----------|
| 1 | Web Framework | Flask | 04/10/26 | Tools, APIs and Processes |
| 2 | SQL Database | Neon Free Tier | 04/10/26 | Database Design Justification |
| 3 | NoSQL Database | MongoDB Atlas | 04/10/26 | Database Design Justification |
| 4 | LLM Provider | OpenAI | 08/10/26 | Cloud APIs and Functions |
| 5 | Vehicle Data API | DVLA Vehicle Enquiry Service API | 08/10/26 | Cloud APIs and Functions |

<!--
To add a decision: copy the template at the end of this file, give it
the next number, and add a row to the summary table.
-->

## 1. Web Framework

**Date:**  
04/10/26

**Context:**  
The web application requires a framework to simplify development. Frameworks can provide routing, reusable components, database tooling, API support, and security features. The learning curve, flexibility, and available community support were also important considerations.

**Options Considered:**  
Flask, Django, Express, FastAPI

**Decision:**  
Flask

**Reasons:**  
Python is a requirement set out in the unit brief, and the unit labs also teach Flask, making it a sensible choice. This rules out Express because it is based on Node.js. I already have experience with Express using TypeScript, so it would have reduced my personal learning curve. Express provides many of the features required for this application, such as routing, middleware support, and access to a large package ecosystem.

FastAPI was ruled out mainly on learning cost. It is designed around asynchronous request handling, Pydantic data models and dependency injection, none of which the unit labs cover, whereas Flask's simpler synchronous model matches the lab material directly.

Flask's app factory and blueprint pattern also aligns with the architecture of HelpBot, making it easier to separate authentication, chat functionality, vehicle management, and API routes into independent modules.

Flask has limited native asynchronous support, but the expected workload for this project is low and primarily I/O-bound, meaning a threaded deployment is sufficient. If significantly higher traffic levels were expected, Flask could be deployed using gevent workers or migrated to Quart, an asynchronous reimplementation of Flask that Flask's own documentation recommends for mainly asynchronous codebases.

Django was also considered because it includes authentication, administration tools, migrations, and an ORM out of the box. MongoDB now maintains an official Django backend, so this tooling could cover both of HelpBot's databases. However, the unit labs teach Flask, and learning Django's larger set of conventions would add time without a clear benefit for an application of this size.

Under the project's time constraints, Flask was chosen because it is easier to learn, supported by the module's practical sessions, and provides sufficient functionality without introducing unnecessary complexity.

**Trade-offs Accepted:**  
Flask is a lightweight framework and does not include many features out of the box. Authentication, and form handling with validation, must be added through extensions such as Flask-Login and Flask-WTF. Unlike Django, Flask has no built-in administration interface, so any admin tools would need to be built or added separately. Flask also does not include an ORM, requiring the use of Flask-SQLAlchemy for relational database access.

**Sources:**

MongoDB. (2025, September 2). *Django MongoDB Backend now generally available*. https://mongodb.com/company/blog/product-release-announcements/django-mongodb-backend-now-generally-available

Pallets. (n.d.). *Using async and await*. Flask Documentation. https://flask.palletsprojects.com/en/stable/async-await/

Pallets. (n.d.). *Welcome to Flask*. Flask Documentation. https://flask.palletsprojects.com/en/stable/

---

## 2. SQL Database

**Date:**  
04/10/26

**Context:**  
The assignment requires the use of an SQL database. The selected solution needed to support relational data storage whilst remaining suitable for a student budget and cloud deployment.

**Options Considered:**  
Neon Free Tier, Supabase Free Tier, Supabase Pro, Neon Launch

**Decision:**  
Neon Free Tier

**Reasons:**  
The paid options were excluded because they exceeded the available budget.

Supabase was the closest competitor. However, free-tier projects can be paused after seven days of low activity and require manual restoration through the dashboard before becoming available again. HelpBot is expected to experience periods of low activity, so this was considered a reliability risk for the project.

The main reason Neon was selected is its support for database branching on the free tier. Branches provide a production-like environment where schema changes and new features can be tested before deployment, without risking the live database. Neon also supports schema-only branching, which copies the database structure without any data, so development branches can hold only synthetic test data rather than real user data, avoiding privacy and GDPR concerns.

Neon also provides a fully managed PostgreSQL database, reducing the infrastructure management required for the project.

**Trade-offs Accepted:**  
On the free tier, Neon's compute scales to zero after five minutes of inactivity. The next query restarts it, typically within a few hundred milliseconds, so the first request after an idle period is slightly slower. The free tier also includes 100 compute-hours per project each month; if these run out, compute is suspended until the next billing period.

The free tier is limited to 1 GB of PostgreSQL storage per project. If the project grows beyond this limit, writes are blocked until data is cleaned up or the plan is upgraded. Hosting data with an external provider introduces security, privacy, and compliance risks that must be managed appropriately.

**Sources:**

Neon. (2026). *Branching*. https://neon.com/docs/introduction/branching

Neon. (2026). *Database branching workflow primer*. https://neon.com/docs/get-started/workflow-primer

Neon. (2026). *Neon pricing*. Retrieved November 9, 2026, from https://neon.com/pricing

Supabase. (2026). *Project pausing*. https://supabase.com/docs/guides/platform/free-project-pausing

---

## 3. NoSQL Database

**Date:**  
04/10/26

**Context:**  
A NoSQL database is required as part of the assignment brief. It is also well suited to storing semi-structured data such as conversations and message histories. Vehicle manuals and maintenance documents vary significantly between manufacturers and models, making a flexible document database an appropriate choice.

**Options Considered:**  
MongoDB Atlas, Firebase Firestore, Self-Hosted MongoDB

**Decision:**  
MongoDB Atlas

**Reasons:**  
MongoDB is widely used in industry, well documented, and integrates easily with Python through official drivers. Its document model suits the semi-structured nature of chat histories and vehicle documentation, which vary in shape between conversations and between manufacturers.

Firebase Firestore was also considered because it provides a document-based database with a free tier. The deciding factor against it was full-text search. HelpBot's manual ingestion script splits each workshop manual into sections and builds a MongoDB text index over them, weighting section titles ten times above body text, so the most relevant sections rank first when answering a question. MongoDB supports this natively, with per-field weights controlling how much each field contributes to the relevance score. Firestore's Standard edition has no native text search. Its Enterprise edition offers text search, but only as a Preview feature, and each search query is charged additional read units based on its complexity. Relying on a Preview feature with less predictable costs for HelpBot's core search function was judged a higher risk than MongoDB's established text indexes.

Portability was a secondary factor. MongoDB Atlas is also a vendor-managed service, but MongoDB itself can run on Atlas, on a self-hosted server, or on another cloud provider, so the data and queries could move without rewriting the data access layer. Firestore only runs on Google's platform.

Self-hosting MongoDB was considered, but the available free hosting option was a small server located in a residential property. This would introduce a single point of failure and offer significantly less redundancy and physical security than a managed cloud service.

MongoDB Atlas is MongoDB's managed hosting platform and provides a free tier with sufficient functionality for this project. Using Atlas allows more time to be spent developing application features rather than maintaining infrastructure.

**Trade-offs Accepted:**  
The free tier is limited to 0.5 GB of storage, including indexes, and 100 read and write operations per second. Atlas also pauses free clusters after 30 days with no connections. This is far more lenient than Supabase's seven-day pause, and regular use of HelpBot should prevent it, but a paused cluster would need to be resumed manually. Hosting data with a third-party provider introduces privacy and compliance concerns.

MongoDB allows only one text index per collection, so every searchable field in the manual sections must share a single index. MongoDB Search (formerly Atlas Search) would lift this limit, as the free tier allows up to three search indexes, and MongoDB recommends it over text indexes for relevance scoring. However, it uses a different query stage (`$search` rather than `$text`), so the search code would need rewriting.

Chat logs may contain personal information provided by users. For example, a user may mention that they are on a tight budget or unable to afford certain repairs. Storing these conversations on infrastructure not directly controlled by the project introduces additional responsibility for protecting user privacy.

The vehicle manuals imported by the ingestion script are commercial Haynes workshop manuals subject to copyright, and will be stored on infrastructure owned by a third party.

**Sources:**

Firebase. (n.d.). *Use text search*. Firestore Documentation. https://firebase.google.com/docs/firestore/enterprise/text-search

Google Cloud. (n.d.). *Firestore editions overview*. https://docs.cloud.google.com/firestore/native/docs/editions-overview

Google Cloud. (n.d.). *Firestore Enterprise edition pricing*. Retrieved November 9, 2026, from https://cloud.google.com/firestore/enterprise/pricing

MongoDB. (n.d.). *Assign $text result weights for self-managed deployments*. MongoDB Manual. https://www.mongodb.com/docs/manual/core/indexes/index-types/index-text/control-text-search-results/

MongoDB. (n.d.). *Atlas free cluster limits*. MongoDB Atlas Documentation. Retrieved November 9, 2026, from https://www.mongodb.com/docs/atlas/reference/free-shared-limitations/

MongoDB. (n.d.). *MongoDB Search compatibility & limitations*. MongoDB Search Documentation. https://www.mongodb.com/docs/search/deployment/feature-compatibility/

---

## 4. LLM Provider

**Date:**  
08/10/26

**Context:**  
HelpBot requires a Large Language Model (LLM) capable of answering user questions about vehicle maintenance and servicing. The chosen provider needed to offer a Python API that could be integrated into Flask.

**Options Considered:**  
OpenAI, Google Gemini

**Decision:**  
OpenAI

**Reasons:**  
Google Gemini was considered because it provides similar API functionality and a free tier. However, Google's terms allow only paid services in applications made available to users in the United Kingdom, the EEA or Switzerland. As HelpBot targets users in Great Britain, either provider would require paid usage, so the Gemini free tier was not a real alternative.

An OpenAI account already existed from previous projects, so development could begin immediately without creating and configuring a new account. Under the project's time constraints, this made OpenAI the lower-risk option.

Both providers offer Python SDKs, and neither uses paid API data to train or improve its models by default, so integration and data handling did not separate them.

The application's architecture places model interactions behind a service layer. This means another provider could be adopted in the future without requiring significant changes throughout the rest of the codebase.

**Trade-offs Accepted:**  
This decision breaks the project's free-tier-only budget, but no compliant free option existed: the OpenAI API is billed per token, and Gemini's free tier cannot be used for an application serving UK users. The budget constraint could therefore not be met by either provider.

OpenAI keeps API inputs and outputs in abuse-monitoring logs for up to 30 days, so the privacy policy must disclose that chat content is sent to a third party.

Using OpenAI creates some dependency on a proprietary service. Although the service layer reduces vendor lock-in, changing providers would still require development and testing effort.

AI-generated responses may occasionally contain inaccurate information. Users must therefore be informed that responses should not be treated as professional mechanical advice.

Although an existing OpenAI account is being reused, a dedicated API key will be created specifically for HelpBot. This allows usage to be monitored independently and reduces the impact if the key is accidentally exposed.

**Sources:**

Google. (2026). *Gemini API additional terms of service*. Google AI for Developers. https://ai.google.dev/gemini-api/terms

Google. (n.d.). *Gemini Developer API pricing*. Google AI for Developers. Retrieved November 9, 2026, from https://ai.google.dev/gemini-api/docs/pricing

OpenAI. (n.d.). *Data controls in the OpenAI platform*. OpenAI API Documentation. https://developers.openai.com/api/docs/guides/your-data

OpenAI. (n.d.). *Pricing*. OpenAI API Documentation. Retrieved November 9, 2026, from https://developers.openai.com/api/docs/pricing

---

## 5. Vehicle Data API

**Date:**  
08/10/26

**Context:**  
HelpBot requires vehicle information that can be retrieved from a registration number. Using an external API allows current vehicle information to be obtained without maintaining a large vehicle database internally.

**Options Considered:**  
DVLA Vehicle Enquiry Service API, Manual Data Collection

**Decision:**  
DVLA Vehicle Enquiry Service API

**Reasons:**  
The DVLA Vehicle Enquiry Service API provides official vehicle information directly from a government source and covers vehicles in Great Britain, where HelpBot's users are primarily based. It is free to use under the Open Government Licence, which fits the project's free-tier budget.

Manual data collection was considered but would require significant effort to maintain and keep accurate over time. Vehicle information changes regularly, making this approach difficult to sustain.

The DVLA API allows registration numbers to be used to retrieve information such as the vehicle make, year of manufacture, engine size, fuel type, colour, tax status, and MOT status. This information can be used to improve the user experience by automatically populating part of the vehicle profile rather than requiring all details to be entered manually.

**Trade-offs Accepted:**  
The application becomes dependent on a third-party service and is therefore affected by API rate limits, downtime, or future changes to the service.

At the time of review (November 2026), DVLA is not accepting new API registrations while it upgrades its systems, and no key has yet been issued for HelpBot. Until registration reopens, vehicle profiles fall back to manual entry, the option rejected above, so the application must work fully without the API.

The API returns the vehicle make but not the model, so users must still enter the model and any other missing details themselves. It also covers Great Britain only, so it cannot be relied on for vehicles registered elsewhere in the UK.

DVLA treats vehicle registration numbers as sensitive information, in line with guidance from the Information Commissioner's Office, and requires them to be sent in the request body rather than the URL. Sending registration numbers to the API introduces privacy considerations that must be handled within the application's privacy policy and data protection processes.

**Sources:**

Department for Transport. (2022). *Vehicle enquiry service API*. https://findtransportdata.dft.gov.uk/dataset/vehicle-enquiry-service-api-178ab5990ef

Driver and Vehicle Licensing Agency. (n.d.). *Vehicle enquiry service (VES) API guide*. https://developer-portal.driver-vehicle-licensing.api.gov.uk/apis/vehicle-enquiry-service/vehicle-enquiry-service-description.html

<!--
## N. Title

**Date:**

**Context:**

**Options Considered:**

**Decision:**

**Reasons:**

**Trade-offs Accepted:**

**Sources:**
-->