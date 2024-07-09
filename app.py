import os
from flask import request, make_response, session, send_from_directory, render_template
from models import Teacher, Student, Parent, Course, Content, User, Report_Card, Assignment, Event, Saved_Content, Comment, Submitted_Assignment
from flask_restful import Resource
from datetime import datetime
from config import mash, db, api, app, admin
from flask_admin.contrib.sqla import ModelView
from werkzeug.exceptions import NotFound, MethodNotAllowed, ServiceUnavailable, BadRequest, InternalServerError
from werkzeug.utils import secure_filename


@app.errorhandler(NotFound)
def resource_missing(e):
    return "Sorry the requested resource does not exist!"


@app.errorhandler(MethodNotAllowed)
def wrong_method(e):
    return "The request made is not allowed!"


@app.errorhandler(BadRequest)
def bad_request(e):
    return "You have made an invalid request, try again with the correct details."


@app.errorhandler(ServiceUnavailable)
def service_error(e):
    return "Sorry for the inconvenience, the service is not available at the moment! Please try again later. Thankyou for your patience!"


@app.errorhandler(InternalServerError)
def server_error(e):
    return "Sorry for the inconvenience, we are looking into the problem. Thankyou for your patience!"


class Index(Resource):
    def get(self):
        message = "Hello, World"
        return render_template('index.html',  
                           message=message)

api.add_resource(Index, '/')


def User_details(user):
    if 'lecturer' in user.email:
        return make_response(
            {
                "teacher_id": user.teacher_id,
                "name": f'{user.teacher.firstname} {user.teacher.lastname}',
                "email": user.email,
                "image_url": user.teacher.image_url,
                "expertise": user.teacher.expertise,
                "department": user.teacher.department,
                "docs": contents_schema.dump(user.teacher.docs),
                "courses": courses_schema.dump(user.teacher.courses),
            }, 200
        )
    elif 'student' in user.email:
        return make_response(
            {
                "student_id": user.student_id,
                "name": f'{user.student.firstname} {user.student.lastname}',
                "email": user.email,
                "image_url": user.student.image_url,
                "report_card": report_cards_schema.dump(user.student.report_card),
                "assignments": submitted_assignments_schema.dump(user.student.assignments),
                "docs": contents_schema.dump(user.student.docs),
                "courses": courses_schema.dump(user.student.courses),
                "event": events_schema.dump(user.student.event)
            }, 200
        )
    return make_response(
        {
            "parent_id": user.parent_id,
            "name": f'{user.parent.firstname} {user.parent.lastname}',
            "email": user.email,
            "child": students_schema.dump(user.parent.child),
            "image_url": user.parent.image_url,
        }, 200
    )


class Login(Resource):
    def post(self):
        user_logins = request.get_json()
        password = user_logins['password']
        user = User.query.filter_by(email=user_logins['email']).first()

        if user:
            if user.authenticate(password):
                session['user'] = user.email
                return User_details(user)

            return "Invalid email or password", 400
        return "User does not exist", 404


api.add_resource(Login, '/login')


class CheckSession(Resource):
    def get(self):
        user = session.get('user')
        user_data = User.query.filter_by(email=user).first()

        if user:
            return User_details(user_data)

        return "Please login to continue", 401


api.add_resource(CheckSession, '/checksession')


class Logout(Resource):
    def delete(self):
        user = session.get('user')

        if user:
            session['user'] = None

            return "You have been logged out successfully", 200
        return make_response("You are not allowed to access this method", 401)


api.add_resource(Logout, '/logout')

class FetchFile(Resource):
    def get(self,id):
        assignment = Assignment.query.filter_by(id=id).first()

        assignment_file = send_from_directory(app.config['FILE_UPLOAD_PATH'] , assignment.assignment_file , as_attachment=True)
        return assignment_file

api.add_resource(FetchFile, '/assignment-file/<int:id>')

class FetchImage(Resource):
    def get(self):
        session_details = session.get('user')

        user = User.query.filter_by(email=session_details).first()

        if 'lecturer' in user.email:
            photo = send_from_directory(app.config['IMAGE_UPLOAD_PATH'] , user.teacher.image_url)
            return photo
        elif 'student' in user.email:
            photo = send_from_directory(app.config['IMAGE_UPLOAD_PATH'] , user.student.image_url)
            return photo
        return send_from_directory(app.config['IMAGE_UPLOAD_PATH'] , user.parent.image_url)

