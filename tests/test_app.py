import pytest
import json
from app import app, db, Task


@pytest.fixture
def client():
    """Create a test client with an in-memory SQLite database."""
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


@pytest.fixture
def sample_task(client):
    """Create a sample task for testing."""
    with app.app_context():
        task = Task(
            title='Test Task',
            description='Test Description',
            completed=False
        )
        db.session.add(task)
        db.session.commit()
        task_id = task.id
    return task_id


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_check_returns_200(self, client):
        """Test that health endpoint returns 200 status."""
        response = client.get('/health')
        assert response.status_code == 200

    def test_health_check_returns_healthy_status(self, client):
        """Test that health endpoint returns healthy status."""
        response = client.get('/health')
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data


class TestGetTasks:
    """Tests for GET /api/tasks endpoint."""

    def test_get_tasks_empty_list(self, client):
        """Test getting tasks when database is empty."""
        response = client.get('/api/tasks')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == []

    def test_get_tasks_returns_tasks(self, client, sample_task):
        """Test getting tasks returns existing tasks."""
        response = client.get('/api/tasks')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['title'] == 'Test Task'


class TestCreateTask:
    """Tests for POST /api/tasks endpoint."""

    def test_create_task_success(self, client):
        """Test creating a new task successfully."""
        response = client.post(
            '/api/tasks',
            data=json.dumps({'title': 'New Task', 'description': 'New Description'}),
            content_type='application/json'
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['title'] == 'New Task'
        assert data['description'] == 'New Description'
        assert data['completed'] is False

    def test_create_task_minimal(self, client):
        """Test creating a task with only title."""
        response = client.post(
            '/api/tasks',
            data=json.dumps({'title': 'Minimal Task'}),
            content_type='application/json'
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['title'] == 'Minimal Task'

    def test_create_task_missing_title(self, client):
        """Test creating a task without title returns 400."""
        response = client.post(
            '/api/tasks',
            data=json.dumps({'description': 'No title'}),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_create_task_empty_body(self, client):
        """Test creating a task with empty body returns 400."""
        response = client.post(
            '/api/tasks',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400


class TestUpdateTask:
    """Tests for PUT /api/tasks/<id> endpoint."""

    def test_update_task_success(self, client, sample_task):
        """Test updating a task successfully."""
        response = client.put(
            f'/api/tasks/{sample_task}',
            data=json.dumps({'title': 'Updated Task', 'completed': True}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['title'] == 'Updated Task'
        assert data['completed'] is True

    def test_update_task_partial(self, client, sample_task):
        """Test partial update of a task."""
        response = client.put(
            f'/api/tasks/{sample_task}',
            data=json.dumps({'completed': True}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['title'] == 'Test Task'
        assert data['completed'] is True

    def test_update_task_not_found(self, client):
        """Test updating a non-existent task returns 404."""
        response = client.put(
            '/api/tasks/9999',
            data=json.dumps({'title': 'Updated'}),
            content_type='application/json'
        )
        assert response.status_code == 404

    def test_update_task_no_data(self, client, sample_task):
        """Test updating a task with no data returns 400."""
        response = client.put(
            f'/api/tasks/{sample_task}',
            data=json.dumps(None),
            content_type='application/json'
        )
        assert response.status_code == 400


class TestDeleteTask:
    """Tests for DELETE /api/tasks/<id> endpoint."""

    def test_delete_task_success(self, client, sample_task):
        """Test deleting a task successfully."""
        response = client.delete(f'/api/tasks/{sample_task}')
        assert response.status_code == 204

        # Verify task is deleted
        response = client.get('/api/tasks')
        data = json.loads(response.data)
        assert len(data) == 0

    def test_delete_task_not_found(self, client):
        """Test deleting a non-existent task returns 404."""
        response = client.delete('/api/tasks/9999')
        assert response.status_code == 404


class TestCSRFToken:
    """Tests for CSRF token endpoint."""

    def test_get_csrf_token(self, client):
        """Test getting CSRF token."""
        response = client.get('/api/csrf-token')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'csrf_token' in data
        assert len(data['csrf_token']) > 0


class TestErrorHandlers:
    """Tests for error handlers."""

    def test_404_handler(self, client):
        """Test 404 error handler."""
        response = client.get('/nonexistent-route')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data


class TestTaskModel:
    """Tests for Task model."""

    def test_task_to_dict(self, client):
        """Test Task.to_dict() method."""
        with app.app_context():
            task = Task(
                title='Dict Test',
                description='Testing to_dict',
                completed=True
            )
            db.session.add(task)
            db.session.commit()

            task_dict = task.to_dict()
            assert task_dict['title'] == 'Dict Test'
            assert task_dict['description'] == 'Testing to_dict'
            assert task_dict['completed'] is True
            assert 'id' in task_dict
            assert 'created_at' in task_dict
            assert 'updated_at' in task_dict
