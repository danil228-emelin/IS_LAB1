import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db

def init_database():
    app = create_app()
    
    with app.app_context():
        # Создаем все таблицы
        db.create_all()
        print("Database tables created successfully!")
        
        # Можно добавить здесь начальные данные
        from models import User, UserProfile
        
        if User.query.count() == 0:
            # Создаем начальных пользователей
            users_data = [
                {'username': 'admin', 'email': 'admin@example.com', 'password': 'admin123'},
                {'username': 'user1', 'email': 'user1@example.com', 'password': 'user123'},
                {'username': 'user2', 'email': 'user2@example.com', 'password': 'user123'},
            ]
            
            for user_data in users_data:
                user = User(
                    username=user_data['username'],
                    email=user_data['email']
                )
                user.set_password(user_data['password'])
                db.session.add(user)
                
                # Создаем профиль
                profile = UserProfile(user_id=user.id)
                db.session.add(profile)
            
            db.session.commit()
            print("Initial users created!")

if __name__ == '__main__':
    init_database()