api.add_resource(FetchImage, '/profile_image')


#Marshmallow API Endpoints

class UserSchema(mash.SQLAlchemySchema):

    class Meta:
        model = User

    email = mash.auto_field()
    student_id = mash.auto_field()
    teacher_id = mash.auto_field()
    parent_id = mash.auto_field()

    student_url = mash.Hyperlinks(
        {
            "student": mash.URLFor(
                "studentbyid",
                values=dict(id="<student_id>")),
            "students_list": mash.URLFor("students")

        }
    )
    parent_url = mash.Hyperlinks(
        {
            "parent": mash.URLFor(
                "parentbyid",
                values=dict(id="<parent_id>")),
            "parents_list": mash.URLFor("parents")

        }
    )
    teacher_url = mash.Hyperlinks(
        {
            "teacher": mash.URLFor(
                "teacherbyid",
                values=dict(id="<teacher_id>")),
            "teachers_list": mash.URLFor("teachers")

        }
    )

class ContentSchema(mash.SQLAlchemySchema):

    class Meta:
        model = Content
    
    id = mash.auto_field()
    content_name = mash.auto_field()
    content_type = mash.auto_field()
    description = mash.auto_field()

class CourseSchema(mash.SQLAlchemySchema):

    class Meta:
        model = Course
    
    id = mash.auto_field()
    course_name = mash.auto_field()
    description = mash.auto_field()
    teachers = mash.List(mash.Nested(lambda: TeacherSchema( only=('firstname','lastname','expertise'))))
    content = mash.List(mash.Nested(ContentSchema))


class TeacherSchema(mash.SQLAlchemySchema):

    class Meta:
        model = Teacher
    
    id = mash.auto_field()
    firstname = mash.auto_field()
    lastname = mash.auto_field()
    email = mash.auto_field()
    expertise = mash.auto_field()
    department = mash.auto_field()
    courses= mash.List(mash.Nested(CourseSchema))
    docs = mash.List(mash.Nested(ContentSchema))


class ParentSchema(mash.SQLAlchemySchema):

    class Meta:
        model = Parent
    
    load_instance = True
    
    id = mash.auto_field()
    firstname = mash.auto_field()
    lastname = mash.auto_field()
    email = mash.auto_field()
    child = mash.List(mash.Nested(lambda: StudentSchema(only=('id','firstname','lastname'))))



class StudentSchema(mash.SQLAlchemySchema):

    class Meta:
        model = Student

    id = mash.auto_field()
    firstname = mash.auto_field()
    lastname = mash.auto_field()
    email = mash.auto_field()
    created_at = mash.auto_field()
    courses = mash.List(mash.Nested(CourseSchema))
    parent = mash.Nested(ParentSchema)
    docs = mash.List(mash.Nested(ContentSchema))
    event = mash.auto_field()
    report_card = mash.List(mash.Nested(lambda: ReportCardSchema(only=('id','topic','grade', 'teacher_remarks', 'course_id'))))
    assignments = mash.List(mash.Nested(lambda: Submitted_AssignmentSchema(only=('id','assignment_name','content', 'remarks', 'grade', 'course_id'))))


    url = mash.Hyperlinks(
        {
            "self": mash.URLFor(
                "studentbyid",
                values=dict(id="<id>")),
            "collection": mash.URLFor("students")

        }
    )


class ReportCardSchema(mash.SQLAlchemySchema):

    class Meta:
        model = Report_Card
    
    id = mash.auto_field()
    topic = mash.auto_field()
    teacher_remarks = mash.auto_field()
    grade = mash.auto_field()
    
    course_id = mash.auto_field()

class AssignmentSchema(mash.SQLAlchemySchema):

    class Meta:
        model = Assignment
    
    id = mash.auto_field()
    assignment_name = mash.auto_field()
    topic = mash.auto_field()
    content = mash.auto_field()
    assignment_file = mash.auto_field()
    due_date = mash.auto_field()
    course_id = mash.auto_field()


    url = mash.Hyperlinks(
        {
            "self":mash.URLFor(
                "assignmentbyid",
                values=dict(id="<id>")),
            "collection":mash.URLFor("assignments")

        }
    )

