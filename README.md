# Team 5
Jeteish
Akshat Jain
Srinivas Oguri
Sarthak Avaiya

# Command to build Application:
To run the LOC microservice individually open the terminal at ```src```
### Start all the services:
```
    docker-compose down -v --remove-orphans
    docker network prune
    docker-compose up --build
```
### LOC API link:
```http://127.0.0.1:5000/analyze```

## Request Header:
```Content-Type : application/json```

## Request Body:
``` 
{
    "metric": "loc/code-churn/mttr",
    "repo_url": "https://github.com/you-repo-url",
    "method": "online/modified",
    "num_commits_before_latest": <integer value less than total number of commits>
}
```
# Command to build and run LOC API Image:
To run the LOC microservice individually open the terminal at ```modules/LOC_api```
### LOC Docker image build:
```docker build --no-cache -t loc_api .```

### LOC Docker image run:
```docker run -p 5002:5002 loc_api```

### LOC API link:
```http://127.0.0.1:5002/loc```

## Request Header:
```Content-Type : application/json```

## Request Body:
``` 
    {
        "repo_url": "https://github.com/your-repo-url", 
        "method": "online/modified",
    }
```

# Command to build and run CodeChurn API Image:
To run the Code churn microservice individually open the terminal at ```modules/LOC_api```
## CC Docker image build
```docker build --no-cache -t cc_api .```

## CC Docker image run
```docker run -p 5001:5001 cc_api```

## CC API link
```http://127.0.0.1:5001/code-churn```

## Request Header:
```Content-Type : application/json```

## Request Body:
``` 
    {
        "repo_url": "https://github.com/your-repo-url", 
        "method": "online/modified",
    }
```

# Command to build and run MTTR API Image:
To run the MTTR microservice individually open the terminal at ```modules/LOC_api```
## MTTR Docker image build
```docker build --no-cache -t mttr_api .```

## MTTR Docker image run
```docker run -p 5003:5003 mttr_api```

## MTTR API link
```http://127.0.0.1:5003/mttr```

## Request Header:
```Content-Type : application/json```

## Request Body:
``` 
    {
        "repo_url": "https://github.com/your-repo-url", 
        "method": "online/modified",
    }
```