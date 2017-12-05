#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, json
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient


app = Flask(__name__)

app.config.update({
    'SQLALCHEMY_DATABASE_URI': 'mysql://root@localhost/shiyanlou'
    })

db = SQLAlchemy(app)
mongodb = MongoClient('localhost', 27017)['shiyanlou']


class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True)
    created_time = db.Column(db.DateTime)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    category = db.relationship('Category', uselist=False)
    content = db.Column(db.Text)
    
    def __init__(self, title, created_time, category, content):
        self.title = title
        self.created_time = created_time
        self.category = category
        self.content = content

    # def __repr__(self):
    #     return '{}'.format(self.title)

    def add_tag(self, tag_name):
        file_item = mongodb.files.find_one({'file_id': self.id})
        if file_item:
            tags = file_item['tags']
            if tag_name not in tags:
                tags.append(tag_name)
            mongodb.files.update_one({'file_id': self.id}, {'$set': {'tags': tags}})
        else:
            tags = [tag_name]
            mongodb.files.insert_one({'file_id': self.id, 'tags': tags})
        return tags
        # tags = [tag_name]
        # mongodb.files.insert({'file_id': self.id, 'tags': tags})
        # return tags

    def remove_tag(self, tag_name):
        file_item = mongodb.files.find_one({'file_id': self.id})
        if file_item:
            tags = file_item['tags']
            try:
                new_tags = tags.remove(tag_name)
            except:
                return tags
            mongodb.files.update_one({'file_id': self.id}, {'$set', {'tags': new_tags}})
            return new_tags
        return []

    @property
    def tags(self):
        file_item = mongodb.files.find_one({'file_id': self.id})
        if file_item:
            print(file_item)
            return file_item['tags']
        else:
            return []


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    files = db.relationship('File') 

    def __init__(self, name):
        self.name = name



@app.route('/')
def index():
    return render_template('index.html', files=File.query.all())


@app.route('/files/<int:file_id>')
def file(file_id):
    file_item = File.query.get_or_404(file_id)
    return render_template('file.html', file_item=file_item)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(port=3000, debug=True)
