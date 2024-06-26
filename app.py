import os
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mobility import Mobility
from flask_mobility.decorators import mobile_template
from werkzeug.utils import secure_filename

# Настройка переменных и конфигурации приложения
upload_folder = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app = Flask(__name__)
Mobility(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newflask.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD'] = upload_folder
db = SQLAlchemy(app)



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class Subcategory(db.Model):
    # Таблица с подкатегориями
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_Category = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(30), nullable=False)


class Category(db.Model):
    # Таблица с категориями
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)


class Сollection(db.Model):
    # Таблица с экземпляроми коллекции
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image = db.Column(db.String(50), nullable=True)
    id_Category = db.Column(db.Integer, nullable=False)
    id_Subcategory = db.Column(db.Integer, nullable=False)
    Year = db.Column(db.Integer, nullable=False)
    Description = db.Column(db.Text, nullable=True)


@app.route('/')
def index():
    return redirect('/collection')


@app.route('/collection', methods=['POST', 'GET'])
@mobile_template("{mobile/}collection.html")
def collection(template):
    # Главная страница с отображением коллекции
    Sub='-'
    coll = Сollection.query.all()
    Subcat = Subcategory.query.order_by(Subcategory.name).all()
    for n in coll:
        n.image = os.path.join(app.config['UPLOAD'], n.image)
    for n in coll:
        cat = Category.query.filter_by(id=n.id_Category).first()
        subcat = Subcategory.query.filter_by(id=n.id_Subcategory).first()
        n.id_Category = cat.name
        n.id_Subcategory = subcat.name
    if request.method == 'POST':
        if request.form['action'] == 'add':
            return redirect('/collection/add')
        elif request.form['action'] == 'find':
            collec = Сollection.query.filter_by(id_Subcategory=request.form['Subcategory']).all()
            return render_template(template, bl=Sub, coll=collec, Subcat=Subcat)
    else:
        return render_template(template,bl=Sub, coll=coll, Subcat=Subcat)


@app.route('/collection/add', methods=['POST', 'GET'])
@mobile_template("{mobile/}add_collection.html")
def add_collection(template):
    # Страница для добавления нового экземпляра
    Subcat = Subcategory.query.order_by(Subcategory.name).all()
    if request.method == 'POST':
        if request.form['action'] == 'add':
            try:
                file = request.files['img']
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD'], filename))
            except:
                filename = 'Base.jpg'
            cat = Subcategory.query.filter_by(id=request.form['Subcategory']).first()
            upload = Сollection(image=filename, id_Category=cat.id_Category, id_Subcategory=request.form['Subcategory'],
                                Year=request.form['Year'], Description=request.form['Description'])
            try:
                db.session.add(upload)
                db.session.commit()
                return redirect('/collection')
            except:
                redirect('/collection/add')
        return redirect('/collection/add')
    else:
        return render_template(template, Subcat=Subcat)


@app.route('/collection/<int:id>/update', methods=['POST', 'GET'])
@mobile_template("{mobile/}update_collection.html")
def update_collection(template, id):
    # Страница редактирования экземпляра коллекции
    coll = Сollection.query.filter_by(id=id).first()
    Subcat = Subcategory.query.order_by(Subcategory.name).all()
    Cat = Category.query.all()

    if request.method == 'POST':
        if request.form['action'] == 'update':
            try:
                file = request.files['img']
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD'], filename))
                coll.image=filename
            except:
                pass
            cat = Subcategory.query.filter_by(id=request.form['Subcategory']).first()
            coll.id_Category = cat.id_Category
            coll.id_Subcategory = request.form['Subcategory']
            coll.Year = request.form['Year']
            coll.Description = request.form['Description']
            try:
                db.session.commit()
                return redirect('/collection')
            except:
                return redirect('/collection/<int:id>/update')

        if request.form['action'] == 'delete':
            try:
                db.session.delete(coll)
                db.session.commit()
                return redirect('/collection')
            except:
                return redirect('/collection/<int:id>/update')
    else:
        return render_template(template, Cat=Cat, coll=coll, Subcat=Subcat)


