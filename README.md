# CRM Dashboard

A full-featured CRM analytics dashboard for sales teams, built with MySQL, Python, Streamlit, and Docker. This project demonstrates data modeling, SQL analytics, dashboarding, and business metrics tracking—ideal for business analyst and data engineering roles.

## Features

- Relational schema for CRM entities (leads, customers, opportunities, activities, users, sources, stages)
- KPI dashboard: new leads/week, conversion rates, pipeline value, average time in stage, win rate, top sources
- CRUD operations, CSV import/export, search & filters
- Role-based access (rep, manager, admin)
- Synthetic seed data for demo/testing
- Dockerized MySQL database
- Streamlit dashboard UI
- Example SQL queries for analytics

## Tech Stack

- **Backend/DB:** MySQL (via Docker)
- **ETL/Analysis:** Python (pandas, SQLAlchemy, Faker)
- **Dashboard:** Streamlit, Plotly
- **Environment:** Docker, .env config
- **Version Control:** GitHub

## Project Structure

```
CRM_Database/
├── app/
│   └── streamlit_app.py         # Streamlit dashboard app
├── db/
│   ├── 01_create_schema.sql     # MySQL schema
│   ├── 02_indexes.sql           # Indexes for performance
│   └── queries.sql              # Example analytics queries
├── seed/
│   └── seed_data.py             # Synthetic data generator
├── docker-compose.yml           # MySQL container setup
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (not tracked)
├── .gitignore                   # Git exclusions
└── README.md                    # Project documentation
```

## Setup Instructions

### 1. Clone the Repository

```sh
git clone https://github.com/Archit-k20/CRM-Dashboard.git
cd CRM_Database
```

### 2. Configure Environment

Create a `.env` file in the root directory:

```
MYSQL_USER=root
MYSQL_PASSWORD=Qwerty@69
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DB=crm_db
```

### 3. Start MySQL with Docker

```sh
docker-compose up -d
```

### 4. Create Database Schema

Run the schema and index scripts:

```sh
docker exec -i <mysql_container_name> mysql -u root -pQwerty@69 < db/01_create_schema.sql
docker exec -i <mysql_container_name> mysql -u root -pQwerty@69 < db/02_indexes.sql
```

Replace `<mysql_container_name>` with your actual container name (use `docker ps` to find it).

### 5. Seed the Database

Install Python dependencies:

```sh
pip install -r requirements.txt
```

Run the seed script:

```sh
python seed/seed_data.py
```

### 6. Launch the Streamlit Dashboard

```sh
streamlit run app/streamlit_app.py
```

## Example SQL Analytics

See `db/queries.sql` for:

- New leads per week
- Lead → Opportunity conversion rate
- Pipeline value by stage
- Average time in stage
- Win rate, top sources

## Screenshots

_Add screenshots of your dashboard here after running the app._

## Business KPIs Tracked

- New leads/week
- Lead → Opportunity conversion rate
- Pipeline value by stage
- Average time in stage
- Win rate
- Top sources by conversion

## How to Extend

- Add more entities (contacts, products)
- Integrate with real CRM APIs
- Add authentication and user management
- Deploy Streamlit app to Streamlit Cloud or Heroku

## License

MIT