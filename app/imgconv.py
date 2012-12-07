__author__ = 'Eddie'
import schema
import os
import Image
from PIL.ExifTags import TAGS
import random
import string
def get_exif(i):
    ret = {}
    info = i._getexif()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
    return ret

def id_generator(size=4, chars=string.ascii_lowercase +  string.digits):
    return  ''.join(random.choice(chars) for x in range(size))

def imgconv(images, sub_url, post):

    url_for_uploads = 'app/static/images/' + sub_url

    if not os.path.exists(url_for_uploads):
        os.makedirs(url_for_uploads)

    random_id = id_generator()


    images.save(url_for_uploads + '/' + sub_url + '_' + 'orig' + '_' + images.filename)

    img_raw =   url_for_uploads + '/' + sub_url + '_' + 'orig' + '_' + images.filename

    im = Image.open(img_raw)

    exif_tags = get_exif(im)

    large_image     = url_for_uploads + '/' + sub_url + '_' + random_id  +  '_' + 'l.jpg'
    thumbnail_image = url_for_uploads + '/' + sub_url + '_' + random_id  +  '_' + 't.jpg'

    if exif_tags['Orientation'] == 3:

        size = 800, 800
        im.thumbnail(size, Image.ANTIALIAS)
        im.rotate(180).save(large_image)

        size = 140, 140
        im.thumbnail(size, Image.ANTIALIAS)
        box = (20,20,80,80)
        im.rotate(180).crop(box).save(thumbnail_image)


    elif exif_tags['Orientation']  == 6:

        size = 800, 800
        im.thumbnail(size, Image.ANTIALIAS)
        im.rotate(270).save(large_image)

        size = 140, 140
        im.thumbnail(size, Image.ANTIALIAS)
        box = (20,20,80,80)
        im.rotate(270).crop(box).save(thumbnail_image)


    elif exif_tags['Orientation']  == 8:

        size = 800, 800
        im.thumbnail(size, Image.ANTIALIAS)
        im.rotate(90).save(large_image)

        size = 140, 140
        im.thumbnail(size, Image.ANTIALIAS)
        box = (20,20,80,80)
        im.rotate(90).crop(box).save(thumbnail_image)

    else:
        size = 800, 800
        im.thumbnail(size, Image.ANTIALIAS)
        im.save(large_image)

        size = 140, 140
        im.thumbnail(size, Image.ANTIALIAS)
        box = (20,20,80,80)
        im.crop(box).save(thumbnail_image)

    image = schema.Image().save()

    image.thumbnail = 'images/' + sub_url + '/' + sub_url + '_' + random_id  +  '_' + 't.jpg'
    image.image     = 'images/' + sub_url + '/' + sub_url + '_' + random_id  +  '_' + 'l.jpg'

    image.save()

    post.update(add_to_set__images = image)



