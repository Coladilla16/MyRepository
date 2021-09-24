from flask import Blueprint

bp = Blueprint("survey", __name__, url_prefix="/survey", template_folder='templates')

from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from werkzeug.exceptions import Forbidden, NotFound

from app import db

from .forms import CreateSurveyForm, CreateQuestionForm
from .models import Survey, SurveyState, Question, QuestionType, QuestionOption, SurveyAnswer, QuestionAnswer, \
    MultipleAnswers


import pandas as pd
import pyodbc 

@bp.route('<int:survey_id>/download')
@login_required
def download_results(survey_id):
    survey = Survey.query.get(survey_id)
    sql_query = db.text("SELECT * FROM Survey.question_answers WHERE Survey.question_answers.survey_answer_id IN (SELECT Survey.survey_answers.id FROM Survey.survey_answers WHERE Survey.survey_answers.survey_id=%i);"%survey_id)
    connection = db.session.connection()
    result = connection.execute(sql_query)
    result = [item for item in result]
    sql_query = db.text("SELECT title FROM Survey.surveys WHERE id =%i;"%survey_id)
    connection = db.session.connection()
    title = connection.execute(sql_query)
    title = title.fetchall()
    title = [item[0] for item in title]
    results=[]
    if request.method == 'GET':
        for i in range(len(result)):
            temp=list(result[i])
            sql_query = db.text("SELECT question_statement FROM Survey.questions WHERE id=%i;"%temp[1])
            connection = db.session.connection()
            question = connection.execute(sql_query)
            question = question.fetchall()
            question = [item[0] for item in question]
            question_id=temp[1]
            sql_query = db.text("SELECT date_submitted FROM Survey.survey_answers WHERE id=%i;"%temp[2])
            connection = db.session.connection()
            date = connection.execute(sql_query)
            date = date.fetchall()
            date = [item[0] for item in date]
            answer_id=temp[0]
            temp[2]=question[0]
            temp[1]=date[0]
            if temp[3] is not None:
                temp.remove(temp[4])
                temp.remove(temp[4])
            elif temp[4] is not None:
                temp.remove(temp[3])
                temp.remove(temp[4])
            elif temp[5] is not None:
                sql_query = db.text("SELECT option_text FROM Survey.question_options WHERE id=%i;"%temp[5])
                connection = db.session.connection()
                option = connection.execute(sql_query)
                option = option.fetchall()
                option = [item[0] for item in option]
                temp[5]=option[0]
                temp.remove(temp[3])
                temp.remove(temp[3])
            else:
                sql_query = db.text("SELECT option_id FROM Survey.multiple_answers WHERE answer_id=%i;"%answer_id)
                connection = db.session.connection()
                options = connection.execute(sql_query)
                options = options.fetchall()
                answers = []
                for i in options:
                    sql_query = db.text("SELECT option_text FROM Survey.question_options WHERE question_id={} AND position={};".format(question_id,i[0]))                    
                    connection = db.session.connection()
                    option = connection.execute(sql_query)
                    option = option.fetchall()
                    option = [item[0] for item in option]
                    answers.append(option[0])
                temp[5]=tuple(answers)
                temp.remove(temp[3])
                temp.remove(temp[3])
            temp.append(answer_id)
            results.append(tuple(temp))
        df = pd.DataFrame(results)
        df.columns=['id', 'date', 'question', 'answer', 'submission_id']
        df.to_csv(r'/Users/pyustecoladilla/Desktop/Data/%s_results'%title[0], index = False) # place 'r' before the path name to avoid errors in the path
        flash("Your results were downloaded succesfully!")
    return render_template('survey/results.html', survey=survey)

@bp.route('<int:survey_id>/visualize')
@login_required
def visualize_results(survey_id):
    survey = Survey.query.get(survey_id)
    if survey.creator_id != current_user.id:
        raise Forbidden()
    return render_template('survey/visualize.html', survey=survey)

