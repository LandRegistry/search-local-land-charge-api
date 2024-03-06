# Search Local Land Charges Api

This repository manages the search for local land charges database part of the Search for Local Land Charges application.This application allows you to retrieve a registered Search for Local Land Charges user's search history.

This application is built to run on our common development environment (common dev-env), which you can read more about here: https://github.com/LandRegistry/common-dev-env


### Unit tests

To run the unit tests if you are using the common dev-env use the following command:
```
docker-compose exec search-local-land-charge-api make unittest
or (using the alias)
unit-test search-local-land-charge-api
```


### Delete users script

`docker exec search-local-land-charge-api python delete_inactive_users.py`


```
usage: delete_inactive_users.py [-h] -m  [-a] -k

Deletes inactive users

optional arguments:
  -h, --help        show this help message and exit
  -m , --months     months of inactivity
  -a , --auth-url   URL of authentication-api, defaults to http://dev-search-
                    authentication-api:8080/v2.0
  -k , --api-key    api key to authorise access with
```
