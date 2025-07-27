from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from sqlalchemy.sql import func
import json
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forum.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/avatars'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['BASE_URL'] = 'http://localhost:5000'  # Change this in production

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    bio = db.Column(db.Text)
    profile_picture = db.Column(db.String(120))
    theme = db.Column(db.String(20), default='dark')
    avatar = db.Column(db.String(200), default="default_avatar.png")
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    
    # New customization fields
    accent_color = db.Column(db.String(7), default='#007AFF')  # Default blue
    font_size = db.Column(db.String(20), default='medium')  # small, medium, large
    notification_preferences = db.Column(db.JSON, default={
        'email_notifications': True,
        'like_notifications': True,
        'comment_notifications': True,
        'mention_notifications': True,
        'follow_notifications': True
    })
    language = db.Column(db.String(10), default='en')  # Language preference
    timezone = db.Column(db.String(50), default='UTC')  # User's timezone
    privacy_settings = db.Column(db.JSON, default={
        'show_email': False,
        'show_join_date': True,
        'show_activity': True
    })
    display_name = db.Column(db.String(80))  # Optional display name different from username
    social_links = db.Column(db.JSON, default={
        'website': '',
        'twitter': '',
        'github': '',
        'linkedin': ''
    })

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Post model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    edited = db.Column(db.Boolean, default=False)
    edited_timestamp = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50), default='general')
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")
    reactions = db.relationship('PostReaction', backref='post', lazy=True, cascade="all, delete-orphan")
    tags = db.Column(db.String(255))
    
    @property
    def comments_count(self):
        return len(self.comments)

# Comment model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    edited = db.Column(db.Boolean, default=False)
    edited_timestamp = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)
    ticks = db.Column(db.Integer, default=0)
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy=True)

# Notification model
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'like', 'comment', 'follow', 'mention'
    content = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)
    viewed = db.Column(db.Boolean, default=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    actor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('notifications', lazy='dynamic'))
    post = db.relationship('Post', backref=db.backref('notifications', lazy='dynamic'))
    comment = db.relationship('Comment', backref=db.backref('notifications', lazy='dynamic'))
    actor = db.relationship('User', foreign_keys=[actor_id], backref=db.backref('actions', lazy='dynamic'))

# PostReaction model to track user reactions
class PostReaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    reaction_type = db.Column(db.String(10), nullable=False)  # 'like' or 'dislike'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_reaction'),)

# Snippet model
class Snippet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(16), unique=True, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    post = db.relationship('Post', backref='snippets')
    comment = db.relationship('Comment', backref='snippets')