@bp.route('<int:survey_id>/question/<int:question_id>/plot')
@login_required
def plot(survey_id,question_id):
    #from matplotlib import pyplot as plt
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from flask import Flask, render_template
    from io import BytesIO
    import base64
    import numpy as np


    img = BytesIO()
    sql_query = db.text("SELECT question_statement FROM Survey.questions WHERE id=%i;"%question_id)
    connection = db.session.connection()
    text = connection.execute(sql_query)
    text = text.fetchall()
    text = [item[0] for item in text]
    text=text[0]

    sql_query = db.text("SELECT position FROM Survey.questions WHERE id=%i;"%question_id)
    connection = db.session.connection()
    pos = connection.execute(sql_query)
    pos = pos.fetchall()
    pos = [item[0] for item in pos]
    pos=pos[0]

    #sql_questions = db.text("SELECT * FROM survey.question_answers WHERE survey.question_answers.survey_answer_id IN (SELECT survey.survey_answers.id FROM survey.survey_answers WHERE survey.survey_answers.survey_id=1);")

    survey = Survey.query.get(survey_id)
    question = Survey.query.get(question_id)
    sql_query = db.text("SELECT * FROM Survey.question_answers WHERE question_id={} AND survey_answer_id IN (SELECT id FROM Survey.survey_answers WHERE survey_id={});".format(question_id,survey_id))
    connection = db.session.connection()
    result = connection.execute(sql_query)
    result = [item for item in result]
    answer=[]
    for i in range(len(result)):
        temp=list(result[i])
        answer_id=temp[0]
        q_id=temp[1]
        if temp[3] is not None:
            temp.remove(temp[4])
            temp.remove(temp[4])
            answer.append(temp[3])
        elif temp[4] is not None:
            temp.remove(temp[3])
            temp.remove(temp[4])
            answer.append(temp[3])
        elif temp[5] is not None:
            sql_query = db.text("SELECT option_text FROM Survey.question_options WHERE id=%i;"%temp[5])
            connection = db.session.connection()
            option = connection.execute(sql_query)
            option = option.fetchall()
            option = [item[0] for item in option]
            temp[5]=option[0]
            temp.remove(temp[3])
            temp.remove(temp[3])
            answer.append(temp[3])
        else:
            sql_query = db.text("SELECT option_text FROM Survey.question_options WHERE question_id={} AND position IN (SELECT option_id FROM Survey.multiple_answers WHERE answer_id={});".format(q_id,answer_id))                    
            connection = db.session.connection()
            option = connection.execute(sql_query)
            option = option.fetchall()
            option = [item[0] for item in option]
            temp[5]=option
            temp.remove(temp[3])
            temp.remove(temp[3])
            for j in temp[3]:
                answer.append(j)
    plt.tight_layout()
    unique, counts = np.unique(answer, return_counts=True)
    plt.bar(unique, counts, align='center', alpha=0.5)
    plt.yticks(counts)
    plt.xticks(unique)
    plt.savefig(img, format='png')
    plt.close()


    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')

    return render_template('survey/plot.html', question=question,plot_url=plot_url,survey=survey, pos=pos, text=text)
    
@bp.route("/")
@login_required
def home():
    create_survey_form = CreateSurveyForm()
    return render_template("survey/home.html", form=create_survey_form)


@bp.route("/create", methods=['POST'])
@login_required
def create():
    form = CreateSurveyForm()
    if form.validate_on_submit():
        db.session.add(
            Survey(title=form.survey_title.data, description=form.survey_description.data, state=SurveyState.NEW,
                   creator_id=current_user.id))
        db.session.commit()
        return redirect(url_for('survey.home'))
    else:
        flash("Unsuccesful validation")
        return redirect(url_for('survey.home'))


@bp.route('/<int:survey_id>/details')
@login_required
def details(survey_id):
    survey = Survey.query.get(survey_id)
    if survey is None:
        raise NotFound()
    if survey.creator_id != current_user.id:
        raise Forbidden()
    if survey.state == SurveyState.NEW:
        question_form = CreateQuestionForm()
        return render_template('survey/details.html', survey=survey, question_form=question_form)
    return render_template('survey/details.html', survey=survey)


@bp.route('<int:survey_id>/change_state/<string:state>')
@login_required
def change_state(survey_id, state):
    survey = Survey.query.get(survey_id)
    if survey.creator_id != current_user.id:
        raise Forbidden()
    if not survey.questions:
        flash("Unable to change state: Missing questions")
        return redirect(url_for('survey.details', survey_id=survey.id))
    else:
        for question in survey.questions:
            if question.type == QuestionType.MULTIPLE_CHOICE or question.type == QuestionType.SINGLE_CHOICE:
                if not question.options:
                    flash("Unable to change state: Questions missing options argument")
                    return redirect(url_for('survey.details', survey_id=survey.id))
    survey.state = SurveyState[state]
    db.session.add(survey)
    db.session.commit()
    return redirect(url_for('survey.details', survey_id=survey.id))


