from functools import wraps
from flask import request, jsonify, current_app
import jwt
from models import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid authorization header'}), 401
        
        if not token:
            return jsonify({'error': 'Authentication token is required'}), 401
        
        try:
            # Decode token
            data = jwt.decode(
                token, 
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            current_user = User.query.get(data['user_id'])
            
            if not current_user or not current_user.is_active:
                return jsonify({'error': 'Invalid or expired token'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'error': 'Token verification failed'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

def optional_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        current_user = None
        token = None
        
        # Try to get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
                data = jwt.decode(
                    token, 
                    current_app.config['SECRET_KEY'],
                    algorithms=['HS256']
                )
                current_user = User.query.get(data['user_id'])
            except:
                # Token is invalid, but we continue as guest
                current_user = None
        
        return f(current_user, *args, **kwargs)
    
    return decorated