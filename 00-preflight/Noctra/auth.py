rd required'}), 400
        
    existing_user = User.query.filter_by(codename=codename).first()
    if existing_user:
        return jsonify({'error': 'Codename already taken'}), 400
        
    new_user = User(
        codename=codename,
        password_hash=generate_password_hash(password),
        clearance_level='alpha'
    )
    db_session.add(new_user)
    db_session.commit()
    
    return jsonify({
        'success': True,
        'codename': new_user.codename,
        'clearance_level': new_user.clearance_level
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    codename = data.get('codename')
    password = data.get('password')
    
    user = User.query.filter_by(codename=codename).first()
    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        return jsonify({
            'success': True,
            'codename': user.codename,
            'clearance_level': user.clearance_level
        }), 200
        
    return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'success': True}), 200

@auth_bp.route('/status', methods=['GET'])
def status():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            return jsonify({
                'authenticated': True,
                'codename': user.codename,
                'clearance_level': user.clearance_level
            }), 200
    return jsonify({'authenticated': False}), 200
