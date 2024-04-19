# Group 5 - Sustainable-City-Management project

Group 5 - Sustainable-City-Management project. 


# Project Video 
> (Pro tip: Click on the image to view the video.):

[![PROJECT VIDEO](https://img.youtube.com/vi/VgQYaTe-VoM/0.jpg)](https://youtu.be/VgQYaTe-VoM)

# DEPLOYED PROJECT AT:
Copy and paste the url into the Browser to access the APP deployed on AWS. Make sure that you are not connected to `TCDWifi` since it blocks the AWS access!


http://frontend-scm-1232923463.ap-south-1.elb.amazonaws.com/

The app will be live until 25th May 2024, after which it will no longer be accesible due to the cost limitations and constraints. The billing increases exponentially when the app is kept running for longer periods and currently we do not have any provision to support these kinds of costs.


If any other issue, please do let us know and we can manually restart the app for easier access and visibility.


# Compile Instructions for Local Setup:
> NOTE: Please don't change any '`.env`' files for the compile instructions!

## BACKEND SETUP

### POSTGRES SETUP
To initialize the PostgreSQL Database, please follow the below steps:

1. Download the postgresql installer from the following website here [https://www.postgresql.org/download/] and follow the installer steps. In the installer please ensure to check the below items as shown in the figure below:
    <figure align="center">
    <img src="https://i.postimg.cc/4yRYLvDZ/postgres-ss.png"/>
    </figure>
2. Once installation is complete, verify that by openining the `pgAdmin` Application.
3. Ensure that the postgresql service is running by going into `services` of windows machine and checking if it is running or not.
4. Then, Open the `pgAdmin` Application again and follow the below steps to create a Database. (Please ensure the creds are same as described below to avoid any unneccessary errors):
    1. Right Click on the `servers` and click on `Register` -> `Server..`
    2. Then inside the popup, please fill in the values as shown in the screenshot below for each of the tabs:
        <figure align="center">
        <img src="https://i.postimg.cc/0QRSFqSL/pgadmin1.png"/>
        </figure>

        Then in the `Connection` tab, please input the following and enter the password as '`admin`' and check the `Save password` option:

        <figure align="center">
        <img src="https://i.postimg.cc/HLCsCWS4/pgadmin2.png"/>
        </figure>
    3. Click on Save to register the server.
    4. Once the server gets registered, right click on the server and select `Create` -> `Database...`
    5. In the dialog popup, enter the database name as `scm` as shown in the below figure:
        <figure align="center">
        <img src="https://i.postimg.cc/htKQ9rnq/pgadmin3.png"/>
        </figure>
    6. Click on Save to create the Database.
5. Done! The DataBase setup is now complete!


### Virtualenv Reference: 
https://uoa-eresearch.github.io/eresearch-cookbook/recipe/2014/11/26/python-virtual-env/


### Installing the requirements for Backend:
After activating the virtual environment, please follow the steps below: 

1. CD into the Backend directory by:
    ```
    cd SCM/Backend
    ```

2. Install `pip-tools`:
    ```
    pip install pip-tools
    ```

3. Run the command `pip-compile` to get the updated `requirements.txt` file.

4. Install the requirements by running:
    ```
    pip install -r requirements.txt
    ```

5. In-case if adding any new dependencies, update only the `requirements.in` file with the name & version and then again run `pip-compile` to update the `.txt` file and then install the required the dependencies by:
    ```
    pip install -r requirements.txt
    ```

### Setting up the server:
After installing the requirements for the backend, please follow the steps below:

1. Migrate the db tables by running:
    ```
    python manage.py migrate
    ```

2. After successful migration, we need to pre-populate the DB with some data. This can be done using the following commands below: (Please Ensure these are run in specific order as below else it might create problems in the DB Relationships)
    ```
    python manage.py createsuperuser
    ```
    Upon prompt, give the desired email and password to the above. Can bypass the password check by entering 'y' when prompted.
    Use 
    Next, run the below commands in order specified in each line one by one (SOME MIGHT REQUIRE LONG TIMES DUE TO DATA LOADING, PLEASE DONT QUIT IN BETWEEN!):
    ```
    python manage.py runscript load_busdata
    python manage.py runscript load_busstopsdata
    python manage.py runscript load_dublinbikesstations
    python manage.py runscript load_energy
    python manage.py runscript load_sensors_and_sensor_data
    ```
3. Once prepopulated successfully, we can now proceed to run the server by running:
    ```
    python manage.py runserver
    ```

## FRONTEND SETUP

1. Open New Command-Prompt
2. Install NVM-Windows from the following link: [nvm-windows](https://github.com/coreybutler/nvm-windows)
3. Re-launch the Command-Prompt and run the following command:
    ```
    nvm -v
    ```
    It should print the nvm version (1.1.11). If not, please reinstall the nvm from step 2.
4. Run the install command to install nodejs in system:
    ```
    nvm install 20.9.0
    ```
    This command install nodejs=20.9.0 which is the current LTS verson.
5. Once installed, verify the node version using:
    ```
    node -v
    ```
6. After install, reinstalling global utilities (e.g. yarn) will have to be done for each installed version of node:
    ```
    nvm use 20.9.0
    npm install -g yarn
    ```
    Nvm use command tells the nvm to use the 20.9.0 version of the nodejs installed in the pervious step.
7. CD into the Frontend directory by:
    ```
    cd SCM/Frontend
    ```
8. Then install the required node dependencies into `node_modules/` by running:
    ```
    npm install
    ```
9. Once done, run the project using the following:
    ```
    npm start
    ```
10. Use the Login email & password from the backend setup step no. 2 for logging into the application
11. Inorder to register a new user, please follow the below steps:
    1. Goto the `http://localhost:8000/auth/whitelist/`, it will open a interactive UI like below:
        <figure align="center">
        <img src="https://i.postimg.cc/xd6mjFXd/whitelist.png"/>
        </figure>
    2. Copy and Paste the following in the `Content` section (replace the email with your desired email to add to whitelist users):
        ```
        {
            "email":"yournewemail@gmail.com"
        }
        ```
    3. Click on the `POST` button on bottom right corner.
12. Once done, navigate to the application register page and enter your details but make sure to use the email set in the previous step.

# Happy Coding !!
