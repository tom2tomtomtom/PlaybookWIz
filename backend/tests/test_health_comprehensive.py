"""
Comprehensive health check tests.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_basic_health_check(self):
        """Test basic health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'PlaybookWiz API'
        assert 'version' in data
        assert 'environment' in data
        assert 'timestamp' in data

    def test_api_v1_health_check(self):
        """Test API v1 health check endpoint."""
        response = client.get('/api/v1/health/')
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'PlaybookWiz API'

    def test_liveness_check(self):
        """Test Kubernetes liveness probe."""
        response = client.get('/api/v1/health/liveness')
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'alive'
        assert data['service'] == 'PlaybookWiz API'
        assert 'timestamp' in data

    @patch('app.api.api_v1.endpoints.health.check_postgres')
    @patch('app.api.api_v1.endpoints.health.check_mongodb')
    @patch('app.api.api_v1.endpoints.health.check_redis')
    @patch('app.api.api_v1.endpoints.health.check_anthropic')
    def test_detailed_health_check_all_healthy(
        self, 
        mock_anthropic, 
        mock_redis, 
        mock_mongodb, 
        mock_postgres
    ):
        """Test detailed health check with all services healthy."""
        # Mock all services as healthy
        mock_postgres.return_value = {"status": "healthy", "response_time_ms": 10.5}
        mock_mongodb.return_value = {"status": "healthy", "response_time_ms": 15.2}
        mock_redis.return_value = {"status": "healthy", "response_time_ms": 5.1}
        mock_anthropic.return_value = {"status": "configured", "model": "claude-3-5-sonnet-20241022"}
        
        response = client.get('/api/v1/health/detailed')
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'PlaybookWiz API'
        assert 'components' in data
        assert data['components']['postgres']['status'] == 'healthy'
        assert data['components']['mongodb']['status'] == 'healthy'
        assert data['components']['redis']['status'] == 'healthy'
        assert data['components']['anthropic']['status'] == 'configured'

    @patch('app.api.api_v1.endpoints.health.check_postgres')
    @patch('app.api.api_v1.endpoints.health.check_mongodb')
    @patch('app.api.api_v1.endpoints.health.check_redis')
    @patch('app.api.api_v1.endpoints.health.check_anthropic')
    def test_detailed_health_check_postgres_unhealthy(
        self, 
        mock_anthropic, 
        mock_redis, 
        mock_mongodb, 
        mock_postgres
    ):
        """Test detailed health check with PostgreSQL unhealthy."""
        # Mock PostgreSQL as unhealthy (critical service)
        mock_postgres.return_value = {"status": "unhealthy", "error": "Connection refused"}
        mock_mongodb.return_value = {"status": "healthy", "response_time_ms": 15.2}
        mock_redis.return_value = {"status": "healthy", "response_time_ms": 5.1}
        mock_anthropic.return_value = {"status": "configured", "model": "claude-3-5-sonnet-20241022"}
        
        response = client.get('/api/v1/health/detailed')
        assert response.status_code == 503
        
        data = response.json()['detail']
        assert data['status'] == 'unhealthy'
        assert data['components']['postgres']['status'] == 'unhealthy'

    @patch('app.api.api_v1.endpoints.health.check_postgres')
    @patch('app.api.api_v1.endpoints.health.check_mongodb')
    @patch('app.api.api_v1.endpoints.health.check_redis')
    @patch('app.api.api_v1.endpoints.health.check_anthropic')
    def test_detailed_health_check_mongodb_unhealthy(
        self, 
        mock_anthropic, 
        mock_redis, 
        mock_mongodb, 
        mock_postgres
    ):
        """Test detailed health check with MongoDB unhealthy (non-critical)."""
        # Mock MongoDB as unhealthy (non-critical service)
        mock_postgres.return_value = {"status": "healthy", "response_time_ms": 10.5}
        mock_mongodb.return_value = {"status": "unhealthy", "error": "Connection timeout"}
        mock_redis.return_value = {"status": "healthy", "response_time_ms": 5.1}
        mock_anthropic.return_value = {"status": "configured", "model": "claude-3-5-sonnet-20241022"}
        
        response = client.get('/api/v1/health/detailed')
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'degraded'  # Not unhealthy because MongoDB is non-critical
        assert data['components']['mongodb']['status'] == 'unhealthy'

    @patch('app.api.api_v1.endpoints.health.check_postgres')
    @patch('app.api.api_v1.endpoints.health.check_redis')
    def test_readiness_check_healthy(self, mock_redis, mock_postgres):
        """Test Kubernetes readiness probe when healthy."""
        mock_postgres.return_value = {"status": "healthy", "response_time_ms": 10.5}
        mock_redis.return_value = {"status": "healthy", "response_time_ms": 5.1}
        
        response = client.get('/api/v1/health/readiness')
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'ready'
        assert data['postgres']['status'] == 'healthy'
        assert data['redis']['status'] == 'healthy'

    @patch('app.api.api_v1.endpoints.health.check_postgres')
    @patch('app.api.api_v1.endpoints.health.check_redis')
    def test_readiness_check_not_ready(self, mock_redis, mock_postgres):
        """Test Kubernetes readiness probe when not ready."""
        mock_postgres.return_value = {"status": "unhealthy", "error": "Connection refused"}
        mock_redis.return_value = {"status": "healthy", "response_time_ms": 5.1}
        
        response = client.get('/api/v1/health/readiness')
        assert response.status_code == 503
        
        data = response.json()['detail']
        assert data['status'] == 'not_ready'
        assert data['postgres']['status'] == 'unhealthy'


