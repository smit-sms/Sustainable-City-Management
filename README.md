# Group 5 - Sustainable-City-Management project

Group 5 - Sustainable-City-Management project. 


## Virtualenv Reference: 
https://uoa-eresearch.github.io/eresearch-cookbook/recipe/2014/11/26/python-virtual-env/


## Installing the requirements for Backend:
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

Happy Coding !!