class UserBehavior(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    action_type = db.Column(db.String(20), nullable=False)  # 'view', 'like', 'comment', 'share'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    weight = db.Column(db.Float, default=1.0)  # Weight of the action

    # Relationships
    user = db.relationship('User', backref='behaviors')
    post = db.relationship('Post', backref='behaviors')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort_by', 'newest')
    category = request.args.get('category')
    search_query = request.args.get('search')
    tag = request.args.get('tag')
    
    # Base query
    query = Post.query
    
    # Apply category filter if specified
    if category:
        query = query.filter(Post.category == category)
    
    # Apply tag filter if specified
    if tag:
        query = query.filter(Post.tags.ilike(f'%{tag}%'))
    
    # Apply search filter if specified
    if search_query:
        search = f"%{search_query}%"
        query = query.filter(
            db.or_(
                Post.title.ilike(search),
                Post.content.ilike(search),
                Post.tags.ilike(search)
            )
        )
    
    # Apply sorting
    if sort_by == 'newest':
        query = query.order_by(Post.timestamp.desc())
    elif sort_by == 'oldest':
        query = query.order_by(Post.timestamp.asc())
    elif sort_by == 'most_liked':
        query = query.order_by(Post.likes.desc())
    elif sort_by == 'most_comments':
        # Use a subquery to count comments for each post
        comment_counts = db.session.query(
            Comment.post_id,
            db.func.count(Comment.id).label('comment_count')
        ).group_by(Comment.post_id).subquery()
        
        # Join with the main query and order by comment count
        query = query.outerjoin(
            comment_counts,
            Post.id == comment_counts.c.post_id
        ).order_by(
            db.func.coalesce(comment_counts.c.comment_count, 0).desc()
        )
    
    # Get paginated results
    posts = query.paginate(page=page, per_page=10, error_out=False)
    
    # Get categories for filter dropdown
    categories = db.session.query(Post.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]  # Remove None values
    
    # Get popular tags
    popular_tags = []
    tag_counts = {}
    all_posts = Post.query.all()
    for post in all_posts:
        if post.tags:
            tags = post.tags.split(',')
            for tag in tags:
                tag = tag.strip()
                if tag:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    # Sort tags by count and get top 10
    popular_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return render_template('home.html', 
                         posts=posts,
                         categories=categories,
                         current_sort=sort_by,
                         current_category=category,
                         search_query=search_query,
                         tag=tag,
                         popular_tags=popular_tags)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validate username
        if not username or len(username) < 3:
            flash('Username must be at least 3 characters long')
            return redirect(url_for('register'))
        
        # Check for duplicate username (case-insensitive)
        existing_user = User.query.filter(db.func.lower(User.username) == db.func.lower(username)).first()
        if existing_user:
            flash('Username already exists. Please choose a different username.')
            return redirect(url_for('register'))
        
        # Check for duplicate email
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use a different email or try logging in.')
            return redirect(url_for('register'))
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! You can now log in.')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.')
            app.logger.error(f"Registration error: {str(e)}")
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        category = request.form.get('category', 'general')
        tags = request.form.getlist('tags')  # Get all tags
        
        if not title or not content:
            return jsonify({'error': 'Title and content are required'}), 400
        
        # Create the post
        post = Post(
            title=title,
            content=content,
            category=category,
            author=current_user,
            tags=','.join(tags) if tags else ''  # Store tags as comma-separated string
        )
        
        db.session.add(post)
        db.session.commit()
        
        return jsonify({
            'message': 'Post created successfully',
            'post_id': post.id
        })
    
    # GET request - render the new post page
    return render_template('new_post.html')

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    user_reaction = None
    if current_user.is_authenticated:
        reaction = PostReaction.query.filter_by(
            user_id=current_user.id,
            post_id=post_id
        ).first()
        if reaction:
            user_reaction = reaction.reaction_type
    return render_template('post.html', post=post, user_reaction=user_reaction)

@app.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form.get('content')
    
    if not content:
        flash('Comment cannot be empty')
        return redirect(url_for('post', post_id=post_id))
    
    comment = Comment(content=content, post=post, author=current_user)
    db.session.add(comment)
    db.session.commit()
    
    flash('Comment added successfully')
    return redirect(url_for('post', post_id=post_id))

@app.route('/comment/<int:comment_id>/reply', methods=['POST'])
@login_required
def reply_to_comment(comment_id):
    parent_comment = Comment.query.get_or_404(comment_id)
    content = request.form.get('content')
    
    if not content:
        flash('Reply cannot be empty')
        return redirect(url_for('post', post_id=parent_comment.post_id))
    
    reply = Comment(content=content, post=parent_comment.post, author=current_user, parent=parent_comment)
    db.session.add(reply)
    db.session.commit()
    
    flash('Reply added successfully')
    return redirect(url_for('post', post_id=parent_comment.post_id))