class Submitted_AssignmentSchema(mash.SQLAlchemySchema):

    class Meta:
        model = Submitted_Assignment
    
    id = mash.auto_field()
    assignment_name = mash.auto_field()
    grade = mash.auto_field()
    content = mash.auto_field()
    assignment_file = mash.auto_field()
    remarks = mash.auto_field()
    course_id = mash.auto_field()
    student_id = mash.auto_field()
    is_graded = mash.auto_field()

class EventSchema(mash.SQLAlchemySchema):

    class Meta:
        model = Event
    
    id = mash.auto_field()
    groupId = mash.auto_field()
    allDay = mash.auto_field()
    start = mash.auto_field()
    end = mash.auto_field()
    daysOfWeek = mash.auto_field()
    startTime = mash.auto_field()
    endTime = mash.auto_field()
    startRecur = mash.auto_field()
    endRecur = mash.auto_field()
    title = mash.auto_field()
    student_id = mash.auto_field()
    course_id = mash.auto_field()
    teacher_id = mash.auto_field()

class SavedContentSchema(mash.SQLAlchemySchema):

    class Meta:
        model = Saved_Content
    
    id = mash.auto_field()
    content_name = mash.auto_field()
    content_type = mash.auto_field()

class CommentsSchema(mash.SQLAlchemySchema):
    class Meta:
        model = Comment

    id = mash.auto_field()
    title = mash.auto_field()
    subject = mash.auto_field()
    content = mash.auto_field()
    parent_id = mash.auto_field()
    student_id = mash.auto_field()
    teacher_id = mash.auto_field()

comment_schema = CommentsSchema()
comments_schema = CommentsSchema(many=True)
saved_content_schema = SavedContentSchema()
saved_contents_schema = SavedContentSchema(many=True)   
event_schema = EventSchema()
events_schema = EventSchema(many=True)
submitted_assignment_schema = Submitted_AssignmentSchema()
submitted_assignments_schema = Submitted_AssignmentSchema(many=True)
assignment_schema = AssignmentSchema()
assignments_schema = AssignmentSchema(many=True)
report_card_schema = ReportCardSchema()
report_cards_schema = ReportCardSchema(many=True)
course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)
content_schema = ContentSchema()
contents_schema = ContentSchema(many=True)
parent_schema = ParentSchema()
parents_schema = ParentSchema(many=True)
teacher_schema = TeacherSchema()
teachers_schema = TeacherSchema(many=True)
user_schema = UserSchema()
users_schema = UserSchema(many=True)
student_schema = StudentSchema()
students_schema = StudentSchema(many=True)

#Flask-Admin Views

class UserView(ModelView):
    form_columns = ['email', 'password', 'student', 'teacher', 'parent']

class StudentView(ModelView):
    form_columns = ['firstname', 'lastname', 'password', 'email', 'personal_email', 'parent', 'image_url']

class TeacherView(ModelView):
    form_columns = ['firstname', 'lastname', 'password', 'email', 'personal_email', 'expertise', 'image_url', 'department']

class ParentView(ModelView):
    form_columns = ['firstname', 'lastname', 'password', 'email', 'child', 'image_url']

admin.add_views(UserView(User, db.session))
admin.add_views(StudentView(Student, db.session))
admin.add_views(TeacherView(Teacher, db.session))
admin.add_views(ParentView(Parent, db.session))
admin.add_views(ModelView(Content, db.session))
admin.add_views(ModelView(Course, db.session))
admin.add_views(ModelView(Event, db.session))


#API Views

class Users(Resource):
    def get(self):
        users = User.query.all()
        
        return make_response(
            users_schema.dump(users), 200
        )

class Students(Resource):
    def get(self):
        students = Student.query.all()

        return make_response(
            students_schema.dump(students), 200
        )

    def post(self):
        student_image = request.files['image_url']
        student_img = secure_filename(student_image.filename)
        student_image.save(os.path.join(
            app.config["IMAGE_UPLOAD_PATH"], student_img))

        # print(type(student_img))
        new_student = Student(
            firstname=request.form.get('firstname'),
            lastname=request.form.get('lastname'),
            image_url=student_img,
            personal_email=request.form.get('personal_email'),
            password=request.form.get('password'),
            email=request.form.get('email'),
            parent_id=request.form.get('parent_id')
        )
        db.session.add(new_student)
        db.session.commit()

        new_student.add_user()

        return make_response(
            student_schema.dump(new_student), 201
        )
    
