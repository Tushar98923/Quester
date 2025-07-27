from app import app, db, User, Post, Comment, Notification, PostReaction
from datetime import datetime, timedelta
import json

def add_sample_data():
    with app.app_context():
        # Create sample users
        users = [
            User(
                username='johndoe',
                email='john@example.com',
                bio='Tech enthusiast and developer',
                display_name='John Doe',
                social_links=json.dumps({
                    'website': 'https://johndoe.dev',
                    'twitter': '@johndoe',
                    'github': 'johndoe'
                })
            ),
            User(
                username='janedoe',
                email='jane@example.com',
                bio='Designer and artist',
                display_name='Jane Doe',
                social_links=json.dumps({
                    'website': 'https://janedoe.design',
                    'twitter': '@janedoe',
                    'instagram': '@janedoe'
                })
            ),
            User(
                username='bobsmith',
                email='bob@example.com',
                bio='Gaming enthusiast',
                display_name='Bob Smith',
                social_links=json.dumps({
                    'twitter': '@bobsmith',
                    'twitch': 'bobsmith'
                })
            )
        ]

        # Set passwords for users
        for user in users:
            user.set_password('password123')

        # Add users to database
        for user in users:
            db.session.add(user)
        db.session.commit()

        # Create sample posts
        posts = [
            Post(
                title='Getting Started with Flask',
                content='Flask is a lightweight WSGI web application framework. It is designed to make getting started quick and easy, with the ability to scale up to complex applications.',
                user_id=users[0].id,
                category='tech',
                tags='python,flask,web-development',
                timestamp=datetime.utcnow() - timedelta(days=2),
                likes=15,
                dislikes=2
            ),
            Post(
                title='Best Practices for UI Design',
                content='Creating a great user interface requires attention to detail and understanding of user behavior. Here are some key principles to follow...',
                user_id=users[1].id,
                category='design',
                tags='ui,design,ux',
                timestamp=datetime.utcnow() - timedelta(days=1),
                likes=12,
                dislikes=1
            ),
            Post(
                title='Favorite Video Games of 2023',
                content='Here are my top picks for the best video games released this year. What are your favorites?',
                user_id=users[2].id,
                category='gaming',
                tags='gaming,2023,reviews',
                timestamp=datetime.utcnow() - timedelta(hours=5),
                likes=8,
                dislikes=0
            )
        ]

        # Add posts to database
        for post in posts:
            db.session.add(post)
        db.session.commit()

        # Create sample comments
        comments = [
            Comment(
                content='Great tutorial! I learned a lot about Flask.',
                user_id=users[1].id,
                post_id=posts[0].id,
                timestamp=datetime.utcnow() - timedelta(days=1, hours=5),
                likes=5,
                ticks=2
            ),
            Comment(
                content='I agree with your design principles. Especially the part about consistency.',
                user_id=users[0].id,
                post_id=posts[1].id,
                timestamp=datetime.utcnow() - timedelta(hours=12),
                likes=3,
                ticks=1
            ),
            Comment(
                content='Have you tried the new Zelda game? It\'s amazing!',
                user_id=users[1].id,
                post_id=posts[2].id,
                timestamp=datetime.utcnow() - timedelta(hours=2),
                likes=4,
                ticks=0
            )
        ]

        # Add comments to database
        for comment in comments:
            db.session.add(comment)
        db.session.commit()

        # Create sample post reactions
        reactions = [
            PostReaction(user_id=users[1].id, post_id=posts[0].id, reaction_type='like'),
            PostReaction(user_id=users[2].id, post_id=posts[0].id, reaction_type='like'),
            PostReaction(user_id=users[0].id, post_id=posts[1].id, reaction_type='like'),
            PostReaction(user_id=users[2].id, post_id=posts[1].id, reaction_type='like'),
            PostReaction(user_id=users[0].id, post_id=posts[2].id, reaction_type='like'),
            PostReaction(user_id=users[1].id, post_id=posts[2].id, reaction_type='like')
        ]

        # Add reactions to database
        for reaction in reactions:
            db.session.add(reaction)
        db.session.commit()

        # Create sample notifications
        notifications = [
            Notification(
                user_id=users[0].id,
                type='like',
                content='johndoe liked your post "Getting Started with Flask"',
                post_id=posts[0].id,
                actor_id=users[1].id
            ),
            Notification(
                user_id=users[1].id,
                type='comment',
                content='bobsmith commented on your post "Best Practices for UI Design"',
                post_id=posts[1].id,
                actor_id=users[2].id
            ),
            Notification(
                user_id=users[2].id,
                type='like',
                content='janedoe liked your post "Favorite Video Games of 2023"',
                post_id=posts[2].id,
                actor_id=users[1].id
            )
        ]

        # Add notifications to database
        for notification in notifications:
            db.session.add(notification)
        db.session.commit()

        print("Sample data added successfully!")

if __name__ == '__main__':
    add_sample_data() 