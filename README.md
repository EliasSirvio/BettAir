# Fuzzy logic tutorial

This tutorial is part of the course _Fuzzy Sets and Systems_
for the [Swiss Joint Master of Science in Computer Science](https://mcs.unibnf.ch/). 
It introduces the use of fuzzy logic algorithms in Python, 
utilizing the [`scikit-fuzzy`](https://scikit-fuzzy.github.io/scikit-fuzzy/) library.

The tutorial instructions are based on examples provided by the `scikit-fuzzy` library.

## Requirements

Python version 3.9, 3.10, or 3.11 (3.12 not yet supported).

## Installation

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

### Docker

If you encounter issues with the setup above, you can use [Docker](https://docs.docker.com/get-docker/) to run the environment.

1. **Build** the Docker image

This command will build a Docker image and install the necessary libraries:

```bash
docker build -t fuzzy-notebook:latest .
```

2. **Run** the Docker container:

Use the following command to start the JupyterLab server in a Docker container:

```bash
docker run -it --rm -p 10000:8888 -v "${PWD}":/home/jovyan/work fuzzy-notebook:latest
```

If you are on Windows (without WSL), replace `"${PWD}"` with `%cd%`.

3. **Access** JupyterLab:

Open your browser and go to http://localhost:10000/lab?token=YOUR_TOKEN_IN_CONSOLE (note the port `10000`).
Replace `YOUR_TOKEN_IN_CONSOLE` with the token displayed in your terminal after running the container. 


## Tutorials

Start with the [Introduction](./Introduction.md), which provides an overview 
of fuzzy logic concepts and terminology. This is recommended as the first step.

This course includes two tutorial notebooks:

* **01_FuzzyControlSystem.ipynb**: Introduction to fuzzy control systems.
* **02_FuzzyClustering.ipynb**: Introduction to fuzzy clustering techniques.

Work through these notebooks in order.

## Deliverable

After completing the tutorials, create your own Jupyter notebook applying one of the approaches to a problem.

1. **Select a domain**: choose a domain related to your group project (if already available) or a personal interest. 
2. **Create and name your notebook**: experiment with the chosen approach and save your notebook as `03_<YourProjectName>.ipynb`. 
3. **Push to your repository**: upload your completed notebook to your GitHub repository (_including_ the output).



2caa6fe0fe5066bc5d382ec56ee1bcea909f0874444db7983cf39353caa408b2