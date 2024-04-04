#!/bin/bash

docker run -it --user=$(id -u):$(id -g) -v $(pwd):/usr/src/app my-project-container-name bash -c "source /opt/conda/etc/profile.d/conda.sh && conda activate myenv && python $1"


