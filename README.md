Team 5 
Jeteish
Akshat Jain
Srinivas Oguri
Sarthak Avaiya

# Command to build and run LOC API Image:

## LOC Docker image build
```docker build --no-cache -t loc_api .```

## LOC Docker image run
```docker run -p 5000:5000 loc_api```

## LOC API link
```http://127.0.0.1:5000/loc```

## LOC API request
enter repo link in place of your repo url and enter either cloc or codetabs in method field.

### request for windows terminal
```Invoke-WebRequest -Uri http://localhost:5000/loc -Method POST -ContentType "application/json" -Body '{"repo_url": "your repo url", "method": "cloc/codetabs"}'``` 
### request for mac/linux
```curl.exe -X POST http://localhost:5000/loc -H "Content-Type: application/json" -d {"repo_url": "your repo url", "method": "cloc/codetabs"}```


# Command to build and run CodeChurn API Image:

## CC Docker image build
```docker build --no-cache -t cc_api .```

## CC Docker image run
```docker run -p 5000:5000 cc_api```

## CC API link
```http://127.0.0.1:5000/cc```