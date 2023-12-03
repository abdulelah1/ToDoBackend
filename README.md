# ToDoBackend

This app assumes that you have PostgreSQL Server running, and a database created, then the app will create the needed tables.

You need to put the Database credentials in .env file

## Preparing the environment

### Installing Python Modeules
`pip install -r requirements.txt`

### Installing wkhtmltopdf so the App can make PDF 

Follow this documentation:
https://thepythoncode.com/article/convert-html-to-pdf-in-python#installing

### .env File

The .env file must have the following:

`
DB_USER=
DB_PASSWORD=
DB_NAME=
DB_HOST=
ENCRYPTION_KEY=
ENCRYPTION_ALGO=
`


