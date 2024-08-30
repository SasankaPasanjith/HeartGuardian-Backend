def test_get_past_predictions_no_token(client):
    response = client.get('/predictions')
    assert response.status_code == 403
    assert response.json['success'] == False

def test_get_past_predictions_with_token(client):
    client.post('/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'mobile_number': '1234567890',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    login_response = client.post('/login', json={
        'email': 'testuser@example.com',
        'password': 'password123'
    })
    token = login_response.json['data']['token']

    response = client.get('/predictions', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json['success'] == True