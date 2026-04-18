from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(min=1, max=200)])
    content = TextAreaField("Content", validators=[DataRequired(), Length(min=10)])
    tags = StringField("Tags (comma-separated)", validators=[Length(max=500)])
    submit = SubmitField("Save Post")
