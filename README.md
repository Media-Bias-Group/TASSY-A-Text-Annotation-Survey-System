# TASSY— A Text Annotation Survey System 

TASSY is a web-based survey application built using Flask and Vue.js. The app allows combining classic survey functionality, such as posing single-choice, multiple-choice, and slider questions, with text annotation functionality, i.e., allowing participants to select and annotate words or phrases in a provided text. 

## Demo

https://unisurveyapp.pythonanywhere.com/

## To run the application locally

1) Resolve all dependencies in requirements.txt.
2) Set up a local flask server.
3) Add this line `app.run(0.0.0.0)` at the end of the file `flask_app.py`.
4) Configure a local MySQL or SQLite server and make the appropriate changes in `surveyapi.models.db` to get the database up and running.

## Application structure and hierarchies

- Models for basic survey questions, such as single-choice and multiple-choice questions, chips select, range sliders, and text highlights already exist in `surveyapi.models`
- To create new models, please perform the appropriate DB migrations as per the configuration of your flask and database servers.
- The following models (and corresponding tables) exist in the survey and can be used out-of-the-box:
> 1. **SurveyRecord**: Holds the parent object generated from a perticipant’s responses, such as *DataConsent*, *Demographics*, *Ideologies* and *QualityControl*.
> 2. **SurveyGroups**: Groups the sentences that are to be annotated. It also holds the max quota variable of the groups.
> 3. **Survey**: Container for various types of surveys, such as demographics, ideologies etc.
> 4. **Question**: Holds a survey question. It can be specified with the type of response the question should hold.
> 3. **AnnotationSentences**: Actual sentences that are to be annotated. Also holds other properties, such as publication, URLs, etc.
> 4. **Annotations**: Holds the words/phrases highlighted/annotated by the participants.

File seeder.py serves to seed and populate the platform database with questions etc.

## Creating a simple demographic question with single choice select

Run the file seeder.py with these lines of code.

```python
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

survey.questions = questions
db.session.add(survey)
db.session.commit()
```


## Creating a simple ideological question with a range slider input

Run the file seeder.py with these lines of code.

```python
survey = Survey(name="ideology_questions")
ideology_questions = []
question_1 = Question(
    text='Do you consider yourself to be liberal, conservative, or somewhere in between?',
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
survey.questions = ideology_questions
db.session.add(survey)
db.session.commit()
```

## Seeding annotation sentences

In the file seeder.py, use the function `seed_annotation_sentences()`.

```python
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

seed_annotation_sentences()
```

The function expects a CSV file such as the following https://github.com/Media-Bias-Analysis-Group/SAQ_text_annotation_and_question_survey_tool/blob/master/sentences_grouped_reshuffled.csv

## Seeding survey questions

In the file seeder.py, use the functions 

1. `seed_personal_questions()`
2. `seed_ideology_questions()`
3. `seed_annotation_questions()`
4. `create_groups()`


## Extracting the survey output

The output is extracted in CSV format. Use the command below to open the interactive python shell.

`python -i db_helper.py`

Get the db 
`db, ctx = create_db_client()`

Get all the survey worker records as CSV
`to_csv_survey_worker_records(db, ctx, after_date=optional)`

Get all the survey annotations as CSV
`to_csv_all_annotations(db, ctx, after_date=optional)`
