from flask import jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User
from datetime import datetime
import re

def init_auth_routes(app):
    
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
            
            # Ищем пользователя
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
            
            # Создаем JWT токен
            access_token = create_access_token(
                identity=user.id,
                additional_claims={'username': user.username}
            )
            
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
            return jsonify({
                'success': False,
                'message': f'Login error: {str(e)}'
            }), 500
    
    @app.route('/auth/register', methods=['POST'])
    def register():
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No JSON data provided'
                }), 400
            
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            
            # Валидация
            if not all([username, email, password]):
                return jsonify({
                    'success': False,
                    'message': 'Username, email and password are required'
                }), 400
            
            if len(password) < 6:
                return jsonify({
                    'success': False,
                    'message': 'Password must be at least 6 characters long'
                }), 400
            
            if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                return jsonify({
                    'success': False,
                    'message': 'Invalid email format'
                }), 400
            
            # Проверяем существование пользователя
            if User.query.filter_by(username=username).first():
                return jsonify({
                    'success': False,
                    'message': 'Username already exists'
                }), 409
            
            if User.query.filter_by(email=email).first():
                return jsonify({
                    'success': False,
                    'message': 'Email already exists'
                }), 409
            
            # Создаем пользователя
            user = User(username=username, email=email)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            # Создаем профиль
            from models import UserProfile
            profile = UserProfile(user_id=user.id)
            db.session.add(profile)
            db.session.commit()
            
            # Создаем токен
            access_token = create_access_token(
                identity=user.id,
                additional_claims={'username': user.username}
            )
            
            return jsonify({
                'success': True,
                'message': 'User registered successfully',
                'data': {
                    'access_token': access_token,
                    'token_type': 'bearer',
                    'user': user.to_dict()
                }
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': f'Registration error: {str(e)}'
            }), 500
    
    @app.route('/auth/me', methods=['GET'])
    @jwt_required()
    def get_current_user():
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'User not found'
                }), 404
            
            response_data = user.to_dict()
            
            # Добавляем данные профиля
            if user.profiles:
                response_data['profile'] = user.profiles.to_dict()
            
            return jsonify({
                'success': True,
                'message': 'User data retrieved successfully',
                'data': response_data
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error retrieving user data: {str(e)}'
            }), 500