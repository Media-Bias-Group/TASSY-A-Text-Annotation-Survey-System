import csv
import sys

from surveyapi.models import db, Survey, Question, AnnotationSentences, SimpleChoice, RangeSliderChoice, SurveyGroups, TestSurveyGroups, TestAnnotationSentences, TestAnnotations, SurveyRecord
from surveyapi.create_app import create_app
from prettytable import PrettyTable
from sqlalchemy import text

def print_annotations():
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    db.init_app(app)
    all_annotations = TestAnnotations.query.all()
    for annotation in all_annotations:
        print(annotation.to_dict())
    ctx.pop()

def detailed_user_record_to_csv():
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    db.init_app(app)

    with open('detailed_user_record_mturk_22_07_2020.csv', mode='w') as csv_file:
        fieldnames = ['id', 'mturk_id', 'age', 'gender', 'education', 'native_english_speaker', 'political_ideology', 'followed_news_outlets', 'news_check_frequency', 'survey_completed']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        ''' First, get the annotation bundle '''
        sql_str = 'SELECT survey_record_id, sentence_group_id, COUNT(*) as count FROM survey_annotations GROUP BY survey_record_id ORDER BY count'
        sql = text(sql_str)
        # result = [dict(row) for row in db.session.execute(sql)]
        for row in db.session.execute(sql):
            survey_record_id = dict(row)['survey_record_id']
            annotation_count = dict(row)['count']

            ''' Then, get the detailed records for each id '''
            selection = "select identifier_key, age, gender, education, political_ideology, native_english_speaker, followed_news_outlets, news_check_frequency, demographics.survey_record_id "
            from_stm = "from demographics "
            joins = "inner join ideologies on demographics.survey_record_id = ideologies.survey_record_id inner join survey_record on survey_record.id=ideologies.survey_record_id "
            whr = "where survey_record.id='"
            sql_str_2 = selection + from_stm + joins + whr + survey_record_id + "'"

            sql_2 = text(sql_str_2)
            result_2 = db.session.execute(sql_2)
            for row_2 in result_2:
                record = dict(row_2)
                print(record)
                mturk_id = record['identifier_key']
                age = record['age']
                gender = SimpleChoice.query.get(record['gender']).to_dict()['text']
                education = SimpleChoice.query.get(record['education']).to_dict()['text']
                native_english_speaker = SimpleChoice.query.get(record['native_english_speaker']).to_dict()['text']
                political_ideology = record['political_ideology']
                followed_news_outlets = record['followed_news_outlets'].split(',')
                converted_news_outlets = []
                for outlet in followed_news_outlets:
                    if (outlet.isdigit()):
                        ot = SimpleChoice.query.get(outlet).to_dict()['text']
                        converted_news_outlets.append(ot)
                    else:
                        converted_news_outlets.append(outlet)
                news_check_frequency = SimpleChoice.query.get(record['news_check_frequency']).to_dict()['text']
                survey_completed = annotation_count >= 10

                writer.writerow({
                    'id': survey_record_id,
                    'mturk_id': mturk_id,
                    'age': age,
                    'gender': gender,
                    'education': education,
                    'native_english_speaker': native_english_speaker,
                    'political_ideology': political_ideology,
                    'followed_news_outlets': converted_news_outlets,
                    'news_check_frequency': news_check_frequency,
                    'survey_completed': survey_completed
                })

    print('csv generated...')
    ctx.pop()

def annotations_to_csv():
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    db.init_app(app)

    sql_str = 'select survey_record_id, created_at, label, words, factual, sentence_group_id, annotation_sentence_id  from survey_annotations ORDER BY created_at'
    sql = text(sql_str)
    fieldnames = ['survey_record_id', 'sentence_id', 'sentence_group_id', 'created_at', 'label', 'words', 'factual']

    with open('annotations_mturk_22_07_2020.csv', mode='w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for row in db.session.execute(sql):
            record = dict(row)
            survey_record_id = record['survey_record_id']
            created_at = record['created_at']
            label = SimpleChoice.query.get(record['label']).to_dict()['text']
            words = record['words']
            factual = SimpleChoice.query.get(record['factual']).to_dict()['text']
            sentence_group_id = record['sentence_group_id']
            sentence_id = record['annotation_sentence_id']

            writer.writerow({
                'survey_record_id': survey_record_id,
                'sentence_id': sentence_id,
                'sentence_group_id': sentence_group_id,
                'created_at': created_at,
                'label': label,
                'words': words,
                'factual': factual
            })

    print('csv generated...')
    ctx.pop()


def all_sentences_to_csv():
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    db.init_app(app)

    fieldnames = ['id', 'group_id', 'text', 'link', 'type', 'topic', 'outlet']

    sql_str = 'select id, group_id, text as sentence, link, type, topic, outlet from annotation_sentences'
    from sqlalchemy import text
    sql = text(sql_str)

    with open('all_sentences_with_ids.csv', mode='w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for row in db.session.execute(sql):
            record = dict(row)
            id = record['id']
            group_id = record['group_id']
            text = record['sentence']
            link = record['link']
            type = record['type']
            topic = record['topic']
            outlet = record['outlet']

            writer.writerow({
                'id': id,
                'group_id': group_id,
                'text': text,
                'link': link,
                'type': type,
                'topic': topic,
                'outlet': outlet
            })

    print('csv generated...')
    ctx.pop()





if __name__ == '__main__':
    globals()[sys.argv[1]]()