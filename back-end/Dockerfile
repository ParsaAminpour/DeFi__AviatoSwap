# FROM django:onbuild

FROM python:3

ENV PYTHONUNBUFFERED=1
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY . . 
EXPOSE 8000
# CMD [python3,manage.py,runserver]
# FROM python:3.4

# RUN apt-get update \
#     && apt-get install -y --no-install-recommands \
#         postgresql-client \
#     && rm -rf /var/lib/apt/lists/*

# WORKDIR /usr/src/app

# COPY requirements.txt ./

# RUN pip3 install -r requirements.txt

# COPY . .

# EXPOSE 8000

# CMD ['python3','manage.py','runserver']


# # FROM django:onbuild

# # # after this line will run automaticly in this image(docker), but I wrote here just for remebering what wxactly will happen
# # COPY . /usr/src/app

# # RUN pip3 install 
# # RUN pip3 install -r requirements.txt 

# # EXPOSE 8000

# # CMD ["python3", "manage.py", "runserver"]