@app.route('/api/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # Check if user has already reacted to the post
    existing_reaction = PostReaction.query.filter_by(
        user_id=current_user.id,
        post_id=post_id
    ).first()
    
    if existing_reaction:
        if existing_reaction.reaction_type == 'like':
            # User already liked the post, remove the like
            post.likes -= 1
            db.session.delete(existing_reaction)
        else:
            # User previously disliked, change to like
            post.dislikes -= 1
            post.likes += 1
            existing_reaction.reaction_type = 'like'
    else:
        # New like
        post.likes += 1
        new_reaction = PostReaction(
            user_id=current_user.id,
            post_id=post_id,
            reaction_type='like'
        )
        db.session.add(new_reaction)
    
    db.session.commit()
    return jsonify({
        'likes': post.likes,
        'dislikes': post.dislikes,
        'user_reaction': 'like' if existing_reaction and existing_reaction.reaction_type == 'like' else None
    })

@app.route('/api/post/<int:post_id>/dislike', methods=['POST'])
@login_required
def dislike_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # Check if user has already reacted to the post
    existing_reaction = PostReaction.query.filter_by(
        user_id=current_user.id,
        post_id=post_id
    ).first()
    
    if existing_reaction:
        if existing_reaction.reaction_type == 'dislike':
            # User already disliked the post, remove the dislike
            post.dislikes -= 1
            db.session.delete(existing_reaction)
        else:
            # User previously liked, change to dislike
            post.likes -= 1
            post.dislikes += 1
            existing_reaction.reaction_type = 'dislike'
    else:
        # New dislike
        post.dislikes += 1
        new_reaction = PostReaction(
            user_id=current_user.id,
            post_id=post_id,
            reaction_type='dislike'
        )
        db.session.add(new_reaction)
    
    db.session.commit()
    return jsonify({
        'likes': post.likes,
        'dislikes': post.dislikes,
        'user_reaction': 'dislike' if existing_reaction and existing_reaction.reaction_type == 'dislike' else None
    })

@app.route('/api/comment/<int:comment_id>/like', methods=['POST'])
@login_required
def like_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.likes += 1
    db.session.commit()
    return jsonify({
        'likes': comment.likes,
        'dislikes': comment.dislikes,
        'ticks': comment.ticks
    })

@app.route('/api/comment/<int:comment_id>/dislike', methods=['POST'])
@login_required
def dislike_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.dislikes += 1
    db.session.commit()
    return jsonify({
        'likes': comment.likes,
        'dislikes': comment.dislikes,
        'ticks': comment.ticks
    })

@app.route('/api/comment/<int:comment_id>/tick', methods=['POST'])
@login_required
def tick_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.ticks += 1
    db.session.commit()
    return jsonify({
        'likes': comment.likes,
        'dislikes': comment.dislikes,
        'ticks': comment.ticks
    })

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        # If the query is empty, redirect back to the previous page
        # If no referrer exists, redirect to home
        return redirect(request.referrer or url_for('home'))
    
    # Search for posts
    posts = Post.query.filter(
        Post.title.ilike(f'%{query}%') | 
        Post.content.ilike(f'%{query}%')
    ).order_by(Post.timestamp.desc()).all()
    
    # Search for users
    users = User.query.filter(
        User.username.ilike(f'%{query}%')
    ).order_by(User.username.asc()).all()
    
    return render_template('search.html', posts=posts, users=users, query=query)

@app.route('/search/suggestions')
def search_suggestions():
    query = request.args.get('q', '')
    if not query or len(query) < 2:
        return jsonify({'posts': [], 'users': []})
    
    # Limit results for performance
    limit = 5
    
    # Search for posts with title matching the query
    posts = Post.query.filter(
        Post.title.ilike(f'%{query}%')
    ).order_by(Post.timestamp.desc()).limit(limit).all()
    
    # Search for users with username matching the query
    users = User.query.filter(
        User.username.ilike(f'%{query}%')
    ).order_by(User.username.asc()).limit(limit).all()
    
    # Format results for JSON response
    post_results = [{
        'id': post.id,
        'title': post.title,
        'author': post.author.username,
        'url': url_for('post', post_id=post.id)
    } for post in posts]
    
    user_results = [{
        'id': user.id,
        'username': user.username,
        'url': url_for('user_profile', username=user.username)
    } for user in users]
    
    return jsonify({
        'posts': post_results,
        'users': user_results
    })

@app.route('/explore')
def explore():
    recommended_posts = get_recommended_posts(current_user.id if current_user.is_authenticated else None)
    trending_posts = Post.query.order_by(Post.likes.desc()).limit(5).all()
    popular_categories = db.session.query(
        Post.category,
        db.func.count(Post.id).label('count')
    ).group_by(Post.category).order_by(db.desc('count')).limit(5).all()
    
    return render_template('explore.html',
                         recommended_posts=recommended_posts,
                         trending_posts=trending_posts,
                         popular_categories=popular_categories)

@app.route('/user/<username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()).all()
    comments = Comment.query.filter_by(user_id=user.id).order_by(Comment.timestamp.desc()).all()
    return render_template('user_profile.html', user=user, posts=posts, comments=comments)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Handle avatar upload
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to filename to avoid duplicates
                filename = f"{current_user.id}_{int(datetime.utcnow().timestamp())}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                current_user.avatar = filename
                db.session.commit()
                flash('Profile picture updated successfully')
                return redirect(url_for('profile'))
            else:
                flash('Invalid file type. Allowed types: png, jpg, jpeg, gif')
        
        return redirect(url_for('profile'))
    
    # Get sort parameters
    post_sort = request.args.get('post_sort', 'newest')
    comment_sort = request.args.get('comment_sort', 'newest')
    
    # Get user's posts with sorting
    if post_sort == 'oldest':
        posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.timestamp.asc()).all()
    elif post_sort == 'most_liked':
        posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.likes.desc()).all()
    elif post_sort == 'most_comments':
        posts = Post.query.filter_by(user_id=current_user.id).order_by(func.count(Comment.id).desc()).all()
    else:  # newest (default)
        posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.timestamp.desc()).all()
    
    # Get user's comments with sorting
    if comment_sort == 'oldest':
        comments = Comment.query.filter_by(user_id=current_user.id).order_by(Comment.timestamp.asc()).all()
    elif comment_sort == 'most_liked':
        comments = Comment.query.filter_by(user_id=current_user.id).order_by(Comment.likes.desc()).all()
    else:  # newest (default)
        comments = Comment.query.filter_by(user_id=current_user.id).order_by(Comment.timestamp.desc()).all()
    
    return render_template('profile.html', 
                          posts=posts, 
                          comments=comments, 
                          post_sort=post_sort, 
                          comment_sort=comment_sort)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        try:
            # Handle theme settings
            theme = request.form.get('theme', 'dark')
            current_user.theme = theme
            
            # Handle accent color
            accent_color = request.form.get('accent_color', '#007AFF')
            current_user.accent_color = accent_color
            
            # Handle font size
            font_size = request.form.get('font_size', 'medium')
            current_user.font_size = font_size
            
            # Handle notification preferences
            notification_preferences = {
                'email_notifications': 'email_notifications' in request.form,
                'like_notifications': 'like_notifications' in request.form,
                'comment_notifications': 'comment_notifications' in request.form,
                'mention_notifications': 'mention_notifications' in request.form,
                'follow_notifications': 'follow_notifications' in request.form
            }
            current_user.notification_preferences = notification_preferences
            
            # Handle language and timezone
            current_user.language = request.form.get('language', 'en')
            current_user.timezone = request.form.get('timezone', 'UTC')
            
            # Handle privacy settings
            privacy_settings = {
                'show_email': 'show_email' in request.form,
                'show_join_date': 'show_join_date' in request.form,
                'show_activity': 'show_activity' in request.form
            }
            current_user.privacy_settings = privacy_settings
            
            # Handle display name
            display_name = request.form.get('display_name', '').strip()
            if display_name:
                current_user.display_name = display_name
            else:
                current_user.display_name = None
                
            # Handle social links
            social_links = {
                'website': request.form.get('website', '').strip(),
                'twitter': request.form.get('twitter', '').strip(),
                'github': request.form.get('github', '').strip(),
                'linkedin': request.form.get('linkedin', '').strip()
            }
            current_user.social_links = social_links
            
            # Handle profile picture upload
            if 'profile_picture' in request.files:
                file = request.files['profile_picture']
                if file and file.filename != '':
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(filepath)
                        current_user.profile_picture = filename
            
            # Handle bio update
            bio = request.form.get('bio', '').strip()
            if bio:
                current_user.bio = bio
                
            db.session.commit()
            flash('Settings updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating settings: {str(e)}', 'danger')
            
        return redirect(url_for('settings'))
    
    # For GET requests, ensure JSON fields are dictionaries
    if current_user.notification_preferences and isinstance(current_user.notification_preferences, str):
        current_user.notification_preferences = json.loads(current_user.notification_preferences)
    if current_user.privacy_settings and isinstance(current_user.privacy_settings, str):
        current_user.privacy_settings = json.loads(current_user.privacy_settings)
    if current_user.social_links and isinstance(current_user.social_links, str):
        current_user.social_links = json.loads(current_user.social_links)
        
    return render_template('settings.html', user=current_user)

