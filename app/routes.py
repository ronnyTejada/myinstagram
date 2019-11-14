from flask import render_template, flash, request,make_response, redirect, url_for, jsonify, json
from app import app, db, photos, socketio, send
from app.forms import RegistrationForm, LoginForm
from app.models import User, Post, Likes, Comments, Notifications
from flask_login import login_required,current_user, login_user,logout_user
from flask import g
from app.forms import SearchForm
from datetime import datetime
import random, time

p = 100
quantity = 1

post_quantity = 5

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str()

@app.route('/', methods=['GET', 'POST'])
def index():
    
    comments = Comments.query.filter_by().all()
    if current_user.is_anonymous == True:
        return redirect(url_for("sing_up"))
    else:
        #mostrar post de otros usuarios en la vista explore, no mostrar los del current user
        posts = current_user.followed_posts()
        global _id_ 
        _id_ = []
        for i in range(0,len(list(posts))):
            
            _id_.append('id'+ str(posts[i].id))

        return render_template('index.html', title='Inicio', posts=posts , likes=likes, comments=comments, _id_=_id_)


@app.route('/sing_up', methods=['GET','POST'])
def sing_up():
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)

		db.session.add(user)
		db.session.commit()
	return render_template('sing_up.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
       	login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sing in', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@login_required
@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.timestamp.desc()).all()
    count = len(posts)

    if request.method == 'POST' and 'photo' in request.files:
            filename = photos.save(request.files['photo'])
            url = photos.url(filename)
            #u = url[21:36]
            u = url.replace("_uploads", "static")
            post = Post(img=u, author=current_user)
            db.session.add(post)
            db.session.commit()
            return redirect('/profile/{}'.format(username))
    

    return render_template('profile.html', title=username, user=user, posts=posts, count=count)

@app.route('/addPost', methods=['GET', 'POST'])
def addPost():
    if request.method == 'POST' and 'photo' in request.files:
            filename = photos.save(request.files['photo'])
            url = photos.url(filename)
            #u = url[21:36]
            u = url.replace("_uploads", "static")
            post = Post(img=u, author=current_user)
            db.session.add(post)
            db.session.commit()
    return render_template('addPost.html')

@app.route('/explore/')
@login_required
def explore():
    #mostrar post de otros usuarios en la vista explore, no mostrar los del current user
    global posts
    posts = list()
    users = User.query.filter_by().all()
    global counter_end
    
    posts = Post.query.filter_by().all()
    return render_template('explore.html', title='Explore', posts=posts)

@app.route('/follow', methods=['POST'])
@login_required
def follow():
    username = request.form['username']
    accion = request.form['accion']
	
    if username and accion:
        user = User.query.filter_by(username=username).first()
        if accion == 'follow':
            if user is None:
                flash('User {} not found.'.format(username))
            if user == current_user:
                flash('You cannot follow yourself')
            current_user.follow(user)
            db.session.commit()
            flash('You are following {}!'.format(user.username))
            return jsonify({'status':'OK','username':username, 'accion':accion})

        else:
            if user is None:
                flash('User {} not found.'.format(username))
            if user == current_user:
                flash('You cannot follow yourself')
            current_user.unfollow(user)
            db.session.commit()
            return jsonify({'status':'OK','username':username, 'accion':accion})

    return jsonify({'error':'missing data'})


    """if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself')
        return redirect(url_for('profile', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(user.username))
    return redirect(url_for('profile', username=username, user=user))"""

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('profile', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(user.username))
    return redirect(url_for('profile', username=username, user=user))

@app.route('/likes', methods=['POST']) #funcion para likes o dislike funciona con ajax
@login_required
def likes():

    postId = request.form['postId']
    action = request.form['action']
   
    print(postId)
    if postId and action:
        post = Post.query.filter_by(id=int(postId)).first_or_404()
        if action == 'likes':
            current_user.like_post(post)
            db.session.commit()
            return jsonify({'status':'OK', 'id':postId, 'action':action})
        if action == 'dislikes':
            current_user.dislike_post(post)
            db.session.commit()
            return jsonify({'status':'OK', 'id':postId, 'action':action})


    return jsonify({'error':'error xxx'})

    """if action == 'like':
        current_user.like_post(post)
        db.session.commit()
    if action == 'dislike':
        current_user.dislike_post(post)
        db.session.commit()

    return redirect('/')"""

@app.route('/post_mdl/<id>')
def post_mdl(id):

    post = Post.query.filter_by(id=id).first_or_404()

    posts = list()
    users = User.query.filter_by().all()
    for p in range(0,len(users)):
        if users[p] != current_user:
           posts += Post.query.filter_by(author=users[p])
    
    user=current_user
    return render_template('_post_modal.html', post=post, posts=posts, id=int(id))

@app.route('/p/<id>')
def post_detail(id):

    post = Post.query.filter_by(id=id).first_or_404()
    comments = Comments.query.filter_by().all()


    user=current_user
   
                    
    return render_template('post_detail.html', post=post, user=user, comments=comments)

idPost = 0

@app.route('/addComment', methods=['POST'])
def addComment():

    body = request.form['comentario']
    user  = request.form['user']
    postId = request.form['postId']

    print(postId == int())
    if body and user and postId: #if there is comment add to bd

        new_comment = Comments(user_id=current_user.id, post_id=int(postId), body=body) #new comment to bd
        db.session.add(new_comment)
        db.session.commit()
        return jsonify({'status':'OK','comentario':body, 'user':user, 'postId':postId})
    
    return jsonify({'error':'missing data'})

@app.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('/'))
    
    page = request.args.get('page', 1, type=int)
    User.reindex()
    users, total = User.search(g.search_form.q.data, page,10)
    
    return render_template('search.html', title='Search', users=users)

@app.route('/delete_post/<id>')
@login_required
def delete_post(id):
    Comments.query.filter_by(post_id=int(id)).delete()
    Post.query.filter_by(id=int(id)).delete()
    db.session.commit()

    return redirect('/profile/{}'.format(current_user.username))

@app.route('/notificaciones')
def notificaciones():
    notifications = Notifications.query.filter_by(other_user=current_user.username).all()
    

    return render_template('notificaciones.html', notifications=notifications)

@app.route('/delete_notification/<id>')
@login_required
def delete_notification(id):
    Notifications.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect('/notificaciones')




@socketio.on('json')
def handleMessage(msg):
    e = msg
    if e['data'] == 'User has connected!':
        print(e['data'])
    else:
        notification = Notifications(user_id=current_user.id, accion=e['data'], other_user=e['other_user'])
        db.session.add(notification)
        db.session.commit()

    send(msg, broadcast=True, json=True)

















