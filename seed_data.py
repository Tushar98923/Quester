from app import app, db, User, Post, Comment, Notification, PostReaction
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def seed_database():
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        PostReaction.query.delete()
        Comment.query.delete()
        Post.query.delete()
        Notification.query.delete()
        User.query.delete()
        db.session.commit()
        
        # Create users
        print("Creating users...")
        users = []
        usernames = [
            "techwizard", "codemaster", "sysadmin", "devopsguru", 
            "securityexpert", "datascientist", "cloudarchitect", 
            "frontenddev", "backendninja", "fullstackhero"
        ]
        
        for i, username in enumerate(usernames):
            user = User(
                username=username,
                email=f"{username}@example.com",
                password_hash=generate_password_hash("password123"),
                bio=f"Tech enthusiast with a passion for {['programming', 'system administration', 'data science', 'cloud computing', 'cybersecurity'][i % 5]}",
                profile_picture=None,
                theme="dark" if i % 2 == 0 else "light",
                avatar=f"avatar{i+1}.png",
                join_date=datetime.now() - timedelta(days=random.randint(30, 365))
            )
            users.append(user)
            db.session.add(user)
        
        db.session.commit()
        print(f"Created {len(users)} users")
        
        # Create posts
        print("Creating posts...")
        posts = []
        categories = ["Programming", "DevOps", "Cybersecurity", "Data Science", "Cloud Computing", "Web Development", "Mobile Development", "AI/ML", "Hardware", "Networking"]
        
        for i in range(50):
            author = random.choice(users)
            post = Post(
                title=f"Interesting discovery about {categories[i % len(categories)]}",
                content=f"This is a sample post about {categories[i % len(categories)]}. It contains some interesting information that would be valuable to the community. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                timestamp=datetime.now() - timedelta(days=random.randint(1, 30), hours=random.randint(0, 23)),
                user_id=author.id,
                category=categories[i % len(categories)],
                likes=random.randint(0, 100),
                dislikes=random.randint(0, 20)
            )
            posts.append(post)
            db.session.add(post)
        
        db.session.commit()
        print(f"Created {len(posts)} posts")
        
        # Create comments
        print("Creating comments...")
        comments = []
        
        for post in posts:
            # Add 2-5 comments to each post
            for _ in range(random.randint(2, 5)):
                author = random.choice(users)
                comment = Comment(
                    content=f"This is a sample comment on the post about {post.category}. It provides additional insights or questions about the topic. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
                    timestamp=post.timestamp + timedelta(hours=random.randint(1, 24)),
                    user_id=author.id,
                    post_id=post.id,
                    parent_id=None
                )
                comments.append(comment)
                db.session.add(comment)
                
                # Add 0-2 replies to some comments
                if random.random() > 0.7:
                    for _ in range(random.randint(0, 2)):
                        reply_author = random.choice(users)
                        reply = Comment(
                            content=f"This is a reply to the previous comment. It adds more context or a different perspective. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
                            timestamp=comment.timestamp + timedelta(minutes=random.randint(5, 60)),
                            user_id=reply_author.id,
                            post_id=post.id,
                            parent_id=comment.id
                        )
                        comments.append(reply)
                        db.session.add(reply)
        
        db.session.commit()
        print(f"Created {len(comments)} comments")
        
        # Create reactions
        print("Creating reactions...")
        reactions = []
        
        for post in posts:
            # Create a set of users who will react to this post
            # This ensures each user only reacts once to each post
            reacting_users = random.sample(users, min(random.randint(5, 15), len(users)))
            
            for user in reacting_users:
                reaction_type = random.choice(["like", "dislike"])
                reaction = PostReaction(
                    user_id=user.id,
                    post_id=post.id,
                    reaction_type=reaction_type
                )
                reactions.append(reaction)
                db.session.add(reaction)
        
        db.session.commit()
        print(f"Created {len(reactions)} reactions")
        
        # Create notifications
        print("Creating notifications...")
        notifications = []
        notification_types = ["like", "comment", "follow", "mention"]
        
        for user in users:
            # Create 5-15 notifications for each user
            for _ in range(random.randint(5, 15)):
                notification_type = random.choice(notification_types)
                message = ""
                if notification_type == "like":
                    message = f"{random.choice(usernames)} liked your post"
                elif notification_type == "comment":
                    message = f"{random.choice(usernames)} commented on your post"
                elif notification_type == "follow":
                    message = f"{random.choice(usernames)} started following you"
                elif notification_type == "mention":
                    message = f"{random.choice(usernames)} mentioned you in a comment"
                
                notification = Notification(
                    user_id=user.id,
                    message=message,
                    type=notification_type,
                    read=random.random() > 0.3,  # 70% chance of being read
                    timestamp=datetime.now() - timedelta(hours=random.randint(1, 72)),
                    link=f"/post/{random.choice(posts).id}" if notification_type in ["like", "comment", "mention"] else f"/profile/{random.choice(usernames)}"
                )
                notifications.append(notification)
                db.session.add(notification)
        
        db.session.commit()
        print(f"Created {len(notifications)} notifications")
        
        print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database() 