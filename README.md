# GitHub Crawler


## Overview

This project crawls 100,000 GitHub repositories and stores their star counts in a PostgreSQL database.  

## Architecture


```
src/
├── models/          # Domain models (immutable data classes)
├── infra/           # Infrastructure layer (API clients, database)
├── services/        # Application services (business logic)
├── config/          # Configuration management
└── main.py          # Entry point
```


## Database Schema

The schema uses a **normalized, time-series approach** for efficient updates:

```sql
-- Core repository data (relatively static)
repositories (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255),
    owner_name VARCHAR(255)
)

-- Time-series metrics (frequently changing)
repository_metrics (
    id SERIAL PRIMARY KEY,
    repository_id BIGINT REFERENCES repositories(id),
    stars_count INTEGER,
    recorded_at TIMESTAMP WITH TIME ZONE
)
```


## Setup

### Prerequisites

- Python
- PostgreSQL
- GitHub Personal Access Token (with `public_repo` scope)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd github-crawler
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file:
   ```env
   GITHUB_TOKEN=your_github_token_here
   DATABASE_URL=postgresql://user:password@localhost:5432/github_crawler
   ```

5. **Initialize the database**
   ```bash
   psql -U postgres -d github_crawler -f schemas/schema.sql
   ```

6. **Run the crawler**
   ```bash
   python -m src.main
   ```


## Performance Considerations

### Rate Limiting

- **Proactive Rate Limit Handling**: Monitors remaining API calls and waits before limits are exhausted
- **Exponential Backoff**: Retries failed requests with exponential backoff
- **GraphQL Efficiency**: Uses GraphQL to fetch multiple repositories per request (up to 100 per query)

### Database Optimization

- **Batch Inserts**: Uses `execute_batch` for efficient bulk inserts
- **UPSERT Pattern**: Uses `ON CONFLICT` to handle duplicate repositories gracefully

## Scalibility Considerations

### Schema Evolution

The current database schema is designed with extensibility in mind. If the schema needs to evolve in the future to accommodate additional metadata (such as issues, pull requests, commits, comments, reviews, or CI checks), the existing normalized, time-series design can be easily extended without requiring significant changes to the current implementation.

- **Current Schema**:
   ![Current Schema](/assets/current.png)
- **Extended Schema**:
   ![Extended Schema](/assets/updated.png)
### Handling 5 Million Repositories:

To scale the system for 5 million repositories, we can implement the following approaches:

- **Parallel Processing**: Implement a multi-worker architecture where the crawling workload is divided into batches and distributed across multiple workers for concurrent processing.

- **Caching Strategy**: Implement a caching layer to store recently fetched or unchanged repository data, reducing redundant API calls and improving overall crawl efficiency.

- **Token Rotation**: Utilize multiple GitHub API tokens and implement a rotation mechanism to effectively manage rate limits while ensuring continuous data fetching across all desired repositories.