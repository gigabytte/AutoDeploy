# OTU Dashboard Automation Server

## Features
- Ability to add, remove and Edit Automation Scripts
- Ability to add, remove and edit endpoints in which scripts are deployed to
- Authentication of User Creds against LDAP Server
- Basic premission system of Script access to normal users and admins
- Ansible based modular backend

## Deployment
- Run Project in virtual Enviroment 

    -  Install pipenv ``` pip install pipenv ```
    - Enter virtual env ``` pipenv shell ```
    - Start server ``` python manage.py runserver 0.0.0.0:8000 ```

## Deployment - Enviroment Variables
Due to security concerns a ``` .env ``` file must be used in order to provide secret keys and databse login creds in order for the server to function. The [python-dotenv](https://pypi.org/project/python-dotenv/) package is used to read in the env vars into the django project.
- Install ``` python-dotenv ```
    - Install within pipenv ``` pip install python-dotenv ```
    - Place ``` .env ``` in root of autodeploy directory
    - Restart server

## Super User Creds
Super used creds can be found in provided ``` super_user_auth.txt ```

## To Do
- [x] AdminLTE Integration
- [x] LDAP Integration
- [x] Console creation, deletion and editing
- [x] Windows Device creation, deletion and editing
- [x] Script creation, deletion and editing
- [x] User Permissions (ie. who can access what devices and scripts)
- [x] Ability to View all Devices and Scripts in a dump format
- [ ] Integrate async subporcess backend for Ansible deployment
- [ ] Script deployment backend for consoles (In Dev)
- [ ] Script deployment backend for windows devices (ie. basic commands) (In Dev)
- [ ] Conversion of Scripts to Ansible based scripts
- [x] Dasboard Struture and Flow Design, SEMI FINISHED

## Resources
Project Followed the [Django Login and Logout Tutorial](https://learndjango.com/tutorials/django-login-and-logout-tutorial) by Will Vincent
Async [Subprocess](https://docs.python.org/3/library/subprocess.html) Backend
- [Stackoverflow](https://stackoverflow.com/questions/636561/how-can-i-run-an-external-command-asynchronously-from-python) topic on Subprocess

### Known Issues
- Deployment using ansible backend needs final dev
- Integrating an async method with frontend (Network and Windows Deployment Page) for logging Ansible output
- Dashaboard Settings Menu does not collapse on selection
- LDAPS does not function properly and returns Cert error on Login attempt
- Cannot update code for Script under Edit Script Section. User must currently delete and make new Script to update

