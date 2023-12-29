### Hexlet tests and linter status:
[![Actions Status](https://github.com/StanislavSol/python-project-83/workflows/hexlet-check/badge.svg)](https://github.com/StanislavSol/python-project-83/actions)

### Code Clamate
<a href="https://codeclimate.com/github/StanislavSol/python-project-83/maintainability"><img src="https://api.codeclimate.com/v1/badges/1604a4145450bc957ef0/maintainability" /></a>

[Page Analyzer](https://python-project-83-mv6t.onrender.com/) - is a site that analyzes specified pages for SEO suitability.

***
## Before installation
To install and run the project, you will need Python version 3.10 and above, the Poetry dependency management tool.

## Install
1. Clone the project repository to your local device:
```
git@github.com:StanislavSol/Page_Analyzer.git

```
2. Go to the project directory and install dependencies using Poetry:
```
cd python-project-52 && make build

```
3. Create a .env file that will contain your sensitive settings:
```
SECRET_KEY=your_key
DATABASE_URL = postgresql://{user}:{password}@{host}:{port}/{db}

```

***
## Usege
1. To start the server in a production environment using Gunicorn, run the command:
```
make start

```
2. Run the server locally in development mode with the debugger active:
```
make dev

```
