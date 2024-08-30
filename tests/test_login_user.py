def test_login_user(client):
    client.post('/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'mobile_number': '1234567890',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    response = client.post('/login', json={
        'email': 'testuser@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert response.json['success'] == True

def test_login_user_missing_fields(client):
    response = client.post('/login', json={
        'email': 'testuser@example.com'
    })
    assert response.status_code == 400
    assert response.json['success'] == False

def test_login_user_invalid_email(client):
    client.post('/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'mobile_number': '1234567890',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    response = client.post('/login', json={
        'email': 'wrongemail@example.com',
        'password': 'password123'
    })
    assert response.status_code == 401
    assert response.json['success'] == False

def test_login_user_invalid_password(client):
    client.post('/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'mobile_number': '1234567890',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    response = client.post('/login', json={
        'email': 'testuser@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert response.json['success'] == False