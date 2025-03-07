
# Project Metrics Analyzer

**Team 5**

- **Akshat Jain**
- **Jeteish**
- **Srinivas Oguri**
- **Sarthak Avaiya**

## Table of Contents
1. [Getting Started](#getting-started)
2. [Using the Application](#using-the-application)
3. [Microservices Documentation](#testing-individual-microservices)
4. [API Documentation](#api-documentation)
5. [Notes](#notes)

## Getting Started

### Prerequisites
- Docker and Docker Compose installed.
- Git Bash (windows) for using runner script

### Run the Application

#### Using the Runner Script:

```bash
./runner.sh
```

The application will automatically open in your default browser.

#### Using Docker Compose:

```bash
docker-compose down -v --remove-orphans  
docker network prune  
docker-compose build --no-cache  
docker-compose up  
```

Access the application at: [http://localhost:5000/home](http://localhost:5000/home).

## Using the Application

1. Navigate to the home page: [http://localhost:5000/home](http://localhost:5000/home).
2. Paste a GitHub repository URL into the input field.
3. Select a metric from the dropdown:
   - LOC (Lines of Code)
   - Code Churn
   - MTTR (Mean Time to Resolve)

   **Code Churn Specific**:
   - Enter the number of commits to analyze (must be ≤ total commits).

   **MTTR Note**:
   - Requires the repository to have issues.

4. View results in two graphs:
   - Modified: Custom implementation of the metric.
   - Online: Baseline from existing tools.

## Testing Individual Microservices

### LOC Microservice

**Directory**: `modules/LOC_api`

```bash
docker build --no-cache -t loc_api .
docker run -p 5002:5002 loc_api
```

**API Endpoint**:

POST [http://localhost:5002/loc](http://localhost:5002/loc)

**Request Body**:

```json
{
  "repo_url": "https://github.com/your-repo-url",
  "method": "online"  or "modified"
}
```

### Code Churn Microservice

**Directory**: `modules/CC_api`

```bash
docker build --no-cache -t cc_api .
docker run -p 5001:5001 cc_api
```

**API Endpoint**:

POST [http://localhost:5001/code-churn](http://localhost:5001/code-churn)

**Request Body**:

```json
{
  "repo_url": "https://github.com/your-repo-url",
  "method": "online",  or "modified"
  "num_commits_before_latest": 10
}
```

### MTTR Microservice

**Directory**: `modules/MTTR_api`

```bash
docker build --no-cache -t mttr_api .
docker run -p 5003:5003 mttr_api
```

**API Endpoint**:

POST [http://localhost:5003/mttr](http://localhost:5003/mttr)

**Request Body**:

```json
{
  "repo_url": "https://github.com/your-repo-url",
  "method": "online"  or "modified"
}
```

## API Documentation

### Main API Endpoint:

POST [http://localhost:5000/analyze](http://localhost:5000/analyze)

**Headers**:

```json
{
  "Content-Type": "application/json"
}
```

**Request Body**:

```json
{
  "metric": "loc",  # or "code-churn" or "mttr"
  "repo_url": "https://github.com/your-repo-url",
  "method": "online",  # or "modified"
  "num_commits_before_latest": 10  # Only for code-churn
}
```

## Notes

- **MTTR**: Ensure the repository has issues.
- **Code Churn**: `num_commits_before_latest` must be ≤ total commits.
- **Port Conflicts**: Ensure ports 5000-5003 are free.
