from config import db, bcrypt
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
import re

course_teacher = db.Table(
    'course_teacher',
    db.metadata,
    db.Column('teacher_id', db.ForeignKey('teachers.id'), primary_key=True),
    db.Column('course_id', db.ForeignKey('courses.id'), primary_key=True),
    extend_existing =True
)

course_student = db.Table(
    'course_student',
    db.metadata,
    db.Column('student_id', db.ForeignKey('students.id'), primary_key=True),
    db.Column('course_id', db.ForeignKey('courses.id'), primary_key=True),
    extend_existing =True
)

class User(db.Model):
    __tablename__ = 'users'

    email = db.Column(db.String, nullable = False , unique = True, primary_key = True)
    _password = db.Column(db.String, nullable = False , unique = True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    
    
    @hybrid_property
    def password(self):
        return self._password
    
    @password.setter
    def password(self,pwd):
        password_hash = bcrypt.generate_password_hash(pwd.encode('utf-8'))
        self._password = password_hash.decode('utf-8')
    
    def authenticate(self,pwd):
        pwd_check = bcrypt.check_password_hash(self._password, pwd.encode('utf-8'))
        return pwd_check

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer , primary_key = True)
    firstname = db.Column(db.String, nullable = False)
    lastname = db.Column(db.String, nullable = False)
    personal_email = db.Column(db.String, nullable = False , unique = True)
    email = db.Column(db.String, nullable = False , unique = True)
    _password = db.Column(db.String, nullable = False , unique = True)
    image_url= db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate = db.func.now())

    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'))

    user = db.relationship('User', backref='student', cascade="save-update , merge, delete, delete-orphan")
    event = db.relationship('Event', back_populates='student', cascade="save-update , merge, delete, delete-orphan")
    parent = db.relationship('Parent', back_populates='child', cascade="save-update , merge, delete")
    assignments = db.relationship('Submitted_Assignment', backref='student', cascade="save-update , merge, delete, delete-orphan")
    report_card = db.relationship('Report_Card', back_populates='student', cascade="save-update , merge, delete, delete-orphan")
    courses = db.relationship('Course', secondary=course_student, back_populates='students', cascade="save-update , merge, delete")
    docs = db.relationship('Content', cascade="save-update , merge, delete, delete-orphan")
    saved_items = db.relationship('Saved_Content', cascade="save-update , merge, delete, delete-orphan")

    def __repr__(self):
        return '<Student %r >' % (f'{self.firstname} {self.lastname}')
    
    @hybrid_property
    def password(self):
        return self._password
    
    @password.setter
    def password(self,pwd):
        password_hash = bcrypt.generate_password_hash(pwd.encode('utf-8'))
        self._password = password_hash.decode('utf-8')
    
    @validates("firstname","lastname")
    def validates_name(self,key,name):
        if not name:
            raise ValueError("Value is required !")
        return name
    
    @validates("email")
    def validates_email(self,key,value):
        email_regex = re.compile(r'[a-zA-Z-_\.0-9]+@[a-zA-Z-_]+\.[a-zA-Z]+[a-zA-Z]?')
        if not value:
            raise ValueError("Email Address is a required field!")
        elif not email_regex.match(value):
            raise ValueError("Please provide a valid email address!")
        return value

    def add_user(self):
        user = User(
            email = self.email,
            _password = self._password,
            student_id = self.id
        )
        db.session.add(user)
        db.session.commit()
        return user
    
class Teacher(db.Model):
    __tablename__ = 'teachers'

    id = db.Column(db.Integer , primary_key = True)
    firstname = db.Column(db.String, nullable = False)
    lastname = db.Column(db.String, nullable = False)
    personal_email = db.Column(db.String, nullable = False , unique = True)
    email = db.Column(db.String, nullable = False , unique = True)
    _password = db.Column(db.String, nullable = False , unique = True)
    image_url= db.Column(db.String)
    expertise = db.Column(db.String)
    department = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate = db.func.now())

    docs = db.relationship('Content', cascade="save-update , merge, delete, delete-orphan")
    user = db.relationship('User', backref='teacher', cascade="save-update , merge, delete, delete-orphan")
    event = db.relationship('Event', back_populates='teacher', cascade="save-update , merge, delete, delete-orphan")
    courses = db.relationship('Course', secondary=course_teacher, back_populates='teachers', cascade="save-update , merge, delete")
    saved_items = db.relationship('Saved_Content', cascade="save-update , merge, delete, delete-orphan")

    def __repr__(self):
        return '<Teacher %r >' % (f'{self.firstname} {self.lastname}')
    
    @hybrid_property
    def password(self):
        return self._password
    
    @password.setter
    def password(self,pwd):
        password_hash = bcrypt.generate_password_hash(pwd.encode('utf-8'))
        self._password = password_hash.decode('utf-8')
    
    @validates("firstname","lastname")
    def validates_name(self,key,name):
        if not name:
            raise ValueError("Value is required !")
        return name
    
    @validates("email")
    def validates_email(self,key,value):
        email_regex = re.compile(r'[a-zA-Z-_\.0-9]+@[a-zA-Z-_]+\.[a-zA-Z]+[a-zA-Z]?')
        if not value:
            raise ValueError("Email Address is a required field!")
        elif not email_regex.match(value):
            raise ValueError("Please provide a valid email address!")
        return value
    
    def add_user(self):
        user = User(
            email = self.email,
            _password = self._password,
            teacher_id = self.id
        )
        db.session.add(user)
        db.session.commit()
        return user

