import csv
import sys
import pandas as pd

from surveyapi.models import db, Survey, Question, AnnotationSentences, SimpleChoice, RangeSliderChoice, SurveyGroups, TestSurveyGroups, TestAnnotationSentences, TestAnnotations, SurveyRecord, Annotations
from surveyapi.create_app import create_app
from prettytable import PrettyTable
from sqlalchemy import text
from sqlalchemy import create_engine
from pprint import pprint
from collections import OrderedDict

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="user",
    password="pass@vv",
    hostname="host",
    databasename="db"
)

MAX_QUOTA = 10

def create_db_client():
    app = create_app()
    ctx = app.app_context()
    db.init_app(app)
    return db, ctx

def get_empty_annotations(db, ctx, after_date='2000-10-10 00:00:00'):
    t = PrettyTable(['identifier_key', 'survey_record_id', 'sentence_group_id', 'worker_started_at', 'count'])
    ctx.push()
    count = 0
    sql_str = """
        SELECT identifier_key, survey_record_id, sentence_group_id, survey_record.created_at, COUNT(*) as count
        FROM survey_annotations
        INNER JOIN survey_record ON survey_record.id = survey_annotations.survey_record_id
        WHERE survey_record.created_at > '""" + after_date + """'
        AND (SELECT COUNT(*) FROM survey_annotations WHERE survey_annotations.words = '' AND survey_annotations.label = 49 AND survey_annotations.survey_record_id = survey_record.id) >= 20
        GROUP BY survey_record_id
        ORDER BY survey_record.created_at;
        """
    sql = text(sql_str)
    result = db.session.execute(sql)
    for row in result:
        t.add_row([dict(row)['identifier_key'], dict(row)['survey_record_id'], dict(row)['sentence_group_id'], dict(row)['created_at'], dict(row)['count'] ])
        count += 1
    print(t)
    print("\n{} results. ".format(count))
    ctx.pop()

def get_survey_worker_status(db, ctx, after_date='2000-10-10 00:00:00'):
    t = PrettyTable(['identifier_key', 'survey_record_id', 'sentence_group_id', 'worker_started_at', 'count'])
    ctx.push()
    count = 0
    sql_str = """
        SELECT identifier_key, survey_record_id, sentence_group_id, survey_record.created_at, COUNT(*) as count
        FROM survey_annotations
        INNER JOIN survey_record ON survey_record.id = survey_annotations.survey_record_id
        WHERE survey_record.created_at > '""" + after_date + """'
        GROUP BY survey_record_id
        ORDER BY survey_record.created_at;
        """
    sql = text(sql_str)
    result = db.session.execute(sql)
    for row in result:
        t.add_row([dict(row)['identifier_key'], dict(row)['survey_record_id'], dict(row)['sentence_group_id'], dict(row)['created_at'], dict(row)['count'] ])
        count += 1
    print(t)
    print("\n{} results. ".format(count))
    ctx.pop()

def get_annotation_status(db, ctx, after_date='2000-10-10 00:00:00'):
    t = PrettyTable(['survey_record_id', 'created_at', 'label', 'words', 'factual', 'sentence_group_id'])
    ctx.push()
    count = 0
    sql_str = """
        SELECT survey_record_id, created_at, label, words, factual, sentence_group_id
        FROM survey_annotations
        WHERE created_at > '""" + after_date + """'
        ORDER BY created_at;
        """
    sql = text(sql_str)
    result = db.session.execute(sql)
    for row in result:
        t.add_row([dict(row)['survey_record_id'], dict(row)['created_at'], dict(row)['label'], dict(row)['words'], dict(row)['factual'], dict(row)['sentence_group_id'] ])
        count += 1
    print(t)
    print("\n{} results. ".format(count))
    ctx.pop()

