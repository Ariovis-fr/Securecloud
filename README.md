# Securecloud

## Description

This is a simple SCIM app that allows you to manage users in your organization. It is built with Flask and SQLAlchemy.

## Dependencies

- Python 3.11
- MySQL 8.0

or

- Docker

## Installation

### From source

1. Clone the repository
2. Install the dependencies with `pip install -r requirements.txt`
3. Create your database in MySQL
4. Create a `.env` file with the following variables:
    - `CLIENT_ID`: The client ID of your OIDC provider
    - `CLIENT_SECRET`: The client secret of your OIDC provider
    - `AUTHORITY`: The authority URL of your OIDC provider
    - `REDIRECT_PATH`: The redirect path of your app
    - `SCIM_SECRET`: A secret key for SCIM operations
    - `DB_URL`: The URL of your database
    - `PORT`: The port on which the app will run
5. Run the migration with migrate.sh script `./migrate.sh` or by running following commands:
    - `python src/manage.py db init`
    - `python src/manage.py db migrate`
    - `python src/manage.py db upgrade`
6. Run the app with `python app.py`

### With Docker

1. Clone the repository
2. Configure the variables in the `docker-compose.yml` file
3. Run migrations with `docker-compose up migrations`
3. Run the app with `docker-compose up`

## Usage

You can use the app to manage users in your organization. You can update, delete, and list users. Creation of users is managed directly by the OIDC client.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.