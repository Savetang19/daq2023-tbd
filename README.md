# TBD-My-Little-Farm
Project from 01219335 - Data Acquisition and Integration
## Team members 
### Department of Software and Knowledge Engineering, Kasetsart University
- Thanida Chaiwongnon 6410545444
- Napasakorn Boonkerd 6410545487
- Maroj Thangthong 6410546238
- Siravich Termvadsayanon 6410546297
- Tanabodee Yambangyang 6410545754

## Project Overview & Features
Our API offers comprehensive environment control for users managing various aspects of our farm surroundings. For plant care, it provides insights on when to water based on real-time weather conditions, soil moisture levels, humidity, and light intensity. Additionally, it will recommend to open or close sunshades by considering ambient light intensity (lux). For roof control, the API factors in weather patterns and rainfall, allowing users to open or close their roofs based on these environment conditions.

## Installation & Run

### How to install
make sure that you have [python](https://www.python.org/downloads/release/python-3913/) in your computer.
first, you need to create file name `config.py` to configuration
`config.py` file template looks like [config.py.example](config.py.example) you can modify value and copy it into `config.py`
**Note that you may get your config.py by contacted our team member via email.**

then, Generate server stubs for python-flask from openapi/tbd-api.yaml with [Swagger Editor](https://editor.swagger.io) or
OpenAPI Generator and Put them inside stub folder

next, you have to create environment by typing this command

```sh
python -m venv env
```

then, activate the environment using

```sh
env\Scripts\activate.bat # Windows
source env/bin/activate # macOS and Linux
```

the terminal will using environment now then typing this command to install requirements

```sh
pip install -r requirements.txt
```

### How to run

make sure you do all the install part, environment is activate and connect internet with KU-WIN network.

#### now, to run server typing this command

```sh
python app.py
```

go to `http://127.0.0.1:8080/tbd-api/v1/ui/` for application.
