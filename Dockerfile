FROM tensorflow/tensorflow


# Create worker directory
WORKDIR /usr/src/worker

# Copying the requirements
COPY requirements.txt ./

# fix for OpenCV on tensorflow image
RUN apt-get install -y libsm6 libxext6 libxrender-dev

# Installing dependencies
RUN pip install -r requirements.txt

# Copying the files over
COPY . .

CMD [ "python", "worker.py" ]
