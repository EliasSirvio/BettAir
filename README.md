# BettAir: A Fuzzy Recommender System for Strategic Placement of Green Areas

This project is done as part of the course _Fuzzy Sets and Systems_
for the [Swiss Joint Master of Science in Computer Science](https://mcs.unibnf.ch/)

## Report
Please refer to the [Project Report](./report.md) for a full description of our project.

## Installation

### Requirements

Python version 3.13

> [!NOTE]
> This guide assists in setting up Python dependencies. 
> If you're already comfortable with Python, feel free to use your preferred setup process.

### Linux / macOS setup

1. Verify your **Python version**:

```bash
python3 --version
```

2. Create a **virtual environment**:

```bash
python3 -m venv venv
```

3. **Activate** the virtual environment:

```bash
source venv/bin/activate
```

4. **Install libraries**

With the virtual environment activated, **install the required dependencies**:

```
pip install --upgrade pip
pip install -r requirements.txt
```



### Windows setup

As an alternative **use WSL2** (Windows Subsystem for Linux) and apply the steps from the Linux step.
Otherwise, continue:

1. Verify your **Python version**:

```shell
python --version
```

2. Create a **virtual environment**:

```bash
python -m venv venv
```

3. **Activate** the virtual environment:

```bash
venv\Scripts\activate
```

4. **Install libraries**

With the virtual environment activated, **install the required dependencies**:

```
pip install --upgrade pip
pip install -r requirements.txt

```

5. **Run program**

To run the bokeh_plot_app, run the following commands:

```
CD bokeh_plot_app
python main.py

```
The program will then add the stations and generate the map. The default location of the app is London. 
If you wish to try with another location, modify bokeh_plot_app/main.py with for example:

real_location_ids = [
    1541052, 11587, 784135, 10837, 784137, 11588
]

This will give you a map of the airquality in Belgrade.

To run the offline version:

```
CD offline_app
python main.py

```