class StudentbyId(Resource):
    def get(self, id):
        student = Student.query.filter_by(id=id).first()

        return make_response(
            student_schema.dump(student), 200
        )

    def patch(self, id):
        student_data = request.get_json()
        student = Student.query.filter_by(id=id).first()

        for attr in student_data:
            setattr(student, attr, student_data[attr])

        db.session.add(student)
        db.session.commit()

        return make_response(
            student_schema.dump(student), 202
        )

    def delete(self, id):
        student = Student.query.filter_by(id=id).first()

        db.session.delete(student)
        db.session.commit()

        return "Record successfully deleted", 202


class Assignments(Resource):
    def get(self):
        assignments = Assignment.query.all()

        return make_response(
            assignments_schema.dump(assignments), 200
        )
    
    def post(self):
        assignment_file = request.files['assignment_file']
        assignment = secure_filename(assignment_file.filename)
        assignment_file.save(os.path.join(app.config["FILE_UPLOAD_PATH"],assignment))
    
        assignment_data = request.form
        # print(assignment_data['assignment_file'])
        new_assignment = Assignment(
            assignment_name = assignment_data.get('assignment_name'),
            topic = assignment_data.get('topic'),
            content = assignment_data.get('content'),
            assignment_file = assignment_data.get('assignment_file'),
            due_date = datetime.strptime(assignment_data.get('due_date'), "%Y-%m-%d").date(),
            course_id = assignment_data.get('course_id'),
            teacher_id = assignment_data.get('teacher_id'),
        )
        db.session.add(new_assignment)
        db.session.commit()

        return make_response(
            assignment_schema.dump(new_assignment), 201
        )
    
class AssignmentbyId(Resource):
    def get(self,id):
        assignment = Assignment.query.filter_by(id=id).first()

        return make_response(
            assignment_schema.dump(assignment), 200
        )
        
    def patch(self,id):
        assignment_data = request.get_json()
        assignment = Assignment.query.filter_by(id=id).first()

        for attr in assignment_data:
            setattr(assignment, attr, assignment_data[attr])
        
        db.session.add(assignment)
        db.session.commit()

        return make_response(
            assignment_schema.dump(assignment), 202
        )

    def delete(self,id):
        assignment = Assignment.query.filter_by(id=id).first()

        db.session.delete(assignment)
        db.session.commit()

        return "record successfully deleted" , 202
    
    
class Teachers(Resource):

    column_searchable_list = ('firstname', 'lastname', 'email')

    def get(self):
        teachers = Teacher.query.all()

        return make_response(
            teachers_schema.dump(teachers), 200
        )

    def post(self):
        teacher_data = request.get_json()
        new_teacher = Teacher(
            firstname=teacher_data['firstname'],
            lastname=teacher_data['lastname'],
            image_url=teacher_data['image_url'],
            personal_email=teacher_data['personal_email'],
            password=teacher_data['password'],
            email=teacher_data['email'],
            expertise=teacher_data['expertise'],
            department=teacher_data['department']
        )
        db.session.add(new_teacher)
        db.session.commit()

        new_teacher.add_user()

        return make_response(
            teacher_schema.dump(new_teacher), 201
        )
   
class TeacherbyId(Resource):
    def get(self, id):
        teacher = Teacher.query.filter_by(id=id).first()

        return make_response(
            teacher_schema.dump(teacher), 200
        )

    def patch(self, id):
        teacher_data = request.get_json()
        teacher = Teacher.query.filter_by(id=id).first()

        for attr in teacher_data:
            setattr(teacher, attr, teacher_data[attr])

        db.session.add(teacher)
        db.session.commit()

        return make_response(
            teacher_schema.dump(teacher), 202
        )

    def delete(self, id):
        teacher = Teacher.query.filter_by(id=id).first()

        db.session.delete(teacher)
        db.session.commit()

        return "record successfully deleted", 202


