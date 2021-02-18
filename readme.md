# Base Demo Project for Device Automation Server, AutoDeploy

## Deployment
- Run Project in virtual Enviroment 

    -  Install pipenv ``` pip install pipenv ```
    - Enter virtual env ``` pipenv shell ```
    - Start server ``` python manage.py runserver ```

## Deployment - Enviroment Variables
Due to security concerns a ``` .env ``` file must be used in order to provide secret keys and databse login creds in order for the server to function. The [python-dotenv](https://pypi.org/project/python-dotenv/) package is used to read in the env vars into the django project.
- Install ``` python-dotenv ```
    - Install within pipenv ``` pip install python-dotenv ```
    - Place ``` .env ``` in root of autodeploy directory
    - Restart server

## Super User Creds
Super used creds can be found in provided ``` super_user_auth.txt ```

## To Do
- [ ] AdminLTE Integration
- [ ] LDAP Integration
- [ ] Some form of sscript deployment
- [ ] User Permissions
- [x] Dasboard Struture and Flow Design, SEMI FINISHED

## Resources
Project Followed the [Django Login and Logout Tutorial](https://learndjango.com/tutorials/django-login-and-logout-tutorial) by Will Vincent

### Known Issues
- Downloading ```.env``` files from drive results in env file being saved as ```.txt``` file. Rename ``` env ``` file in root of AutoDeploy to ``` .env ```
