from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import os
import uuid
import logging
from config import ProductionConfig

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация приложения
app = Flask(__name__)
app.config.from_object(ProductionConfig)

# Инициализация расширений
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app)

# Модели
def generate_uuid():
    return str(uuid.uuid4())

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
         # Хэширование пароля с помощью bcrypt
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'user_id': self.user_id,
            'author_username': self.author.username if self.author else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_published': self.is_published
        }

# Маршруты

# 1. POST /auth/login
@app.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({
                'success': False,
                'message': 'Invalid username or password'
            }), 401
        
        if not user.is_active:
            return jsonify({
                'success': False,
                'message': 'Account is deactivated'
            }), 401
        
        access_token = create_access_token(
            identity=user.id,
            additional_claims={'username': user.username}
        )
        
        logger.info(f"User {username} logged in successfully")
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'data': {
                'access_token': access_token,
                'token_type': 'bearer',
                'user': user.to_dict()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Login error: {str(e)}'
        }), 500

# 2. GET /api/data - защищенный маршрут
@app.route('/api/data', methods=['GET'])
@jwt_required()
def get_data():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Статистика
        total_users = User.query.count()
        total_posts = Post.query.count()
        user_posts = Post.query.filter_by(user_id=current_user_id).count()
        
        # Последние посты
        recent_posts = Post.query.filter_by(is_published=True)\
                               .order_by(Post.created_at.desc())\
                               .limit(5)\
                               .all()
        
        # Пользователи
        users = User.query.filter_by(is_active=True).all()
        
        data = {
            'stats': {
                'total_users': total_users,
                'total_posts': total_posts,
                'your_posts': user_posts
            },
            'recent_posts': [post.to_dict() for post in recent_posts],
            'users': [{
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at.isoformat()
            } for user in users]
        }
        
        return jsonify({
            'success': True,
            'message': 'Data retrieved successfully',
            'data': data
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving data: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error retrieving data: {str(e)}'
        }), 500

# 3. POST /api/posts - создание поста (третий метод)
@app.route('/api/posts', methods=['POST'])
@jwt_required()
def create_post():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        title = data.get('title')
        content = data.get('content')
        
        if not title or not content:
            return jsonify({
                'success': False,
                'message': 'Title and content are required'
            }), 400
        
        if len(title) > 200:
            return jsonify({
                'success': False,
                'message': 'Title too long (max 200 characters)'
            }), 400
        
        post = Post(
            title=title,
            content=content,
            user_id=current_user_id
        )
        
        db.session.add(post)
        db.session.commit()
        
        logger.info(f"Post created by user {current_user_id}: {title}")
        
        return jsonify({
            'success': True,
            'message': 'Post created successfully',
            'data': post.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating post: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error creating post: {str(e)}'
        }), 500

# JWT обработчики ошибок
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'success': False,
        'message': 'Token has expired'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'success': False,
        'message': 'Invalid token'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'success': False,
        'message': 'Token is missing'
    }), 401

# Обработчик ошибок 404
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Endpoint not found'
    }), 404

# Инициализация базы данных
def init_db():
    with app.app_context():
        db.create_all()
        
        # Создаем тестового пользователя если нет пользователей
        if User.query.count() == 0:
            admin_user = User(
                username='admin',
                email='admin@example.com'
            )
            admin_user.set_password('admin123')
            
            test_user = User(
                username='testuser',
                email='test@example.com'
            )
            test_user.set_password('test123')
            
            db.session.add(admin_user)
            db.session.add(test_user)
            db.session.commit()
            
            # Создаем тестовые посты
            post1 = Post(
                title='Добро пожаловать в наше приложение!',
                content='Это первый демонстрационный пост. Рады видеть вас здесь!',
                user_id=admin_user.id
            )
            
            post2 = Post(
                title='Второй демонстрационный пост',
                content='Этот пост создан тестовым пользователем.',
                user_id=test_user.id
            )
            
            db.session.add(post1)
            db.session.add(post2)
            db.session.commit()
            
            logger.info("=" * 50)
            logger.info("Тестовые данные созданы!")
            logger.info("Админ: username='admin', password='admin123'")
            logger.info("Тестовый пользователь: username='testuser', password='test123'")
            logger.info("=" * 50)

if __name__ == '__main__':
    init_db()
    app.run(debug=False, host='0.0.0.0', port=5000)