def to_csv_survey_worker_records(db, ctx, after_date='2000-10-10 00:00:00'):
    ctx.push()
    with open('detailed_user_record_mturk_{}.csv'.format(after_date), mode='w') as csv_file:
        fieldnames = ['id', 'mturk_id', 'age', 'gender', 'education', 'native_english_speaker', 'political_ideology', 'followed_news_outlets', 'news_check_frequency', 'survey_completed']
        t = PrettyTable(fieldnames)
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        # First, get all worker status
        sql_str = """
            SELECT identifier_key, survey_record_id, sentence_group_id, survey_record.created_at, COUNT(*) as count
            FROM survey_annotations
            INNER JOIN survey_record ON survey_record.id = survey_annotations.survey_record_id
            WHERE survey_record.created_at > '""" + after_date + """'
            GROUP BY survey_record_id
            ORDER BY survey_record.created_at;
            """
        sql = text(sql_str)
        for row in db.session.execute(sql):
            survey_record_id = dict(row)['survey_record_id']
            annotation_count = dict(row)['count']

            # Then, get the detailed records for each id
            sql_str_2 = """
                SELECT identifier_key, age, gender, education, political_ideology, native_english_speaker, followed_news_outlets, news_check_frequency, demographics.survey_record_id
                FROM demographics
                INNER JOIN ideologies on demographics.survey_record_id = ideologies.survey_record_id
                INNER JOIN survey_record on survey_record.id=ideologies.survey_record_id
                WHERE survey_record.id = '""" + survey_record_id + """'
                ;
                """
            sql_2 = text(sql_str_2)

            # selection = "select identifier_key, age, gender, education, political_ideology, native_english_speaker, followed_news_outlets, news_check_frequency, demographics.survey_record_id "
            # from_stm = "from demographics "
            # joins = "inner join ideologies on demographics.survey_record_id = ideologies.survey_record_id inner join survey_record on survey_record.id=ideologies.survey_record_id "
            # whr = "where survey_record.id='"
            # sql_str_2 = selection + from_stm + joins + whr + survey_record_id + "'"
            # sql_2 = text(sql_str_2)

            result_2 = db.session.execute(sql_2)
            for row_2 in result_2:
                record = dict(row_2)
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
                survey_completed = annotation_count >= 20

                t.add_row([survey_record_id, mturk_id, age, gender, education, native_english_speaker, political_ideology, converted_news_outlets, news_check_frequency, survey_completed ])

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
        # print(t)
        ctx.pop()

