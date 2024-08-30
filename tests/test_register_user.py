def test_register_user(client):
    response = client.post('/register', json={
        'username': 'testuser1',
        'email': 'testuser1@example.com',
        'mobile_number': '1234567891',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    assert response.status_code == 201
    assert response.json['success'] == True

def test_register_user_missing_fields(client):
    response = client.post('/register', json={
        'username': 'testuser',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    assert response.status_code == 400
    assert response.json['success'] == False

def test_register_user_password_mismatch(client):
    response = client.post('/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'mobile_number': '1234567890',
        'password': 'password123',
        'confirm_password': 'differentpassword'
    })
    assert response.status_code == 400
    assert response.json['success'] == False

def test_register_user_username_exists(client):
    client.post('/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'mobile_number': '1234567890',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    response = client.post('/register', json={
        'username': 'testuser',
        'email': 'newuser@example.com',
        'mobile_number': '0987654321',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    assert response.status_code == 400
    assert response.json['success'] == False

def test_register_user_email_exists(client):
    client.post('/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'mobile_number': '1234567890',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    response = client.post('/register', json={
        'username': 'newuser',
        'email': 'testuser@example.com',
        'mobile_number': '0987654321',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    assert response.status_code == 400
    assert response.json['success'] == False