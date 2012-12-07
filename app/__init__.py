from flask import Flask, render_template, request, url_for, redirect, jsonify, json, session, escape
from werkzeug.utils import secure_filename
import os, datetime, time

app = Flask(__name__)

app.config.from_pyfile('config.cfg')
app.config['TRAP_BAD_REQUEST_ERRORS'] = True
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


from forms import *
import schema
from imgconv import imgconv


@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/index', methods=['GET', 'POST', 'PUT', 'DELETE'])
def index():

    if request.method == 'PUT':

        if 'sub_url' in session:
            sub_url = session['sub_url']
            post = schema.Post.objects(sub_url=sub_url).first()

            images  = request.files.getlist('images')

            for image in images:
                imgconv(image, sub_url, post)

            post = schema.Post.objects(sub_url=sub_url).first()

            images = post.images

            return render_template('images_bu.html', images=images)

        else:
            images  = request.files.getlist('images')
            post = schema.Post().save()
            sub_url = post.sub_url = str(post.id)[-5:]
            session['sub_url'] = sub_url
            post.sub_url = sub_url
            post.save()

            for image in images:
                imgconv(image, sub_url, post)

            post = schema.Post.objects(sub_url=sub_url).first()

            return render_template('images_bu.html', images=post.images)

    elif request.method == 'POST':

        if 'sub_url' in session:
            sub_url = session['sub_url']
            post = schema.Post.objects(sub_url=sub_url)

            email        = request.form['email']
            craft        = request.form['craft']
            city         = request.form['city']
            description  = request.form['description']

            st_date      = map(int, request.form['start_date'].split('/'))
            st_date_day  = st_date[0]
            st_date_mth  = st_date[1]
            st_date_yr   = st_date[2]
            start_date   = datetime.date(st_date_yr, st_date_mth, st_date_day)

            (user, is_new)  = schema.User.objects.get_or_create(email=email)
            (craft, is_new) = schema.Craft.objects.get_or_create(craft=craft)
            (city, is_new)  = schema.City.objects.get_or_create(city=city)

            post.description   = description
            post.craft         = craft
            post.city          = city
            post.author        = user
            post.creation_date = datetime.datetime.now()
            post.start_date    = start_date


            post.save()

            session.pop('sub_url', None)

            return redirect(url_for('post', sub_url=sub_url))

        else:
            post    = schema.Post().save()
            sub_url = post.sub_url = str(post.id)[-5:]

            email        = request.form['email']
            craft        = request.form['craft']
            city         = request.form['city']
            description  = request.form['description']

            st_date      = map(int, request.form['start_date'].split('/'))
            st_date_day  = st_date[0]
            st_date_mth  = st_date[1]
            st_date_yr   = st_date[2]
            start_date   = datetime.date(st_date_yr, st_date_mth, st_date_day)

            (user, is_new)  = schema.User.objects.get_or_create(email=email)
            (craft, is_new) = schema.Craft.objects.get_or_create(craft=craft)
            (city, is_new)  = schema.City.objects.get_or_create(city=city)

            post.description   = description
            post.craft         = craft
            post.city          = city
            post.author        = user
            post.creation_date = datetime.datetime.now()
            post.start_date    = start_date
            post.sub_url       = sub_url

            post.save()

            return redirect(url_for('post', sub_url=sub_url))

    elif request.method == 'DELETE':
        pass



#        images  = request.files.getlist('images')

#        sub_url = request.form['sub_url']

#        post = schema.Post.objects(sub_url=sub_url).first()
#        post = schema.Post().save()
#        post.sub_url = str(post.id)[-5:]
#        sub_url = post.sub_url
#        post.save()
#
#        for image in images:
#            imgconv(image, sub_url, post)
#
#        post = schema.Post.objects(sub_url=sub_url).first()
#
#        return render_template('images_bu.html', images=post.images)

    else:
        def import_cities():
            with open('app/static/pilsetas.txt', 'r') as f:

                text = [line.strip() for line in f]
                return json.dumps(text)

        date_today= datetime.date.today()
        date = str(date_today.day) + '/' + str(date_today.month) + '/' + str(date_today.year)

        return render_template('index.html',
                                cities = import_cities(),
                                date   = date)


@app.route('/post/<sub_url>', methods=['POST', 'GET'])
def post(sub_url):
    post       = schema.Post.objects(sub_url=sub_url).first()
    created_on = post.creation_date

    return render_template('post.html',
                            craft        = post.craft.craft,
                            city         = post.city.city,
                            description  = post.description,
                            user         = post.author.email,
                            sub_url      = sub_url,
#                            images       = post.images,
                            created_on   = created_on,
                            start_date   = post.start_date)

@app.route('/list')
def list():
    list = reversed(schema.Post.objects().all())
    return render_template('list.html', list=list)

@app.route('/jquery', methods=['POST', 'GET'])
def jquery():
    if request.method == 'POST':
        data = request.form

        rating = data['rating']
        try:
            tr = schema.Rating.objects().first()
            tr.total_ratings += int(rating)
            tr.count += 1
            tr.save()
        except AttributeError:
            tr = schema.Rating().save()
            tr.total_ratings = int(rating)
            tr.count = 1
            tr.save()

        average_rating = tr.total_ratings / tr.count

        return render_template('result.html', rating=rating,  count=tr.count, average_rating=average_rating)
    else:
        return render_template('jquery.html')


@app.route('/images', methods=['POST', 'GET', 'DELETE'])
def images():

    if request.method == 'POST':
        images = request.files.getlist('image')

        for image in images:
            imgconv(image)

        images = schema.Image.objects().all()

        return render_template('images_bu.html', images = images)

    elif request.method == 'DELETE':

        delete_file = request.data

        im_delete = schema.Images.objects(thumbnail=delete_file)
        im_delete.delete()

        def delete_files(f):
            f = f.split('_')[0]
            f = f.split('/')
            striped_str =  f.pop()
            dir_list = os.listdir('app/static/images/save')
            files_to_delete = [s for s in dir_list if striped_str in s]

            for f in files_to_delete:
                os.remove('app/static/images/save/' + f)

        delete_files(delete_file)

        images = schema.Image.objects().all()

        return render_template('images.html', images=images)

    else:

        images = schema.Image.objects().all()
        return render_template('images.html', images=images)

@app.route('/form', methods=['POST', 'GET'])
def form():
    def import_cities():
        with open('app/static/pilsetas.txt', 'r') as f:

            text = [line.strip() for line in f]
            return json.dumps(text)

    return render_template('form.html', cities = import_cities())

@app.route('/test', methods=['POST', "GET"])
def test():
    return render_template('test.html')