class TestHealthCheckFunctions:
    """Test individual health check functions."""

    @pytest.mark.asyncio
    @patch('app.api.api_v1.endpoints.health.engine')
    async def test_check_postgres_healthy(self, mock_engine):
        """Test PostgreSQL health check when healthy."""
        from app.api.api_v1.endpoints.health import check_postgres
        
        # Mock successful database connection
        mock_conn = AsyncMock()
        mock_engine.begin.return_value.__aenter__.return_value = mock_conn
        mock_conn.execute.return_value = None
        
        result = await check_postgres()
        
        assert result['status'] == 'healthy'
        assert 'response_time_ms' in result
        assert isinstance(result['response_time_ms'], float)

    @pytest.mark.asyncio
    @patch('app.api.api_v1.endpoints.health.engine')
    async def test_check_postgres_unhealthy(self, mock_engine):
        """Test PostgreSQL health check when unhealthy."""
        from app.api.api_v1.endpoints.health import check_postgres
        
        # Mock database connection failure
        mock_engine.begin.side_effect = Exception("Connection refused")
        
        result = await check_postgres()
        
        assert result['status'] == 'unhealthy'
        assert 'error' in result
        assert 'Connection refused' in result['error']

    @pytest.mark.asyncio
    @patch('app.api.api_v1.endpoints.health.mongodb')
    async def test_check_mongodb_healthy(self, mock_mongodb):
        """Test MongoDB health check when healthy."""
        from app.api.api_v1.endpoints.health import check_mongodb
        
        # Mock successful MongoDB connection
        mock_client = AsyncMock()
        mock_mongodb.client = mock_client
        mock_client.admin.command.return_value = {"ok": 1}
        
        result = await check_mongodb()
        
        assert result['status'] == 'healthy'
        assert 'response_time_ms' in result

    @pytest.mark.asyncio
    @patch('app.api.api_v1.endpoints.health.redis_db')
    async def test_check_redis_healthy(self, mock_redis_db):
        """Test Redis health check when healthy."""
        from app.api.api_v1.endpoints.health import check_redis
        
        # Mock successful Redis connection
        mock_redis = AsyncMock()
        mock_redis_db.redis = mock_redis
        mock_redis.ping.return_value = True
        
        result = await check_redis()
        
        assert result['status'] == 'healthy'
        assert 'response_time_ms' in result

    @pytest.mark.asyncio
    @patch('app.api.api_v1.endpoints.health.settings')
    async def test_check_anthropic_configured(self, mock_settings):
        """Test Anthropic health check when configured."""
        from app.api.api_v1.endpoints.health import check_anthropic
        
        mock_settings.ANTHROPIC_API_KEY = "test-api-key"
        mock_settings.ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"
        
        result = await check_anthropic()
        
        assert result['status'] == 'configured'
        assert result['model'] == 'claude-3-5-sonnet-20241022'

    @pytest.mark.asyncio
    @patch('app.api.api_v1.endpoints.health.settings')
    async def test_check_anthropic_not_configured(self, mock_settings):
        """Test Anthropic health check when not configured."""
        from app.api.api_v1.endpoints.health import check_anthropic
        
        mock_settings.ANTHROPIC_API_KEY = None
        
        result = await check_anthropic()
        
        assert result['status'] == 'not_configured'
        assert 'error' in result
