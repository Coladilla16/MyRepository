import datetime
import enum

from app import db


class SurveyState(enum.Enum):
    NEW = "New"
    ONLINE = "Online"
    CLOSED = "Closed"


class QuestionType(enum.Enum):
    NUMBER = "Number"
    TEXT = "Text"
    SINGLE_CHOICE = "Single Choice"
    MULTIPLE_CHOICE = "Multiple Choice"


class Survey(db.Model):
    __tablename__ = 'surveys'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    state = db.Column(db.Enum(SurveyState), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    answers = db.relationship('SurveyAnswer', backref='survey', lazy=True, cascade="all, delete")
    questions = db.relationship('Question', backref='survey', lazy=True, cascade="all, delete",
                                order_by='Question.position')

    # helper method to get formatted date
    @property
    def fdate_created(self):
        return self.date_created.strftime("%b %d %Y at %I:%M %p")

    def __str__(self):
        return self.title

    def __repr__(self):
        return f"<Survey: {self.title}>"


class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    question_statement = db.Column(db.String(200), nullable=False)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Enum(QuestionType), nullable=False)
    answers = db.relationship('QuestionAnswer', backref='question', lazy=True, cascade="all, delete")
    options = db.relationship('QuestionOption', backref='question', lazy=False, cascade="all, delete",
                              order_by="QuestionOption.position")

    def __str__(self):
        return self.question_statement

    def __repr__(self):
        return f"<Question: {self.question_statement}>"


class QuestionOption(db.Model):
    __tablename__ = 'question_options'
    id = db.Column(db.Integer, primary_key=True)
    option_text = db.Column(db.String(200), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)

    def __str__(self):
        return self.option_text

    def __repr__(self):
        return f"<Option: {self.option_text}>"


class SurveyAnswer(db.Model):
    __tablename__ = 'survey_answers'
    id = db.Column(db.Integer, primary_key=True)
    date_submitted = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    answers = db.relationship('QuestionAnswer', backref='survey_answer', lazy=True, cascade='all, delete')


class QuestionAnswer(db.Model):
    __tablename__ = 'question_answers'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    survey_answer_id = db.Column(db.Integer, db.ForeignKey('survey_answers.id'), nullable=False)
    text_answer = db.Column(db.Text)
    integer_answer = db.Column(db.Integer)
    single_option_answer = db.Column(db.Integer, db.ForeignKey('question_options.id'))
    multiple_answers = db.relationship('MultipleAnswers', backref='question_answer', cascade='all, delete', lazy=False)

    @property
    def selected_option(self):
        return QuestionOption.query.get(self.single_option_answer)

    @property
    def selected_options(self):
        options = []
        for option in self.multiple_answers:
            options.append(QuestionOption.query.get(option.option_id))
        return options


class MultipleAnswers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answer_id = db.Column(db.Integer, db.ForeignKey('question_answers.id'), nullable=False)
    option_id = db.Column(db.Integer, db.ForeignKey('question_options.id'), nullable=False)



