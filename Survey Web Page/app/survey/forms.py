from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, RadioField
from wtforms.validators import DataRequired


class CreateSurveyForm(FlaskForm):
    survey_title = StringField("Survey Title", validators=[DataRequired()])
    survey_description = TextAreaField("Description", validators=[DataRequired()])


class CreateQuestionForm(FlaskForm):
    question_text = StringField('Question Text', validators=[DataRequired()])
    type = RadioField('Question Type',
                      choices=[('TEXT', 'Text'), ('NUMBER', 'Number'), ('SINGLE_CHOICE', 'Single Choice'),
                               ('MULTIPLE_CHOICE', 'Multiple Choice')], default='TEXT')



