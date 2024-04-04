# Use an official minimal Docker image with Miniconda installed (Miniforge variant)
FROM condaforge/miniforge3:latest

# User setup
# Assuming the host user's UID and GID are both 1000
ARG USER_ID=1000
ARG GROUP_ID=1000

# Create a group and user
RUN addgroup --gid $GROUP_ID user && \
    adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID user

# Change permissions to allow the non-root user to write to the Conda directory
RUN chown -R user:user /opt/conda

# Switch to the new user
USER user

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . /usr/src/app

# Install Mamba from Conda-Forge and use it to create a new environment and install packages
# Use mamba to create the Python environment as per the requirements.yml file
RUN conda install mamba -n base -c conda-forge && \
    echo "source activate myenv" > ~/.bashrc && \
    mamba env create -f /usr/src/app/requirements.yml

# Make port 8888 available to the world outside this container
EXPOSE 8888

# If you need other ports, define them here

# Define environment variable to ensure that Python outputs are sent straight to terminal without being first buffered
ENV PYTHONUNBUFFERED=1

RUN echo "source activate myenv" >> ~/.bashrc

# Use the new environment. Ensure commands run in the shell will use the `myenv` environment by default
SHELL ["/bin/bash", "--login", "-c"]

# Run JupyterLab on container start, making it accessible to your localhost
CMD ["jupyter", "lab", "--ip='*'", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
