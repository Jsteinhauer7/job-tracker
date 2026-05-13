def test_register_success(client):
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'password123'
    })
    assert response.status_code == 302  # redirects to dashboard on success

def test_register_duplicate_email(client):
    client.post('/register', data={
        'username': 'user1',
        'email': 'same@example.com',
        'password': 'password123'
    })
    response = client.post('/register', data={
        'username': 'user2',
        'email': 'same@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert b'Email already registered' in response.data

def test_login_success(client):
    client.post('/register', data={
        'username': 'user',
        'email': 'user@example.com',
        'password': 'password123'
    })
    response = client.post('/login', data={
        'email': 'user@example.com',
        'password': 'password123'
    })
    assert response.status_code == 302  # redirects to dashboard

def test_login_wrong_password(client):
    client.post('/register', data={
        'username': 'user',
        'email': 'user@example.com',
        'password': 'password123'
    })
    response = client.post('/login', data={
        'email': 'user@example.com',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert b'Invalid email or password' in response.data

def test_login_unknown_email(client):
    response = client.post('/login', data={
        'email': 'nobody@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert b'Invalid email or password' in response.data

def test_logout(auth_client):
    response = auth_client.get('/logout')
    assert response.status_code == 302  # redirects to login
