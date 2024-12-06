# BettAir: A Fuzzy Recommender System for Strategic Placement of Green Areas

This project is done as part of the course _Fuzzy Sets and Systems_
for the [Swiss Joint Master of Science in Computer Science](https://mcs.unibnf.ch/)

## Report
Please refer to the [Project Report](./report.md) for a full description of our project.

## Installation

### Requirements

Python version 3.9, 3.10, or 3.11 (3.12 not yet supported).

> [!NOTE]
> This guide assists in setting up JupyterLab and Python dependencies. 
> If you're already comfortable with Python, feel free to use your preferred setup process.

First, **fork and clone this repository**, or download it manually to your computer. 
Then open a terminal inside the repository and proceed.

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
pip install jupyterlab
```

5. **Start JupyterLab**:

```bash
jupyter lab
```

This should open a local web interface (or display a URL) for JupyterLab, where you can access the tutorial notebooks.


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
pip install jupyterlab
```

5. **Start JupyterLab**:

```bash
jupyter lab
```

This command should open a local web interface (or display a URL) for JupyterLab, where you can access the tutorial notebooks.
