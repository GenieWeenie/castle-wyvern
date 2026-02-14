# COMPLETE Password Reset Implementation

## Full Code

```python
```python
@auth_bp.route('/reset-password', methods=['POST'])
@rate_limit(limit=3, period=3600)
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')
    password_confirm = data.get('password_confirmation')
    
    if not token or not new_password or not password_confirm:
        return jsonify({'error': 'Missing required fields'}), 400
    
    user = User.query.filter_by(reset_token=token).first()
    if not user:
        return jsonify({'error': 'Invalid token'}), 400
    
    if user.token_expiration < datetime.utcnow():
        return jsonify({'error': 'Token expired'}), 400
    
    if len(new_password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters long'}), 400
    
    if not re.search(r'[A-Z]', new_password):
        return jsonify({'error': 'Password must contain at least one uppercase letter'}), 400
    
    if not re.search(r'[a-z]', new_password):
        return jsonify({'error': 'Password must contain at least one lowercase letter'}), 400
    
    if not re.search(r'\d', new_password):
        return jsonify({'error': 'Password must contain at least one number'}), 400
    
    if new_password != password_confirm:
        return jsonify({'error': 'Passwords do not match'}), 400
    
    hashed_password = generate_password_hash(new_password)
    user.password = hashed_password
    user.reset_token = None
    user.token_expiration = None
    db.session.commit()
    
    return jsonify({'message': 'Password reset successfully'}), 200
```
```

## Status: COMPLETE AND READY FOR DEPLOY
