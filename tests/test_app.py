def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Heart Disease Prediction API running" in response.data