@app.route('/notifications')
@login_required
def notifications():
    page = request.args.get('page', 1, type=int)
    filter_type = request.args.get('filter_type', 'all')
    
    # Base query for notifications
    query = Notification.query.filter_by(user_id=current_user.id)
    
    # Apply filters
    if filter_type == 'unread':
        query = query.filter_by(read=False)
    elif filter_type == 'unviewed':
        query = query.filter_by(viewed=False)
    elif filter_type == 'mentions':
        query = query.filter(Notification.type == 'mention')
    
    # Order by timestamp descending
    query = query.order_by(Notification.timestamp.desc())
    
    # Paginate results
    notifications = query.paginate(page=page, per_page=20, error_out=False)
    
    return render_template('notifications.html', 
                         notifications=notifications,
                         filter_type=filter_type)

@app.route('/api/notifications/<int:notification_id>/view', methods=['POST'])
@login_required
def mark_notification_viewed(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    
    # Ensure the current user is the recipient
    if notification.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Mark as viewed
    notification.viewed = True
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    
    # Ensure the current user is the recipient
    if notification.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Mark as read
    notification.read = True
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    # Mark all unread notifications as read
    Notification.query.filter_by(
        user_id=current_user.id,
        read=False
    ).update({'read': True})
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/create_post', methods=['POST'])
@login_required
def create_post():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    category = data.get('category')
    tags = data.get('tags', [])
    
    if not title or not content or not category:
        return jsonify({'success': False, 'message': 'Title, content and category are required'})
    
    # Create the post with the provided data
    post = Post(
        title=title,
        content=content, 
        category=category, 
        author=current_user,
        tags=','.join(tags) if tags else ''
    )
    db.session.add(post)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Post created successfully'})

@app.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # Check if the current user is the author of the post
    if post.user_id != current_user.id:
        flash('You do not have permission to delete this post.')
        return redirect(url_for('profile'))
    
    # Delete the post
    db.session.delete(post)
    db.session.commit()
    
    flash('Post deleted successfully.')
    return redirect(url_for('profile'))

@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    # Check if the current user is the author of the comment
    if comment.user_id != current_user.id:
        flash('You do not have permission to delete this comment.')
        return redirect(url_for('profile'))
    
    # Store the post_id for redirection
    post_id = comment.post_id
    
    # Delete the comment
    db.session.delete(comment)
    db.session.commit()
    
    flash('Comment deleted successfully.')
    
    # If we're on the profile page, redirect back there
    if request.referrer and 'profile' in request.referrer:
        return redirect(url_for('profile'))
    
    # Otherwise, redirect to the post page
    return redirect(url_for('post', post_id=post_id))

@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # Check if the current user is the author of the post
    if post.user_id != current_user.id:
        flash('You do not have permission to edit this post.', 'danger')
        return redirect(url_for('post', post_id=post_id))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        category = request.form.get('category')
        tags = request.form.get('tags')
        
        if not title or not content:
            flash('Title and content are required.', 'danger')
            return redirect(url_for('edit_post', post_id=post_id))
        
        post.title = title
        post.content = content
        post.category = category
        post.tags = tags
        post.edited = True
        post.edited_timestamp = datetime.utcnow()
        
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('post', post_id=post_id))
    
    return render_template('edit_post.html', post=post)

