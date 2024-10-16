# Web Application Exercise

A little exercise to build a web application following an agile development process. See the [instructions](instructions.md) for more detail.

## Team members
[Alvaro Martinez](https://github.com/AlvaroMartinezM)

[Natalie Ovcarov](https://github.com/nataliovcharov)

[Daniel Brito](https://github.com/danny031103 )

[Jun Li](https://github.com/jljune9li )

## Product vision statement

Our mobile web app allows people to be more organized by keeping track of their ongoing and completed tasks.

## User stories

1. As a busy person, I want to remind myself of the stuff I have to bring during moving so that I don’t leave important stuff behind
2. As a deadline-driven person, I want a central place to track all my important events and appointments, so I can manage my time effectively.
3. As a student with ADHD, I want to create tasks for organizing my study schedule so I can stay on top of my coursework and deadlines.
4. As a student,  I want to set reminders for upcoming exams to ensure I don’t miss important dates.
5. As a busy person, I want to remind myself about daily chores like cleaning and laundry to keep my living space tidy and organized.
6. As a busy person, I want to schedule exercise and relaxation breaks to balance my academic life with self-care.
7. As a busy person, I want to keep a list of errands, like grocery shopping or running to the library, so I can be more efficient with my time.
8. As a dog walker, I want to make sure I know when I am dog watching or dog walking.
9. As a person with two jobs, I want to manage the tasks I have for each of them to make sure I am getting everything done.
10. As a student, I want to manage my deadlines for homework.


## Steps necessary to run the software

## Install Python
Install Python on your local machine.

## Clone the repository to your local machine
```bash 
git clone https://github.com/software-students-fall2024/2-web-app-java_and_the_scripts.git
```

## Install Requirements
Install Flask and Pymongo, and other requirements on your local machine.
```bash 
pip3 install -r requirements.txt
```

## Install Docker
Install Docker on your local machine.

## Navigate into cloned directory using cd
Ensure that the current working directory is in the project.

## Configure .env file
Copy the provided contents of .env posted in the discord and create your own .env file located in the project folder.

## Boot up DB and Web App
Use Docker Compose to boot up both the `mongodb` database and the `flask-app` web app with one command:
```bash
 docker compose up --force-recreate --build
 ```

## Stop Containers
When done using application, stop docker containers using:
```bash 
docker compose down
```

## Error Messages
If you see an error message that a particular port is already in use, select a different port for either the `flask-app` or `mongodb` service, as necessary.  To do so, edit the first port number for that service in the `docker-compose.yml` file and try again. E.g., change the `flask-app`'s port to `12000:12000` if you want the flask app to run on port `12000` on your computer.  If changing the `flask-app` port in this way, you must also update the `FLASK_PORT` setting in the `docker-compose.yml` file to match

## View App
Open a web browser and go to `http://localhost:11000` (or change `11000` to whatever port number you used for the `flask-app`.)


## Task boards

[Task Board Sprint 1](https://github.com/orgs/software-students-fall2024/projects/25)
[Task Board Sprint 2](https://github.com/orgs/software-students-fall2024/projects/88/views/1)
 

