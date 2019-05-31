Slope extractor
===============

Installation instructions tested on Ubuntu 18.04

1. Create a virtualenv: `$ python3.6 -m venv env`
2. Activate it: `$ . env/bin/activate`
3. Update pip: `$ pip install --upgrade pip`
4. Install requirements: `$ pip install -r requirements.txt`

Usage:
1. Activate the environment: `$ . env/bin/activate`
1. Run with a cvs data file as first argument: `$ ./get_slopes.py pressure_sensor.csv`

It will open a plot where the different positive slopes are colored:
![image](https://user-images.githubusercontent.com/764126/58719730-b3884800-83d0-11e9-8b60-a047adfb7e8c.png)

And it will write one csv file per positive slope in a new directory called `files`, each one of those files will contain the
'chunk' of cvs that correspond to each of the slopes.