class Parents(Resource):
    def get(self):
        parents = Parent.query.all()

        return make_response(
            parents_schema.dump(parents), 200
        )

    def post(self):
        parent_data = request.get_json()
        new_parent = Parent(
            firstname=parent_data['firstname'],
            lastname=parent_data['lastname'],
            email=parent_data['email'],
            password=parent_data['password'],
            # image_url = parent_data['Image_url']
        )
        db.session.add(new_parent)
        db.session.commit()

        new_parent.add_user()

        return make_response(
            parent_schema.dump(new_parent), 201
        )
    
class ParentbyId(Resource):
    def get(self, id):
        parent = Parent.query.filter_by(id=id).first()

        return make_response(
            parent_schema.dump(parent), 200
        )

    def patch(self, id):
        parent_data = request.get_json()
        parent = Parent.query.filter_by(id=id).first()

        for attr in parent_data:
            setattr(parent, attr, parent_data[attr])

        db.session.add(parent)
        db.session.commit()

        return make_response(
            parent_schema.dump(parent), 202
        )

    def delete(self, id):
        parent = Parent.query.filter_by(id=id).first()

        db.session.delete(parent)
        db.session.commit()

        return "record successfully deleted", 202


class Contents(Resource):
    def get(self):
        contents = Content.query.all()

        return make_response(
            contents_schema.dump(contents), 200
        )

    def post(self):
        content_data = request.get_json()
        new_content = Content(
            content_name=content_data['content_name'],
            description=content_data['description'],
            content_type=content_data['content_type'],
        )
        db.session.add(new_content)
        db.session.commit()

        return make_response(
            content_schema.dump(new_content), 201
        )


class ContentbyId(Resource):
    def get(self, id):
        content = Content.query.filter_by(id=id).first()

        return make_response(
            content_schema.dump(content), 200
        )

    def patch(self, id):
        content_data = request.get_json()
        content = Content.query.filter_by(id=id).first()

        for attr in content_data:
            setattr(content, attr, content_data[attr])

        db.session.add(content)
        db.session.commit()

        return make_response(
            content_schema.dump(content), 202
        )

    def delete(self, id):
        content = Content.query.filter_by(id=id).first()

        db.session.delete(content)
        db.session.commit()

        return "record successfully deleted", 202


class Courses(Resource):
    def get(self):
        course = Course.query.all()

        return make_response(
            courses_schema.dump(course), 200
        )

    def post(self):
        course_data = request.get_json()
        new_course = Course(
            course_name=course_data['course_name'],
            description=course_data['description'],
            # student_id = course_data['student_id'],
            # teacher_id = course_data['teacher_id'],
            daysOfWeek=course_data['daysOfWeek'],
            startTime=datetime.strptime(
                course_data['startTime'], "%H:%M").time(),
            endTime=datetime.strptime(course_data['endTime'], "%H:%M").time(),
            startRecur=datetime.strptime(
                course_data['startRecur'], "%Y-%m-%d").date(),
            endRecur=datetime.strptime(
                course_data['endRecur'], "%Y-%m-%d").date(),
        )
        db.session.add(new_course)
        db.session.commit()

        return make_response(
            course_schema.dump(new_course), 201
        )

class CoursebyId(Resource):
    def get(self, id):
        course = Course.query.filter_by(id=id).first()

        return make_response(
            course_schema.dump(course), 200
        )

    def patch(self, id):
        course_data = request.get_json()
        course = Course.query.filter_by(id=id).first()

        if not course:
            return make_response({"message": "Course not found"}, 404)

        for attr in course_data:
            if attr in ['startTime', 'endTime']:
                setattr(course, attr, datetime.strptime(
                    course_data[attr], "%H:%M").time())
            elif attr in ['startRecur', 'endRecur']:
                setattr(course, attr, datetime.strptime(
                    course_data[attr], "%Y-%m-%d").date())
            else:
                setattr(course, attr, course_data[attr])

        db.session.add(course)
        db.session.commit()

        return make_response(
            course_schema.dump(course), 202
        )


    def delete(self, id):
        course = Course.query.filter_by(id=id).first()

        db.session.delete(course)
        db.session.commit()

        return "record successfully deleted", 202


