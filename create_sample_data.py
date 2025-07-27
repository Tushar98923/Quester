from app import app, db, User, Post, Comment
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def create_sample_data():
    with app.app_context():
        # Create sample users
        users = []
        for i in range(5):
            user = User(
                username=f'user{i+1}',
                email=f'user{i+1}@example.com',
                password_hash=generate_password_hash(f'password{i+1}'),
                join_date=datetime.utcnow() - timedelta(days=random.randint(0, 365))
            )
            users.append(user)
            db.session.add(user)
        
        # Create sample posts
        posts = []
        topics = ['Technology', 'Science', 'Gaming', 'Movies', 'Books', 'Music', 'Sports']
        for i in range(15):
            topic = random.choice(topics)
            post = Post(
                title=f'{topic} Discussion #{i+1}',
                content=f'This is a sample post about {topic.lower()}. Here we can discuss various aspects of {topic.lower()} '
                       f'and share our thoughts and experiences. What do you think about recent developments in this field?',
                timestamp=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                author=random.choice(users),
                likes=random.randint(0, 50),
                dislikes=random.randint(0, 20)
            )
            posts.append(post)
            db.session.add(post)
        
        # Create sample comments
        comment_texts = [
            "Great post! Thanks for sharing.",
            "I completely agree with your points.",
            "This is very interesting, never thought about it this way.",
            "Could you elaborate more on this?",
            "I have a different perspective on this.",
            "Thanks for bringing this up for discussion.",
            "This reminds me of something similar I experienced.",
            "Very informative post!",
            "I learned something new today.",
            "Looking forward to more posts like this."
        ]
        
        for post in posts:
            # Add 2-5 comments per post
            for _ in range(random.randint(2, 5)):
                comment = Comment(
                    content=random.choice(comment_texts),
                    timestamp=post.timestamp + timedelta(hours=random.randint(1, 72)),
                    author=random.choice(users),
                    post=post,
                    likes=random.randint(0, 20),
                    dislikes=random.randint(0, 10),
                    ticks=random.randint(0, 5)
                )
                db.session.add(comment)
                
                # Add 0-2 replies per comment
                for _ in range(random.randint(0, 2)):
                    reply = Comment(
                        content=f"Reply: {random.choice(comment_texts)}",
                        timestamp=comment.timestamp + timedelta(hours=random.randint(1, 24)),
                        author=random.choice(users),
                        post=post,
                        parent=comment,
                        likes=random.randint(0, 10),
                        dislikes=random.randint(0, 5),
                        ticks=random.randint(0, 3)
                    )
                    db.session.add(reply)
        
        # Commit all changes
        db.session.commit()
        print("Sample data created successfully!")

if __name__ == '__main__':
    # First, delete all existing data
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database tables recreated!")
    
    # Create sample data
    create_sample_data() 