class Parent(db.Model):
    __tablename__ = 'parents'

    id = db.Column(db.Integer , primary_key = True)
    firstname = db.Column(db.String, nullable = False)
    lastname = db.Column(db.String, nullable = False)
    email = db.Column(db.String, nullable = False , unique = True)
    _password = db.Column(db.String, nullable = False , unique = True)
    image_url= db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate = db.func.now())

    child = db.relationship('Student', back_populates='parent', cascade="save-update , merge, delete, delete-orphan")
    user = db.relationship('User', backref='parent', cascade="save-update , merge, delete, delete-orphan")

    def __repr__(self):
        return '<Parent %r >' % (f'{self.firstname} {self.lastname}')

    @hybrid_property
    def password(self):
        return self._password
    
    @password.setter
    def password(self,pwd):
        password_hash = bcrypt.generate_password_hash(pwd.encode('utf-8'))
        self._password = password_hash.decode('utf-8')
    
    @validates("firstname","lastname")
    def validates_name(self,key,name):
        if not name:
            raise ValueError("Value is required !")
        return name
    
    @validates("email")
    def validates_email(self,key,value):
        email_regex = re.compile(r'[a-zA-Z-_\.0-9]+@[a-zA-Z-_]+\.[a-zA-Z]+[a-zA-Z]?')
        if not value:
            raise ValueError("Email Address is a required field!")
        elif not email_regex.match(value):
            raise ValueError("Please provide a valid email address!")
        return value
    
    def add_user(self):
        user = User(
            email = self.email,
            _password = self._password,
            parent_id = self.id
        )
        db.session.add(user)
        db.session.commit()
        return user

    
class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer , primary_key = True)
    course_name = db.Column(db.String, nullable = False , unique = True)
    description = db.Column(db.String, nullable = False)
    image_url= db.Column(db.String)
    daysOfWeek = db.Column(db.String)  
    startRecur = db.Column(db.Date)
    endRecur = db.Column(db.Date)    
    startTime = db.Column(db.Time) 
    endTime = db.Column(db.Time)
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate = db.func.now())

    content = db.relationship('Content', back_populates='course', cascade="save-update , merge, delete, delete-orphan")
    students = db.relationship('Student', secondary=course_student, back_populates='courses', cascade="save-update , merge, delete")
    teachers = db.relationship('Teacher', secondary=course_teacher, back_populates='courses', cascade="save-update , merge, delete")

    def __repr__(self):
        return '<Course %r >' % (self.course_name)

class Content(db.Model):
    __tablename__ = 'contents'

    id = db.Column(db.Integer , primary_key = True)
    content_name = db.Column(db.String, nullable = False)
    description = db.Column(db.String, nullable = False)
    content_file = db.Column(db.String )
    content_type = db.Column(db.String, nullable = False)
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate = db.func.now())

    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))

    course = db.relationship('Course', back_populates='content', cascade="save-update , merge, delete")

    def __repr__(self):
        return '<Content %r >' % (self.content_name)

class Saved_Content(db.Model):
    __tablename__ = 'saved-contents'

    id = db.Column(db.Integer , primary_key = True)
    content_name = db.Column(db.String, nullable = False)
    content_type = db.Column(db.String, nullable = False)
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate = db.func.now())

    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))

    def __repr__(self):
        return '<Saved_Content %r >' % (self.content_name)

class Report_Card(db.Model):
    __tablename__ = 'report_cards'
    
    id = db.Column(db.Integer , primary_key = True)
    topic = db.Column(db.String, nullable = False)
    grade = db.Column(db.Integer, nullable = False)
    teacher_remarks = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate = db.func.now())

    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))

    student = db.relationship('Student', back_populates='report_card', cascade="save-update , merge, delete")



class Assignment(db.Model):
    __tablename__ = 'assignments'
    
    id = db.Column(db.Integer , primary_key = True)
    assignment_name = db.Column(db.String, nullable = False)
    topic = db.Column(db.String, nullable = False)
    content = db.Column(db.String, nullable = False)
    assignment_file = db.Column(db.String)
    due_date = db.Column(db.DateTime, server_default = db.func.now())
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate = db.func.now())

    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))

    def __repr__(self):
        return '<Assignment %r >' % (self.assignment_name)
    
class Submitted_Assignment(db.Model):
    __tablename__ = 'submitted_assignments'
    
    id = db.Column(db.Integer , primary_key = True)
    assignment_name = db.Column(db.String, nullable = False)
    content = db.Column(db.String)
    grade = db.Column(db.Integer)
    assignment_file = db.Column(db.String)
    remarks = db.Column(db.String)
    is_graded = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate = db.func.now())

    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    
    
class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    groupId = db.Column(db.Integer) 
    allDay = db.Column(db.Boolean, default=False)
    start = db.Column(db.Date, nullable=False)
    end = db.Column(db.Date)
    daysOfWeek = db.Column(db.String)  
    startTime = db.Column(db.Time) 
    endTime = db.Column(db.Time)  
    startRecur = db.Column(db.Date)
    endRecur = db.Column(db.Date)
    title = db.Column(db.String, nullable=False)
    
    def __repr__(self):
        return '<Event %r >' % (self.title)
    
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    
    student = db.relationship('Student', back_populates='event', cascade="save-update , merge, delete")
    teacher = db.relationship('Teacher', back_populates='event', cascade="save-update , merge, delete")
    course = db.relationship('Course')
    
class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer , primary_key = True)
    title = db.Column(db.String)
    subject = db.Column(db.String)
    content = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate = db.func.now())

    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'))

    def __repr__(self):
        return '<Comment %r >' % (self.subject)