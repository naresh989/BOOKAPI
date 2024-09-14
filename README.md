﻿# BOOKFASTAPI
Virtual Environment Creation
Begin by creating a virtual environment using the built-in Python module venv. If you already have Python installed, you might not need to install it separately. However, on Linux, installation may be necessary based on your distribution. In your commandline or terminal, type the following command.


python3 -m venv env
This command generates a virtual environment in the specified folder (in our example, env). This folder is an isolated Python environment which shall separate the dependencies of our project from the system wide Python installation.

Activate the virtual environment using the following commands:

On Linux or macOS:


source env/bin/activate
On Windows:


env/Scripts/activate
Once activated, your command line will indicate the active virtual environment:

On Linux or macOS:


(env) yourusername@yourmachine$
On Windows:


(env) C:\users\YourUsername>
2. Directory Structure
At this point, your directory structure should look like this:


└── env
3. Installing FastAPI
Now, let us install FastAPI within the virtual environment. We shall install FastAPI with the pip using the following command.


(env) pip install fastapi
4. Freeze Dependencies
Freeze the installed dependencies into a requirements.txt file to track the exact versions of our dependencies so that we can easily reproduce them in the future.


(env) pip freeze > requirements.txt
5. Confirm the installation
Let us confirm our fastapi installation by running the following command.


(env) fastapi --version
FastAPI CLI version: 0.0.2
This command shall show us the version of FastAPI CLI the FastAPI commandline interface.
