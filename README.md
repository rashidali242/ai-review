# Documentation

* create .env.local and .env.prod files inside application folder
```
FLASK_ENV=development  or production
FLASK_DEBUG=1   Or 0 for production
NAME=Local   (it can be anything)
```

* Install Docker setup
- Go to the root folder and run below command
```
docker-compose -f docker-compose-dev.yml up --build
```
If build is already exist then run
```
docker-compose -f docker-compose-dev.yml up -d
```

* Access application
```
http://localhost:5000/
```