@app.route('/edit_comment/<int:comment_id>', methods=['GET', 'POST'])
@login_required
def edit_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    # Check if the current user is the author of the comment
    if comment.user_id != current_user.id:
        flash('You do not have permission to edit this comment.', 'danger')
        return redirect(url_for('post', post_id=comment.post_id))
    
    if request.method == 'POST':
        content = request.form.get('content')
        
        if not content:
            flash('Comment content is required.', 'danger')
            return redirect(url_for('edit_comment', comment_id=comment_id))
        
        comment.content = content
        comment.edited = True
        comment.edited_timestamp = datetime.utcnow()
        
        db.session.commit()
        flash('Comment updated successfully!', 'success')
        return redirect(url_for('post', post_id=comment.post_id))
    
    return render_template('edit_comment.html', comment=comment)

@app.route('/api/notifications/<int:notification_id>/delete', methods=['POST'])
@login_required
def delete_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    
    # Ensure the current user is the recipient
    if notification.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Delete the notification
    db.session.delete(notification)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/s/<token>')
def view_snippet(token):
    """View a shared snippet"""
    # Get snippet data from database
    snippet = Snippet.query.filter_by(token=token).first_or_404()
    
    # Get the post and optional comment
    post = Post.query.get_or_404(snippet.post_id)
    comment = Comment.query.get(snippet.comment_id) if snippet.comment_id else None
    
    # Generate the original URL
    if comment:
        original_url = url_for('post', post_id=post.id, _anchor=f'comment-{comment.id}', _external=True)
    else:
        original_url = url_for('post', post_id=post.id, _external=True)
    
    return render_template('snippet.html', post=post, comment=comment, original_url=original_url)

