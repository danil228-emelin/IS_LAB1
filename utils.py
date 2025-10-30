from functools import wraps
from flask import jsonify, request
from models import User
import jwt
from config import Config

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Проверяем заголовок Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid token format'
                }), 401
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Token is missing'
            }), 401
        
        try:
            # Декодируем токен
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            current_user = User.query.get(data['identity'])
            
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'Invalid token'
                }), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'message': 'Token has expired'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'message': 'Invalid token'
            }), 401
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Token error: {str(e)}'
            }), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        # Простая проверка на админа (можно расширить)
        if current_user.username != 'admin':
            return jsonify({
                'success': False,
                'message': 'Admin access required'
            }), 403
        return f(current_user, *args, **kwargs)
    return decorated