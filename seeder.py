import csv
import uuid

# from flask.cli import with_appcontext
from surveyapi.models import db, Survey, Question, AnnotationSentences, SimpleChoice, RangeSliderChoice, SurveyGroups, TestSurveyGroups, TestAnnotationSentences
from surveyapi.create_app import create_app

# VERY IMPORTANT
MAX_QUOTA = 5
REMAINING_QUOTA = 5
NUM_OF_GROUPS = 85

NUM_OF_TEST_GROUPS = 3
MAX_TEST_QUOTA = 15
REMAINING_TEST_QUOTA = 15


def seed_personal_questions():
    # survey_old = Survey.query.filter_by(name='personal_questions').first()
    # db.session.delete(survey_old)
    # db.session.commit()

    survey = Survey(name="demographic_questions")
    questions = []

    # 1
    question_1 = Question(text='What is your gender?', type='radio', name='gender')
    question_1.simple_choices = [
        SimpleChoice(text='Female'),
        SimpleChoice(text='Male'),
        SimpleChoice(text='Other/Prefer not to say')
    ]
    questions.append(question_1)

    # 2
    question_2 = Question(text='What is your age?', type='text_field', name='age')
    questions.append(question_2)

    # 3
    question_3 = Question(text='What is the highest level of education you have completed?', type='radio', name='education')
    question_3.simple_choices = [
        SimpleChoice(text='8th grade'),
        SimpleChoice(text='Some high school'),
        SimpleChoice(text='High school graduate'),
        SimpleChoice(text='Vocational or technical school'),
        SimpleChoice(text='Some college'),
        SimpleChoice(text='Associate degree'),
        SimpleChoice(text='Bachelor’s degree'),
        SimpleChoice(text='Graduate work'),
        SimpleChoice(text='I prefer not to say')
    ]
    questions.append(question_3)

    # 4
    question_4 = Question(text='What is the level of your English proficiency?', type='radio', name='native_english_speaker')
    question_4.simple_choices = [
        SimpleChoice(text='Native speaker'),
        SimpleChoice(text='Near-native speaker'),
        SimpleChoice(text='Non-native speaker'),
    ]
    questions.append(question_4)

    survey.questions = questions
    db.session.add(survey)
    db.session.commit()


def seed_ideology_questions():
    # survey_old = Survey.query.filter_by(name='ideology_questions').first()
    # db.session.delete(survey_old)
    # db.session.commit()

    survey = Survey(name="ideology_questions")
    ideology_questions = []

    # 1
    question_1 = Question(
        text='Do you consider yourself to be liberal, conservative or somewhere in between?',
        type='range_slider',
        name='political_ideology'
    )
    question_1.range_slider_choices = [
        RangeSliderChoice(
            min_range=-10,
            max_range=10,
            label_left_side='Very liberal',
            label_right_side='Very conservative'
        )
    ]
    ideology_questions.append(question_1)

    # 2
    question_2 = Question(
        text='How often on an average do you check the news?',
        type='radio',
        name='news_check_frequency'
    )
    question_2.simple_choices = [
        SimpleChoice(text='Never'),
        SimpleChoice(text='Very rarely'),
        SimpleChoice(text='Several times per month'),
        SimpleChoice(text='Several times per week'),
        SimpleChoice(text='Every day'),
        SimpleChoice(text='Several times per day')
    ]
    ideology_questions.append(question_2)


    # 3
    question_3 = Question(text='Please select AT LEAST one news outlets that you follow.', type='checkbox', name='followed_news_outlets')
    question_3.simple_choices = [
        SimpleChoice(text='Fox News'),
        SimpleChoice(text='Fox News'),
        SimpleChoice(text='New York Times'),
        SimpleChoice(text='CNN'),
        SimpleChoice(text='MSNBC'),
        SimpleChoice(text='Reuters'),
        SimpleChoice(text='Breitbart'),
        SimpleChoice(text='The Federalist'),
        SimpleChoice(text='Huffington Post'),
        SimpleChoice(text='New York Post'),
        SimpleChoice(text='Alternet'),
        SimpleChoice(text='USA Today'),
        SimpleChoice(text='ABC News'),
        SimpleChoice(text='CBS News'),
        SimpleChoice(text='Univision'),
        SimpleChoice(text='The Washington Post'),
        SimpleChoice(text='The Wall Street Journal'),
        SimpleChoice(text='The Guardian'),
        SimpleChoice(text='BuzzFeed'),
        SimpleChoice(text='Vice'),
        SimpleChoice(text='Time magazine'),
        SimpleChoice(text='Business Insider')
    ]
    ideology_questions.append(question_3)

    survey.questions = ideology_questions
    db.session.add(survey)
    db.session.commit()