class Report_Cards(Resource):
    def get(self):
        report_card = Report_Card.query.all()

        return make_response(
            report_cards_schema.dump(report_card), 200
        )

    def post(self):
        reportcard_data = request.get_json()
        new_report = Report_Card(
            topic=reportcard_data['topic'],
            grade=reportcard_data['grade'],
            teacher_remarks=reportcard_data['teacher_remarks'],
            student_id=reportcard_data['student_id'],
            course_id=reportcard_data['course_id'],
        )
        db.session.add(new_report)
        db.session.commit()

        return make_response(
            report_card_schema.dump(new_report), 201
        )
    
class Report_CardbyId(Resource):
    def get(self, id):
        report_card = Report_Card.query.filter_by(id=id).first()

        return make_response(
            report_card_schema.dump(report_card), 200
        )

    def patch(self, id):
        report_card_data = request.get_json()
        report_card = Report_Card.query.filter_by(id=id).first()

        for attr in report_card_data:
            setattr(report_card, attr, report_card_data[attr])

        db.session.add(report_card)
        db.session.commit()

        return make_response(
            report_card_schema.dump(report_card), 202
        )

    def delete(self, id):
        report_card = Report_Card.query.filter_by(id=id).first()

        db.session.delete(report_card)
        db.session.commit()

        return "record successfully deleted", 202


class Submitted_Assignments(Resource):
    def get(self):
        assignments = Submitted_Assignment.query.all()

        return make_response(
            submitted_assignments_schema.dump(assignments), 200
        )

    def post(self):
        assignment_data = request.get_json()
        new_assignment = Content(
            assignment_name=assignment_data['assignment_name'],
            grade=assignment_data['grade'],
            content=assignment_data['content'],
            assignment_file=assignment_data['assignment_file'],
            remarks=assignment_data['remarks'],
            course_id=assignment_data['course_id'],
            student_id=assignment_data['student_id'],
        )
        db.session.add(new_assignment)
        db.session.commit()

        return make_response(
            submitted_assignment_schema.dump(new_assignment), 201
        )
   
class Submitted_AssignmentbyId(Resource):
    def get(self, id):
        assignment = Submitted_Assignment.query.filter_by(id=id).first()

        return make_response(
            submitted_assignment_schema.dump(assignment), 200
        )

    def patch(self, id):
        assignment_data = request.get_json()
        assignment = Submitted_Assignment.query.filter_by(id=id).first()

        for attr in assignment_data:
            setattr(assignment, attr, assignment_data[attr])

        db.session.add(assignment)
        db.session.commit()

        return make_response(
            submitted_assignment_schema.dump(assignment), 202
        )

    def delete(self, id):
        assignment = Submitted_Assignment.query.filter_by(id=id).first()

        db.session.delete(assignment)
        db.session.commit()

        return "record successfully deleted", 202


class Events(Resource):
    def get(self):
        events = Event.query.all()
        return make_response(events_schema.dump(events), 200)

    def post(self):
        data = request.get_json()

        course = Course.query.get(data['course_id'])
        title = ''

        if course:
            title = f"{course.course_name} "
        else:
            title = "Unknown Course"

        custom_title = data.get('title')
        event_title = custom_title if custom_title else title

        new_event = Event(
            groupId=data['groupId'],
            allDay=data['allDay'],
            start=datetime.strptime(data['start'], "%Y-%m-%d").date(),
            end=datetime.strptime(data['end'], "%Y-%m-%d").date(),
            daysOfWeek=data['daysOfWeek'],
            startTime=datetime.strptime(data['startTime'], "%H:%M").time(),
            endTime=datetime.strptime(data['endTime'], "%H:%M").time(),
            startRecur=datetime.strptime(
                data['startRecur'], "%Y-%m-%d").date(),
            endRecur=datetime.strptime(data['endRecur'], "%Y-%m-%d").date(),
            title=event_title,
            course_id=data['course_id'],
            student_id=data['student_id'],
            teacher_id=data['teacher_id'],
        )
        db.session.add(new_event)
        db.session.commit()

        events = Event.query.all()

        return make_response(event_schema.dump(new_event), 200)