@app.route('/api/share', methods=['POST'])
def create_share():
    """Create a shareable snippet"""
    data = request.get_json()
    post_id = data.get('post_id')
    comment_id = data.get('comment_id')
    
    # Validate the post exists
    post = Post.query.get_or_404(post_id)
    comment = Comment.query.get(comment_id) if comment_id else None
    
    # Generate a unique token
    token = secrets.token_urlsafe(8)
    
    # Create snippet
    snippet = Snippet(
        token=token,
        post_id=post_id,
        comment_id=comment_id
    )
    db.session.add(snippet)
    db.session.commit()
    
    # Generate share URL
    share_url = url_for('view_snippet', token=token, _external=True)
    
    return jsonify({
        'url': share_url,
        'token': token
    })

def track_user_behavior(user_id, post_id, action_type):
    """Track user behavior and update weights"""
    # Different weights for different actions
    weights = {
        'view': 1.0,
        'like': 2.0,
        'comment': 3.0,
        'share': 4.0
    }
    
    behavior = UserBehavior(
        user_id=user_id,
        post_id=post_id,
        action_type=action_type,
        weight=weights.get(action_type, 1.0)
    )
    db.session.add(behavior)
    db.session.commit()

def get_user_interests(user_id, days=30):
    """Get user interests based on recent behavior"""
    # Get recent behaviors
    recent_behaviors = UserBehavior.query.filter(
        UserBehavior.user_id == user_id,
        UserBehavior.timestamp >= datetime.utcnow() - timedelta(days=days)
    ).all()
    
    # Calculate category weights
    category_weights = {}
    for behavior in recent_behaviors:
        post = behavior.post
        if post.category not in category_weights:
            category_weights[post.category] = 0
        category_weights[post.category] += behavior.weight
    
    return category_weights

def get_recommended_posts(user_id, limit=5):
    """Get recommended posts based on user interests"""
    if not user_id:
        # For non-logged in users, return trending posts
        return Post.query.order_by(Post.likes.desc()).limit(limit).all()
    
    # Get user interests
    interests = get_user_interests(user_id)
    
    if not interests:
        # If no interests, return trending posts
        return Post.query.order_by(Post.likes.desc()).limit(limit).all()
    
    # Get posts from interested categories
    recommended_posts = []
    for category, weight in sorted(interests.items(), key=lambda x: x[1], reverse=True):
        category_posts = Post.query.filter_by(category=category).order_by(Post.likes.desc()).limit(limit).all()
        recommended_posts.extend(category_posts)
    
    # Remove duplicates and limit results
    seen = set()
    unique_posts = []
    for post in recommended_posts:
        if post.id not in seen:
            seen.add(post.id)
            unique_posts.append(post)
            if len(unique_posts) >= limit:
                break
    
    return unique_posts

# Create database tables
def init_db():
    with app.app_context():
        # Create all tables if they don't exist
        db.create_all()
        print("Database tables checked/created successfully!")

if __name__ == '__main__':
    # Initialize the database
    init_db()
    app.run(debug=True) 