@bp.route('<int:survey_id>/add_question', methods=['POST'])
@login_required
def add_question(survey_id):
    survey = Survey.query.get(survey_id)
    if survey.creator_id != current_user.id:
        raise Forbidden()
    form = CreateQuestionForm()
    if form.validate_on_submit():
        question = Question(question_statement=form.question_text.data, type=QuestionType[form.type.data],
                            survey_id=survey_id)
        if survey.questions:
            question.position = survey.questions[-1].position + 1
        else:
            question.position = 1
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('survey.details', survey_id=survey_id))
    else:
        flash("Unsuccesful validation")
        return redirect(url_for('survey.details', survey_id=survey_id))


@bp.route('<int:survey_id>/question/<int:question_id>/add_option', methods=['POST'])
@login_required
def add_question_option(survey_id, question_id):
    survey = Survey.query.get(survey_id)
    if survey.creator_id != current_user.id:
        raise Forbidden()
    options = request.get_json()
    option_objects = []
    for option in options:
        option_objects.append(QuestionOption(question_id=question_id, option_text=option))
    last_option_position = 0 if not Question.query.get(question_id).options else \
        Question.query.get(question_id).options[-1].position
    for index, option in enumerate(option_objects):
        option.position = last_option_position + index + 1
        db.session.add(option)
    db.session.commit()
    return "success"


@bp.route('<int:survey_id>/question/<int:question_id>/delete')
@login_required
def delete_question(survey_id, question_id):
    survey = Survey.query.get(survey_id)
    if survey.creator_id != current_user.id:
        raise Forbidden()
    question = Question.query.get(question_id)
    db.session.delete(question)
    db.session.commit()
    db.session.refresh(survey)
    if survey.questions:
        for index, question in enumerate(survey.questions):
            question.position = index + 1
    db.session.add(survey)
    db.session.commit()
    return redirect(url_for('survey.details', survey_id=survey_id))


@bp.route('<int:survey_id>/delete')
@login_required
def delete(survey_id):
    survey = Survey.query.get(survey_id);
    if survey.creator_id != current_user.id:
        raise Forbidden()
    db.session.delete(survey)
    db.session.commit()
    return redirect(url_for('survey.home'))


@bp.route('<int:survey_id>/results')
@login_required
def results(survey_id):
    survey = Survey.query.get(survey_id)
    if survey.creator_id != current_user.id:
        raise Forbidden()
    return render_template('survey/results.html', survey=survey)


@bp.route('<int:survey_id>/answer', methods=['POST', 'GET'])
def answer(survey_id):
    survey = Survey.query.get(survey_id)
    if survey is None:
        raise NotFound()
    if survey.state != SurveyState.ONLINE:
        raise NotFound()
    if request.method == 'POST':
        survey_answer = SurveyAnswer(survey_id=survey_id)
        db.session.add(survey_answer)
        db.session.flush()
        db.session.refresh(survey_answer)
        for key in request.form.keys():
            question = Question.query.get(int(key))
            if question.type == QuestionType.NUMBER:
                for value in request.form.getlist(key):
                    answer = QuestionAnswer(integer_answer=int(value), question_id=question.id,
                                            survey_answer_id=survey_answer.id)
                    db.session.add(answer)
                    db.session.commit()
            elif question.type == QuestionType.TEXT:
                for value in request.form.getlist(key):
                    answer = QuestionAnswer(text_answer=value, question_id=question.id,
                                            survey_answer_id=survey_answer.id)
                    db.session.add(answer)
                    db.session.commit()
            elif question.type == QuestionType.SINGLE_CHOICE:
                for value in request.form.getlist(key):
                    answer = QuestionAnswer(single_option_answer=int(value), question_id=question.id,
                                            survey_answer_id=survey_answer.id)
                    db.session.add(answer)
                    db.session.commit()
            else:
                answer = QuestionAnswer(survey_answer_id=survey_answer.id, question_id=question.id)
                db.session.add(answer)
                db.session.flush()
                db.session.refresh(answer)
                for value in request.form.getlist(key):
                    ans = MultipleAnswers(answer_id=answer.id, option_id=int(value))
                    db.session.add(ans)
                db.session.commit()
        flash("Submission completed!")
        return redirect(url_for('main.home'))
    else:
        return render_template('main/answer.html', survey=survey)




