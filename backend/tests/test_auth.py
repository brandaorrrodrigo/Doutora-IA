"""
Tests for authentication endpoints
"""

import pytest
from fastapi import status


class TestAuth Endpoints:
    """Test authentication functionality"""

    def test_register_success(self, client):
        """Test successful user registration"""
        response = client.post(
            "/auth/register",
            params={
                "email": "newuser@example.com",
                "password": "secure_password123",
                "role": "user"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["role"] == "user"
        assert "message" in data

    def test_register_invalid_email(self, client):
        """Test registration with invalid email"""
        response = client.post(
            "/auth/register",
            params={
                "email": "invalid-email",
                "password": "password123",
                "role": "user"
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "inválido" in response.json()["detail"].lower()

    def test_register_short_password(self, client):
        """Test registration with short password"""
        response = client.post(
            "/auth/register",
            params={
                "email": "test@example.com",
                "password": "12345",  # Too short
                "role": "user"
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "6 caracteres" in response.json()["detail"]

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with existing email"""
        response = client.post(
            "/auth/register",
            params={
                "email": test_user.email,
                "password": "password123",
                "role": "user"
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "já cadastrado" in response.json()["detail"].lower()

    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post(
            "/auth/login",
            params={
                "email": test_user.email,
                "password": "testpassword123"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == test_user.email

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password"""
        response = client.post(
            "/auth/login",
            params={
                "email": test_user.email,
                "password": "wrongpassword"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post(
            "/auth/login",
            params={
                "email": "nonexistent@example.com",
                "password": "password123"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user(self, client, auth_headers, test_user):
        """Test getting current user info"""
        response = client.get(
            "/auth/me",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
        assert data["role"] == test_user.role

    def test_get_current_user_without_token(self, client):
        """Test getting current user without authentication"""
        response = client.get("/auth/me")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token"""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token(self, client, auth_headers):
        """Test refreshing access token"""
        response = client.post(
            "/auth/refresh",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_jwt_token_contains_user_info(self, client, test_user):
        """Test that JWT token contains correct user information"""
        from services.auth import create_access_token, verify_token

        token_data = {
            "sub": str(test_user.id),
            "email": test_user.email,
            "role": test_user.role
        }
        token = create_access_token(token_data)

        # Verify token
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == str(test_user.id)
        assert payload["email"] == test_user.email
        assert payload["role"] == test_user.role

    def test_password_hashing(self):
        """Test password hashing and verification"""
        from services.auth import hash_password, verify_password

        password = "my_secure_password_123"
        hashed = hash_password(password)

        # Should not be plain text
        assert hashed != password

        # Should verify correctly
        assert verify_password(password, hashed) is True

        # Should not verify wrong password
        assert verify_password("wrong_password", hashed) is False
