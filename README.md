## GOLDWORTH LMS Documentation

## What is GoldWorth?
## Goldworth is a Learning Management System, that focuses on bridging the gap between old and newer models of delivering knowledge to its users. Goldworth is Education based, aand therefore seeks to make the process of studying, accessing materials, uploading materials, viewing references and many more easily accessible to the user

## Target Audience
## Goldworth seeks to meet the needs of a wide variety os users including teachers, parenst and its most important user group, the students.

1. Students
    # Goldworth allows students to express interest in their said course so as to stand a chance at enrollment in one of the leading online educational platforms. The students have at their disposal, reference material as provided by their teachers, ability to scheme through the course of their choice, give feedback as well as viewing their progress from an entrie dashboard dedicated soley to them.

2. Teachers
    # Instructors at Goldworth can take advantage of technology to influence the lives of students and their parents through the engaging platform. The are able to monitor the students progress giving timely feedback as well as reporting the same to the parents. Teachers have the ability to grade asignments on the platform, set events, classes as well as upload extra content for the learners.

3. Parents
    # Being a major stakeholder at the institution, parents also have a dedicated dashboard to viewing their child's progress, the ccourse's content uploaded and its materials as well and engaging with the teacher on any issue that may arise.

## Access to Goldworth Services
## Goldworth in its entirety can only be access and its full value weighed and experienced by any of the enrolled users of the platform. All you have to do to earn a place at this experience is enroll a child, be a student or express interest as a faithfull and willing member of staff to the institution. Once accepted by the institution, you get your own login details as your personal keys to the greatness that awaits.

## Goldworth has done its due diligence in employing a myriad of technologies to ensure that education is offered at the highest standard possible while not forgetting the user experience along their journey. A beautifully crafted website gives you a feel of the following:

# A python Backend
# React Frontend
# Worldclass libraries to bring the best possible experience

## Setup
## The setup is quite simple for developers

1. Getting Started with Goldworth as a User.
    # After the School accepts your request to be a part of the community you are given access details which you will use to access further parts of the application. The access details include a verified Email address and login password. Keep the details safe at all times and at all cost to prevent breach of data privacy.
    # Navigate to the homepage which has access to the Log In menu.
    # Access the LogIn button for a panel to input your user details.
        ~ The user details are given upon acceptance as part of Goldwort Community. For more detils on how to get the log in details refer to the top of the page on : Access to Goldworth Services.
    # Log in to the application where you'll be directed to your respective dashboard where you'll get to explore the application in full depth.

2. Getting Started with Goldworth as an Admin.
    # Full access to Goldworth application is at the hands of the admin who has access to the teacher/student/parents sides respectively. The admin has the ability to register any user as a fellow adim member or user of the application with limited priviledges.
    # Access to the said right is via a signle entry point using the api endpoint with '/admin' as the slug to the CRUD functionality of the application.
    # The Admin has the ability to add a User, Course, Course-content, Event as well as Content. In addition, the admin can update any of the mentioned details as well as delete anything from the application database.


2. Getting started with Goldworth LMS for Local Development
    ## Setting up the Server
    # Cd into your directory holding the LMS files, preferably starting with the Server side.
    # Create a virtual environnment so as to have a dedicated environment for implementing the server and being able to run it efficiently.
    # Activate your environment and begin setting up the remainder of the project.
    # Run `pip install -r requirements.txt` to install the required libraries to your environment.
    # If there is no active database; the following instructions should get you an active one.
        1. Initialise the database using `Flask db init`
        2. Migrate the models with `flask db migrate -m <commit-message>` (use quotation marks in place of <>)
        3. Update the created database with 'Flask db upgrade'
        
#  Please not this is owned by Goldworth.