def add_job(client, company='Acme', role='Engineer', status='Applied'):
    return client.post('/add', data={
        'company': company,
        'role': role,
        'status': status,
        'notes': 'Test note',
        'date_applied': '2026-05-13'
    })

def test_dashboard_requires_login(client):
    response = client.get('/')
    assert response.status_code == 302  # redirects unauthenticated users to login

def test_dashboard_loads(auth_client):
    response = auth_client.get('/')
    assert response.status_code == 200

def test_add_job(auth_client):
    response = add_job(auth_client, company='Google', role='SWE')
    assert response.status_code == 302  # redirects to dashboard after add

def test_job_appears_on_dashboard(auth_client):
    add_job(auth_client, company='Google', role='SWE')
    response = auth_client.get('/', follow_redirects=True)
    assert b'Google' in response.data
    assert b'SWE' in response.data

def test_edit_job(auth_client):
    add_job(auth_client, company='Google', role='SWE')
    response = auth_client.post('/edit/1', data={
        'company': 'Meta',
        'role': 'Engineer',
        'status': 'Interview',
        'notes': 'Updated',
        'date_applied': '2026-05-13'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Meta' in response.data

def test_delete_job(auth_client):
    add_job(auth_client, company='Google', role='SWE')
    auth_client.get('/delete/1')
    response = auth_client.get('/')
    assert b'Google' not in response.data

def test_status_filter(auth_client):
    add_job(auth_client, company='Google', role='SWE', status='Applied')
    add_job(auth_client, company='Meta', role='Engineer', status='Interview')
    response = auth_client.get('/?status=Interview')
    assert b'Meta' in response.data
    assert b'Google' not in response.data

def test_cannot_edit_other_users_job(client):
    # Register two users
    client.post('/register', data={'username': 'user1', 'email': 'user1@example.com', 'password': 'pass'})
    client.post('/register', data={'username': 'user2', 'email': 'user2@example.com', 'password': 'pass'})

    # Login as user1 and add a job
    client.post('/login', data={'email': 'user1@example.com', 'password': 'pass'})
    add_job(client, company='Secret Co', role='Dev')
    client.get('/logout')

    # Login as user2 and try to edit user1's job
    client.post('/login', data={'email': 'user2@example.com', 'password': 'pass'})
    response = client.post('/edit/1', data={
        'company': 'Hacked',
        'role': 'Hacker',
        'status': 'Applied',
        'notes': '',
        'date_applied': '2026-05-13'
    }, follow_redirects=True)
    # Should redirect away, not save the change
    assert b'Hacked' not in response.data