@app.route('/category', methods=['POST', 'GET'])
@mobile_template("{mobile/}category.html")
def category(template):
    # Страница категорий
    Cat = Category.query.all()

    if request.method == 'POST':
        if request.form['action'] == 'add':
            return redirect('/category/add')
    else:
        return render_template(template, Cat=Cat)


@app.route('/category/add', methods=['POST', 'GET'])
@mobile_template("{mobile/}add_category.html")
def add_category(template):
    # Страница добавления новой категории
    if request.method == 'POST':
        if request.form['action'] == 'add':
            Cat = Category(name=request.form['cat_name'])
            try:
                db.session.add(Cat)
                db.session.commit()
                return redirect('/category')
            except:
                return redirect('/category/add')
    else:
        return render_template(template)


@app.route('/category/<int:id>/update', methods=['POST', 'GET'])
@mobile_template("{mobile/}update_category.html")
def update_category(template, id):
    # Страница редактирования категории
    Cat = Category.query.filter_by(id=id).first()

    if request.method == 'POST':
        if request.form['action'] == 'update':
            Cat.name = request.form['cat_name']
            try:
                db.session.commit()
                return redirect('/category')
            except:
                return redirect('/category/<int:id>/update')

        if request.form['action'] == 'delete':
            subcat = Subcategory.query.filter_by(id_Category=Cat.id)
            coll = Сollection.query.filter_by(id_Category=Cat.id)
            try:
                for n in coll:
                    db.session.delete(n)
                for n in subcat:
                    db.session.delete(n)
                db.session.delete(Cat)
                db.session.commit()
                return redirect('/category')
            except:
                return redirect('/category/<int:id>/update')
    else:
        return render_template(template, Cat=Cat)


@app.route('/subcategory', methods=['POST', 'GET'])
@mobile_template("{mobile/}subcategory.html")
def subcategory(template):
    # Страница подкатегорий
    Subcat = Subcategory.query.all()
    for n in Subcat:
        cat = Category.query.filter_by(id=n.id_Category).first()
        n.id_Category= cat.name

    if request.method == 'POST':
        if request.form['action'] == 'add':
            return redirect('/subcategory/add')
    else:
        return render_template(template, Subcat=Subcat)


@app.route('/subcategory/add', methods=['POST', 'GET'])
@mobile_template("{mobile/}add_subcategory.html")
def add_subcategory(template):
    # Страница добавления подкатегории
    Cat = Category.query.order_by(Category.name).all()
    if request.method == 'POST':
        if request.form['action'] == 'add':
            Subcat = Subcategory(name=request.form['sub_name'], id_Category=request.form['selCat'])
            try:
                db.session.add(Subcat)
                db.session.commit()
                return redirect('/subcategory')
            except:
                return redirect('/subcategory/add')
    else:
        return render_template(template, Cat=Cat)


@app.route('/subcategory/<int:id>/update', methods=['POST', 'GET'])
@mobile_template("{mobile/}update_subcategory.html")
def update_subcategory(template, id):
    # Страница редактирования под категории
    Cat = Category.query.all()
    Subcat = Subcategory.query.filter_by(id=id).first()
    if request.method == 'POST':
        if request.form['action'] == 'update':
            Subcat.name = request.form['sub_name']
            Subcat.id_Category = request.form['selCat']
            try:

                db.session.commit()
                return redirect('/subcategory')
            except:
                return redirect('/subcategory/<int:id>/update')

        if request.form['action'] == 'delete':
            coll = Сollection.query.filter_by(id_Category=Subcat.id)
            try:
                for n in coll:
                    db.session.delete(n)
                db.session.delete(Subcat)
                db.session.commit()
                return redirect('/subcategory')
            except:
                return redirect('/subcategory/<int:id>/update')
    else:
        return render_template(template, Cat=Cat, Subcat=Subcat)



if __name__ == '__main__':
    app.run(host='0.0.0.0')
