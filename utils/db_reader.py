import csv
import uuid

# from flask.cli import with_appcontext
from ..surveyapi.models import db, Survey, Question, AnnotationSentences, SimpleChoice, RangeSliderChoice, SurveyGroups, TestSurveyGroups, TestAnnotationSentences, TestAnnotations
from ..surveyapi.create_app import create_app

def print_annotations():
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    db.init_app(app)
    all_annotations = TestAnnotations.query.all()
    print(all_annotations)
    ctx.pop()