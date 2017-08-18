#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# all the imports
import json
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash
from flask_sqlalchemy import SQLAlchemy
import random
from sqlalchemy import and_

# configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///./databases.db'
DEBUG = True
SECRET_KEY = 'remember'
SQLALCHEMY_TRACK_MODIFICATIONS = True

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

db = SQLAlchemy(app)


class EnglishWords(db.Model):
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    word = db.Column('word', db.String(50))
    term_frequency = db.Column('term_frequency', db.Integer)
    images = db.Column('images', db.Text)
    ext = db.Column('ext', db.Text)

    def __init__(self, word, term_frequency, images, ext):
        self.word = word
        self.term_frequency = term_frequency
        self.images = images
        self.ext = ext

    def __repr__(self):
        return '<EnglishWords %r>' % self.word

@app.route('/')
def home_page():
    redirect(url_for(show_index))

@app.route('/index', methods=['GET'])
def show_index():

    from_num = request.args.get('from_num', 1)
    to_num = request.args.get('to_num', 100)

    min_word = EnglishWords.query.filter(
        and_(EnglishWords.term_frequency >= from_num, EnglishWords.term_frequency <= to_num)).order_by(
        EnglishWords.id).first()
    max_word = EnglishWords.query.filter(
        and_(EnglishWords.term_frequency >= from_num, EnglishWords.term_frequency <= to_num)).order_by(
            EnglishWords.id.desc()).first()

    random_id = random.randint(min_word.id, max_word.id)

    word = EnglishWords.query.filter(EnglishWords.id >= random_id).first()

    ext = json.loads(word.ext)
    images = json.loads(word.images)

    # 删除未找到翻译的单词
    if not ext['translation']:
        db.session.delete(word)
        db.session.commit()

    word.images = images
    word.ext = ext

    data = {}
    data['word'] = word
    data['from_num'] = from_num
    data['to_num'] = to_num

    return render_template('show_index.html', data=data)


@app.route('/tongji')
def show_tontji():
    count = []
    categories = []

    for i in range(1, 10):
        s = i * 10 - 9
        e = i * 10

        categories.append('/'.join([str(s), str(e)]))

        item_count = EnglishWords.query.filter(
            and_(EnglishWords.term_frequency >= s, EnglishWords.term_frequency < e)).count()
        count.append(item_count)

    item_count = EnglishWords.query.filter(EnglishWords.term_frequency >= 100).count()
    count.append(item_count)
    categories.append('100/~')

    return render_template('tongji.html', count=count, categories=categories)


if __name__ == '__main__':
    # show_index()
    app.run(host='127.0.0.1')
