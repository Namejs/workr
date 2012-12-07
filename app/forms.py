
from flask.ext.wtf import Form,TextField, TextAreaField, SubmitField, DateField, FileField
from flask.ext.wtf.html5 import EmailField

class PostForm(Form):
    city = TextField('city')
    craft = TextField('craft')
    description = TextAreaField('description', id='textField')
    email = EmailField('email')
    start_date = DateField()
    images = FileField('images')
    submit = SubmitField()

