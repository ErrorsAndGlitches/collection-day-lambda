from continuumio/miniconda3:4.5.12

ENV project_name collection-day-lambda

# Set up environment and dependencies
RUN apt-get update --fix-missing && \
  apt-get install -y build-essential autoconf libtool zip

COPY environment-docker.yml .
RUN conda env create -f environment-docker.yml
RUN echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc

# Copy workspace
WORKDIR /opt/${project_name}/

COPY cdl cdl
COPY tests tests
COPY setup.py setup.cfg /opt/${project_name}/

# Run tests
RUN /bin/bash -c "source activate ${project_name} && python setup.py test"

# Create the AWS Lambda archive
ENV zip_output_file /opt/lambda-archive-collection-day-lambda.zip

RUN cd /opt/conda/envs/${project_name}/lib/python3.7/site-packages/ && \
  zip -r ${zip_output_file} . -x '*__pycache__*' && \
  cd /opt/${project_name}/ && \
  zip -gr ${zip_output_file} cdl -x '*__pycache__*'
