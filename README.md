# Group 5 - Sustainable-City-Management project

Group 5 - Sustainable-City-Management project. 

## BACKEND SETUP

### Virtualenv Reference: 
https://uoa-eresearch.github.io/eresearch-cookbook/recipe/2014/11/26/python-virtual-env/


### Installing the requirements for Backend:
After activating the virtual environment, please follow the steps below: 

1. Install `pip-tools`:
    ```
    pip install pip-tools
    ```

2. Run the command `pip-compile` to get the updated `requirements.txt` file.

3. Install the requirements by running:
    ```
    pip install -r requirements.txt
    ```

4. In-case if adding any new dependencies, update only the `requirements.in` file with the name & version and then again run `pip-compile` to update the `.txt` file and then install the required the dependencies by:
    ```
    pip install -r requirements.txt
    ```


## FRONTEND SETUP

1. Open Command-Prompt
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
7. cd into the frontend directory and run:
    ```
    npm install
    ```
    This will install the required node dependencies into `node_modules/`
8. Once done, run the project using the following:
    ```
    npm start
    ```


# Happy Coding !!
