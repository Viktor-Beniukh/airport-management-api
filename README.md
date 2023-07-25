# Airport Management API

API service for airport management with the ability to make ordering and payment tickets online


### Installing using GitHub

- Python3 must be already installed
- Install PostgreSQL and create db

```shell
git clone https://github.com/Viktor-Beniukh/airport-management-api.git
cd airport-management-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver   
```
You need to create `.env` file and add there the variables with your according values:
- `POSTGRES_DB`: this is databases name;
- `POSTGRES_USER`: this is username for databases;
- `POSTGRES_PASSWORD`: this is username password for databases;
- `POSTGRES_HOST`: this is host name for databases;
- `POSTGRES_PORT`: this is port for databases;
- `SECRET_KEY`: this is Django Secret Key - by default is set automatically when you create a Django project.
                You can generate a new key, if you want, by following the link: `https://djecrety.ir`;
- `STRIPE_PUBLIC_KEY` & `STRIPE_SECRET_KEY`: your keys received after registration on the Stripe website.


## Run with docker

Docker should be installed

- Create docker image: `docker-compose build`
- Run docker app: `docker-compose up`


## Getting access

- Create user via /api/user/register/
- Get access token via /api/user/token/


## Features

- JWT authentication;
- Admin panel /admin/;
- Documentation is located at /api/doc/swagger/;
- Creating airport types, airports, airplanes, routes, crews (only admin);
- Creating flights with airplanes and routes (only admin);
- Filtering airports by name;
- Filtering airplanes by name and airplane types;
- Filtering routes by source and destination;
- Filtering crews by position;
- Filtering flights by airplane name, source and destination;
- Managing orders and tickets, and also their payment (authenticated users);


### How to create superuser
- Run `docker-compose up` command, and check with `docker ps`, that 2 services are up and running;
- Create new admin user. Enter container `docker exec -it <container_name> bash`, and create in from there;


### What do APIs do

- [GET] /airplanes/ - obtains a list of airplanes with the possibility of filtering by name and type;
- [GET] /airports/ - obtains a list of airports with the possibility of filtering by name;
- [GET] /routes/ - obtains a list of routes with the possibility of filtering by source and destination;
- [GET] /crews/ - obtains a list of crews with the possibility of filtering by position;
- [GET] /flights/ - obtains a list of flights with the possibility of filtering by airplane name, source and destination;
- [GET] /orders/ - browses users order history page;
- [GET] /payment/ - obtains a list of payments of orders;

- [GET] /airplanes/id/ - obtains the specific airplane information data;
- [GET] /crews/id/ - obtains the specific crew data;
- [GET] /flights/id/ - obtains the specific flight data;
- [GET] /payment/id/ - obtains the specific payment order data;

- [POST] /airplane-types/ - creates an airplane type;
- [POST] /airplanes/ - creates an airplane;
- [POST] /airports/ - creates an airport;
- [POST] /routes/ - creates a route of a flight;
- [POST] /crews/ - creates a member of a crew;
- [POST] /flights/ - creates a flight data;
- [POST] /orders/ - creates an order of tickets for the user;
- [POST] /payment/ - creates a payment of order of tickets;
- [POST] /payment/<id>/create-session/ - redirects to payment page;

- [GET] /success/ - check successful stripe payment;
- [GET] /cancelled/ - return payment paused message;

- [GET] /api/user/me/ - obtains the specific user information data;

- [POST] /api/user/register/ - creates new users;
- [POST] /api/user/token/ - creates token pair for user;
- [POST] /api/user/token/refresh/ - gets new access token for user by refresh token;
- [POST] /api/user/token/verify/ - validates user access token;

- [PUT] /api/user/me/ - updates the specific user information data;


### Checking the endpoints functionality
- You can see detailed APIs at swagger page: `http://127.0.0.1:8000/api/doc/swagger/`.


## Testing

- Run tests using different approach: `docker-compose run app sh -c "python manage.py test"`;
- If needed, also check the flake8: `docker-compose run app sh -c "flake8"`.


## Check project functionality

Superuser credentials for test the functionality of this project:
- email address: `migrated@admin.com`;
- password: `migratedpassword`.


## Create token pair for user

Token page: `http://127.0.0.1:8000/api/user/token/`

Enter:
- email address: `migrated@admin.com`;
- password: `migratedpassword`.