class EventbyId(Resource):
    def get(self, id):
        event = Event.query.filter_by(id=id).first()
        return make_response(event_schema.dump(event), 200)

    def patch(self, id):
        data = request.get_json()
        event = Event.query.filter_by(id=id).first()

        if not event:
            return make_response({"message": "Event not found"}, 404)

        for attr in data:
            if attr in ['startTime', 'endTime']:
                setattr(event, attr, datetime.strptime(
                    data[attr], "%H:%M").time())
                
            elif attr in ['startRecur','endRecur','end','start']:
                setattr(event, attr, datetime.strptime(
                    data[attr], "%Y-%m-%d").date())
            else:
                setattr(event, attr, data[attr])

        # Update the title based on the course_id
        if 'course_id' in data:
            course = Course.query.get(data['course_id'])
            if course:
                event.title = f"{course.course_name}"
            else:
                event.title = "Unknown Course"

        db.session.add(event)
        db.session.commit()

        return make_response(event_schema.dump(event), 200)

    def delete(self, id):
        event = Event.query.filter_by(id=id).first()

        db.session.delete(event)
        db.session.commit()

        return make_response({"message": "Record successfully deleted"}, 200)

class Saved_Contents(Resource):
    def get(self):
        saved_Contents = Saved_Content.query.all()

        return make_response(
            saved_contents_schema.dump(saved_Contents), 200
        )

    def post(self):
        saved_Content = request.get_json()
        new_content = Saved_Content(
            content_name=saved_Content['content_name'],
            content_type=saved_Content['content_type'],
            course_id=saved_Content['course_id'],
            student_id=saved_Content['student_id'],
            teacher_id=saved_Content['teacher_id'],
        )
        db.session.add(new_content)
        db.session.commit()

        return make_response(
            saved_content_schema.dump(new_content), 201
        )
    
class SavedContentById(Resource):
    def delete(self, id):
        saved_content = Saved_Content.query.filter_by(id=id).first()

        db.session.delete(saved_content)
        db.session.commit()

        return "record successfully deleted", 202


class Comments(Resource):
    def get(self):
        comments = Comment.query.all()

        return make_response(
            comments_schema.dump(comments), 200
        )

    def post(self):
        comment_data = request.get_json()
        new_comment = Comment(
            title=comment_data['title'],
            subject=comment_data['subject'],
            content=comment_data['content'],
            parent_id=comment_data['parent_id'],
            student_id=comment_data['student_id'],
            teacher_id=comment_data['teacher_id'],
        )
        db.session.add(new_comment)
        db.session.commit()

        return make_response(
            comment_schema.dump(new_comment), 201
        )


class CommentById(Resource):
    def get(self, id):
        comment = Comment.query.filter_by(id=id).first()

        return make_response(
            comment.dump(comment), 200
        )

    def patch(self, id):
        comment_data = request.get_json()
        comment = Comment.query.filter_by(id=id).first()

        for attr in comment_data:
            setattr(comment, attr, comment_data[attr])

        db.session.add(comment)
        db.session.commit()

        return make_response(
            comment_schema.dump(comment), 202
        )

    def delete(self, id):
        comment = Comment.query.filter_by(id=id).first()

        db.session.delete(comment)
        db.session.commit()

        return "record successfully deleted", 202


api.add_resource(Users, '/users')
api.add_resource(StudentbyId, '/students/<int:id>')
api.add_resource(Students, '/students')
api.add_resource(TeacherbyId, '/teachers/<int:id>')
api.add_resource(Teachers, '/teachers')
api.add_resource(ParentbyId, '/parents/<int:id>')
api.add_resource(Parents, '/parents')
api.add_resource(ContentbyId, '/contents/<int:id>')
api.add_resource(Contents, '/contents')
api.add_resource(CoursebyId, '/courses/<int:id>')
api.add_resource(Courses, '/courses')
api.add_resource(Report_CardbyId, '/report-cards/<int:id>')
api.add_resource(Report_Cards, '/report-cards')
api.add_resource(AssignmentbyId, '/assignments/<int:id>')
api.add_resource(Assignments, '/assignments')
api.add_resource(Submitted_AssignmentbyId, '/submitted-assignments/<int:id>')
api.add_resource(Submitted_Assignments, '/submitted-assignments')
api.add_resource(EventbyId, '/events/<int:id>')
api.add_resource(Events, '/events')
api.add_resource(SavedContentById, '/saved_contents/<int:id>')
api.add_resource(Saved_Contents, '/saved_contents')
api.add_resource(CommentById, '/comments/<int:id>')
api.add_resource(Comments, '/comments')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