def seed_iqc_questions():

    survey = Survey(name="info_quality_control")
    questions = []

    # 1
    question_1 = Question(text='How is bias connected to the sentiment?', type='radio', name='bias_sentiment')
    question_1.simple_choices = [
        SimpleChoice(text='Bias is the same as negative sentiment'),
        SimpleChoice(text='Bias is the same as positive sentiment'),
        SimpleChoice(text='Bias can be both positive, negative or even not have particular sentiment'),
        SimpleChoice(text='Bias is not connected to sentiment at all')
    ]
    questions.append(question_1)

    survey.questions = questions
    db.session.add(survey)
    db.session.commit()


def seed_annotation_questions():

    # survey_old = Survey.query.filter_by(name='annotation_questions').first()
    # db.session.delete(survey_old)
    # db.session.commit()

    survey = Survey(name="annotation_questions")
    questions = []

    # 1
    question_1 = Question(text='Please highlight words or phrases that you think introduce bias or convey strong opinions/emotions in the sentence displayed above.', type='highlight', name='sentence_bias_annotation')
    questions.append(question_1)

    # 2
    question_2 = Question(text='Do you find the above sentence as biased or non-biased?', type='radio',
                          name='sentence_bias_label')
    question_2.simple_choices = [
        SimpleChoice(text='Biased'),
        SimpleChoice(text='Non-biased')
    ]
    questions.append(question_2)

    # 3
    question_3 = Question(
        text='Would you say that the sentence is entirely factual or expresses the writer’s opinion?',
        type='radio',
        name='sentence_opinion_fact'
    )
    question_3.simple_choices = [
        SimpleChoice(text='Entirely factual'),
        SimpleChoice(text='Expresses writer’s opinion'),
        SimpleChoice(text='Somewhat factual but also opinionated')
    ]
    questions.append(question_3)

    survey.questions = questions
    db.session.add(survey)
    db.session.commit()


def create_groups():
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    db.init_app(app)
    for i in range(1, NUM_OF_GROUPS+1):
        group = SurveyGroups(id=i, max_quota=MAX_QUOTA, remaining_quota=REMAINING_QUOTA)
        db.session.add(group)
        db.session.commit()
    ctx.pop()


def seed_annotation_sentences():
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    db.init_app(app)
    with open('sentences_grouped_reshuffled.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            annotation_sentence = AnnotationSentences(
                id=uuid.uuid4().hex,
                text=row['sentence'],
                link=row['news_link'],
                type=row['type'],
                topic=row['topic'],
                outlet=row['outlet'],
                group_id=int(row['group_id'])
            )
            db.session.add(annotation_sentence)
            db.session.commit()
    ctx.pop()


def create_test_groups():
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    db.init_app(app)
    for i in range(1, NUM_OF_TEST_GROUPS+1):
        group = TestSurveyGroups(id=i, max_quota=MAX_TEST_QUOTA, remaining_quota=REMAINING_TEST_QUOTA)
        db.session.add(group)
        db.session.commit()
    ctx.pop()


def seed_test_annotation_sentences():
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    db.init_app(app)
    with open('sentences_test.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            annotation_sentence = TestAnnotationSentences(
                id=uuid.uuid4().hex,
                text=row['sentence'],
                link=row['news_link'],
                type=row['type'],
                topic=row['topic'],
                outlet=row['outlet'],
                group_id=int(row['group_id'])
            )
            db.session.add(annotation_sentence)
            db.session.commit()
    ctx.pop()


if __name__ == '__main__':
    # seed_personal_questions()
    # seed_ideology_questions()
    # seed_iqc_questions()
    # seed_annotation_questions()
    create_test_groups()
    seed_test_annotation_sentences()
    # create_groups()
    # seed_annotation_sentences()
