from app import app, db, Post, Notification, PostReaction
from datetime import datetime
from sqlalchemy import text

def migrate_database():
    with app.app_context():
        # Check if the category column exists
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('post')]
        
        if 'category' not in columns:
            print("Adding category column to Post table...")
            # Add the category column
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE post ADD COLUMN category VARCHAR(50) DEFAULT "general"'))
                conn.commit()
            print("Category column added successfully!")
        else:
            print("Category column already exists.")
        
        # Update all existing posts to have a default category if they don't have one
        posts = Post.query.filter(Post.category == None).all()
        for post in posts:
            post.category = "general"
        
        db.session.commit()
        print(f"Updated {len(posts)} posts with default category.")
        
        # Check if the notification table exists
        tables = inspector.get_table_names()
        if 'notification' not in tables:
            print("Creating notification table...")
            db.create_all()
            print("Notification table created successfully!")
        else:
            print("Notification table already exists.")
            
            # Check if the content column exists in the notification table
            notification_columns = [col['name'] for col in inspector.get_columns('notification')]
            if 'content' not in notification_columns:
                print("Adding content column to Notification table...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE notification ADD COLUMN content VARCHAR(200)'))
                    conn.commit()
                print("Content column added successfully!")
            else:
                print("Content column already exists in Notification table.")
                
            # Check if the viewed column exists in the notification table
            if 'viewed' not in notification_columns:
                print("Adding viewed column to Notification table...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE notification ADD COLUMN viewed BOOLEAN DEFAULT FALSE'))
                    conn.commit()
                print("Viewed column added successfully!")
            else:
                print("Viewed column already exists in Notification table.")
                
            # Check if the post_id column exists in the notification table
            if 'post_id' not in notification_columns:
                print("Adding post_id column to Notification table...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE notification ADD COLUMN post_id INTEGER REFERENCES post(id)'))
                    conn.commit()
                print("Post ID column added successfully!")
            else:
                print("Post ID column already exists in Notification table.")
                
            # Check if the comment_id column exists in the notification table
            if 'comment_id' not in notification_columns:
                print("Adding comment_id column to Notification table...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE notification ADD COLUMN comment_id INTEGER REFERENCES comment(id)'))
                    conn.commit()
                print("Comment ID column added successfully!")
            else:
                print("Comment ID column already exists in Notification table.")
                
            # Check if the actor_id column exists in the notification table
            if 'actor_id' not in notification_columns:
                print("Adding actor_id column to Notification table...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE notification ADD COLUMN actor_id INTEGER REFERENCES user(id)'))
                    conn.commit()
                print("Actor ID column added successfully!")
            else:
                print("Actor ID column already exists in Notification table.")
            
        # Check if the post_reaction table exists
        if 'post_reaction' not in tables:
            print("Creating post_reaction table...")
            db.create_all()
            print("Post reaction table created successfully!")
        else:
            print("Post reaction table already exists.")

if __name__ == "__main__":
    migrate_database()
    print("Migration completed successfully!") 