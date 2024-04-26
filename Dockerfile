FROM python:3.12

WORKDIR /app

# copy requirements file to the current directory (i.e. /app) in container
COPY ./src/requirements.txt ./

# install the packages from requirements file (without caching the installation files)
RUN pip install --no-cache-dir -r requirements.txt

# copy all the contents from the `src` directory to the `src` folder in container's current directory
# (since docker caches each step in this file sequentially, we first just copied the requirements.txt file and installed the packages.
# so that the next time we change something in our source directory and re-build the image, docker can avoid executing pip install step again
# and just re-execute the actions from this step forward)
COPY ./src ./src/

# set the require env variables
ENV DB_USER=postgres_user
ENV DB_PASSWORD=dbpassword

# finally, run the flask app
CMD ["python", "src/app.py"]