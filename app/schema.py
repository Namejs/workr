from mongoengine import connect, StringField, ReferenceField, DateTimeField, ComplexDateTimeField, Document, \
                        ListField, IntField, BooleanField

connect('works')

class Rating(Document):
    count = IntField()
    total_ratings = IntField()
    average = IntField()

class User(Document):
    email = StringField()
    password = StringField()
    accept_tos = BooleanField
    created = ComplexDateTimeField()
    created = ComplexDateTimeField()
    confirmed   = BooleanField()
    active = BooleanField()
    rating = ReferenceField(Rating)

class Bid(Document):
    amount = IntField()
    bidder = ReferenceField(User)

class Craft(Document):
    craft = StringField()

class City(Document):
    city = StringField(unique=True)

class Image(Document):
    image = StringField()
    thumbnail = StringField()

class QuestionAnswer(Document):
    question        = StringField()
    question_author = ReferenceField(User)
    answer          = StringField()
    answer_author   = ReferenceField(User)

class Post(Document):
    sub_url = StringField()
    author = ReferenceField(User)
    craft = ReferenceField(Craft)
    city = ReferenceField(City)
    description = StringField()
    creation_date = ComplexDateTimeField()
    start_date = DateTimeField()
    images = ListField(ReferenceField(Image))
    bids = ListField(ReferenceField(Bid))
    question = ReferenceField(QuestionAnswer)

    meta = {'allow_inheritance':True}