def to_csv_all_annotations(db, ctx, after_date='2000-10-10 00:00:00'):
    ctx.push()
    fieldnames = ['survey_record_id', 'sentence_id', 'sentence_group_id', 'created_at', 'label', 'words', 'factual']
    t = PrettyTable(fieldnames)
    with open('annotations_mturk_{}.csv'.format(after_date), mode='w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        count = 0
        sql_str = """
            SELECT survey_record_id, created_at, label, words, factual, sentence_group_id, annotation_sentence_id
            FROM survey_annotations
            WHERE created_at > '""" + after_date + """'
            ORDER BY created_at;
            """
        sql = text(sql_str)
        result = db.session.execute(sql)
        for row in result:
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
            count += 1
            t.add_row([survey_record_id, sentence_id, sentence_group_id, created_at, label, words, factual])
        print('csv generated...')
        # print(t)
        print("\n{} results. ".format(count))
        ctx.pop()


def get_groups_status(db, ctx):
    ctx.push()
    # Get all groups
    all_groups = [row.id for row in SurveyGroups.query.with_entities(SurveyGroups.id).all()]
    sql_str = """
        SELECT identifier_key, survey_record_id, sentence_group_id, survey_record.created_at, COUNT(*) as count
        FROM survey_annotations
        INNER JOIN survey_record ON survey_record.id = survey_annotations.survey_record_id
        WHERE (SELECT COUNT(*) FROM survey_annotations WHERE survey_annotations.words = '' AND survey_annotations.label = 49 AND survey_annotations.survey_record_id = survey_record.id) >= 20
        GROUP BY survey_record_id
        ORDER BY survey_record.created_at;
        """
    sql = text(sql_str)
    empty_annotations = [dict(row) for row in db.session.execute(sql)]

    empty_groups = {}

    for row in empty_annotations:
        if row['sentence_group_id'] not in empty_groups:
            key = row['sentence_group_id']
            if key is not None:
                empty_groups.update({key: 1})
        else:
            key = row['sentence_group_id']
            old_val = empty_groups[key]
            if key is not None:
                empty_groups.update({key: old_val + 1})

    # Get the current annotations
    sql = text('SELECT survey_record_id, sentence_group_id, COUNT(*) as count FROM survey_annotations GROUP BY survey_record_id')
    result = [dict(row) for row in db.session.execute(sql)]

    # If nothing is annotated yet
    if len(result) == 0:
        return all_groups

    # Filter the result and calculate annotated sentences' group frequency
    GROUP_SENTENCE_COUNT = 20
    grp_freq = {}
    for row in result:
        if row['count'] >= GROUP_SENTENCE_COUNT:
            if row['sentence_group_id'] not in grp_freq:
                key = row['sentence_group_id']
                if key is not None:
                    grp_freq.update({key: 1})
            else:
                key = row['sentence_group_id']
                if key is not None:
                    old_val = grp_freq[key]
                    grp_freq.update({key: old_val + 1})
        else:
            if row['sentence_group_id'] not in grp_freq:
                key = row['sentence_group_id']
                if key is not None:
                    grp_freq.update({key: 0})
            else:
                continue

    for (key, value) in grp_freq.items():
        if key in empty_groups:
            grp_freq[key] = grp_freq[key] - empty_groups[key]

    for key in sorted(grp_freq):
        print ("%s: %s" % (key, grp_freq[key]))

    ordered_group_status = OrderedDict({k: v for k, v in sorted(grp_freq.items(), key=lambda item: item[1])})

    print('Ordered status => ')
    t_1 = PrettyTable(['group_id', 'current_quota'])
    for key in ordered_group_status:
        t_1.add_row([key, ordered_group_status[key]])
    print(t_1)

    persons = 0

    dfs = pd.read_excel('quotas14.08.xlsx', sheet_name=None)

    dfs = dfs['Sheet1']

    # print(dfs)

    df_1 = dfs[(dfs['survey_record_id'] < 10)]

    # print(df_1)

    df_2 = df_1['survey_record_id'].apply(recalc_quota)

    print(df_2)

    updated_quotas_dict = df_2.to_dict()

    print(updated_quotas_dict)

    all_groups_proxy = all_groups
    for (key, value) in grp_freq.items():
        if value >= MAX_QUOTA:
            if int(key) in updated_quotas_dict:
                if value >= updated_quotas_dict[key]:
                    all_groups_proxy.remove(int(key))
            else:
                all_groups_proxy.remove(int(key))
        else:
            persons = persons + (MAX_QUOTA - int(value))

    print('Available groups for annotation => {}'.format(len(all_groups_proxy)))
    print(all_groups_proxy)

    print('Number of people that can still take the survey => {}'.format(persons))

    if len(all_groups_proxy) == 0:
        print('WARNING: GROUP QUOTAS FULL!')




    # l = list(grp_freq.items())
    # l.sort()

    # print(dict(l))
    # count = 0

    # for (key, value) in dict(l).items():
    #     count += 1
    #     print("key: {} -- Value: {}".format(key, value))
    # print('{} results.'.format(count))

def recalc_quota(curr_quota):
    return MAX_QUOTA + (MAX_QUOTA - curr_quota)

# def get_available_groups(db, ctx):
#     ctx.push()
    # engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)

    # sql = 'SELECT survey_record_id, label, words, factual, sentence_group_id, annotation_sentence_id FROM survey_annotations;'
    # query = pd.read_sql(sql, engine)
    # df_1 = pd.DataFrame(query, columns=['survey_record_id', 'label', 'words', 'factual', 'sentence_group_id', 'annotation_sentence_id'])

    # df_1.to_csv ('export_dataframe.csv', index = False, header=True)


    # print(df.head())
    # print(df_1.count())

    # df_1 = df_1[(df_1['words'].isnull()) & (df_1['label']=='Non-biased')]

    # df_2 = df_1.groupby(["survey_record_id", "sentence_group_id"], as_index=False)["annotation_sentence_id"].nunique()

    # print(df_new[df_new['annotation_sentence_id']==20])

    # df_xx = df_new[df_new['annotation_sentence_id']==20]

    # df_new_new = df_xx.groupby(["sentence_group_id"], as_index=False)["survey_record_id"].nunique()

    # print(df_new_new)

    # print(df.groupby("survey_record_id")["annotation_sentence_id"].nunique().to_frame())


    # all_annotations = Annotations.query.all()
    # print(len(all_annotations))
    # for i in range(5):
    #     print(all_annotations[i])
