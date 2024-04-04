# PythonDevContainer

A basis for Python development work in a containerized system (Docker). The initial example provides the basics for a data science development system, including JupyterLab. Packaging is based on Conda/Mamba. The example assumes the local user is UID 1000 / GID 1000.

## Installation and Usage

1. **Install prerequisites:**
   - Docker-CE or Docker Desktop

2. **Clone this repository:**

git clone <repository-url>


3. **Copy `Dockerfile` and `requirements.yml` to the base directory of your project.**

4. **Modify `requirements.yml` to suit your project.**

This will likely involve adding packages needed for your project and setting the desired Python version.

5. **Build the container using `docker build`:**

docker build . -f Dockerfile -t my-project-container-name --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)

Replace `my-project-container-name` with something specific to your project.

6. **To run a JupyterLab instance, use the following command:**

docker run -it --user=$(id -u):$(id -g) -v $(pwd):/usr/src/app -p 8888:8888 my-project-container-name bash -c "source /opt/conda/etc/profile.d/conda.sh && conda activate myenv && jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --NotebookApp.token='' --NotebookApp.password=''"

Open a web browser and visit "http://localhost:8888".

7. **Interactive container invocation:**

docker run -it --user=$(id -u):$(id -g) -v $(pwd):/usr/src/app -p 8888:8888 my-project-container-name bash

This gives you a Bash prompt inside the container.

8. **Running a Python program:**

docker run -it --user=$(id -u):$(id -g) -v $(pwd):/usr/src/app my-project-container-name bash -c "source /opt/conda/etc/profile.d/conda.sh && conda activate myenv && python myprogram.py"

To simplify, consider using a script (e.g., `run.sh` or `run.bat`) for execution.

Example `run.sh` for Unix/Linux/macOS:
```bash
#!/bin/bash
docker run -it --user=$(id -u):$(id -g) -v $(pwd):/usr/src/app my-project-container-name bash -c "source /opt/conda/etc/profile.d/conda.sh && conda activate myenv && python $1"

Make it executable with chmod +x run.sh

## Caveats

This is intended for development purposes, not suitable for production without modifications (e.g., securing JupyterLab).

The Dockerfile and example Jupyter notebook were crafted with assistance from OpenAI's ChatGPT.

## Sharing the Container

To ensure exact reproduction of the environment, share both the Dockerfile and the container image. Here's how to save and share the Docker image:

  docker save my-project-container-name > my-project-container-name.tar

To load the image on another system:

  docker load < my-project-container-name.tar

Alternatively, specify exact package versions in requirements.yml to aid reproducibility.

