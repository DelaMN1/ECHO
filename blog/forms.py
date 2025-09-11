from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class PostForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(), 
        Length(min=1, max=200, message='Title must be between 1 and 200 characters')
    ])
    content = TextAreaField('Content', validators=[
        DataRequired(), 
        Length(min=10, message='Content must be at least 10 characters')
    ])
    tags = StringField('Tags (comma-separated)', validators=[
        Length(max=500, message='Tags must be less than 500 characters')
    ])
    submit = SubmitField('Save Post')