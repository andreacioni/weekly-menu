import pytest

from test_shopping_list import get_all_shopping_list

from flask import jsonify
from flask.json import dumps, loads
from flask.testing import FlaskClient

from weekly_menu.webapp.api.models import User

def test_bad_request_registration(client: FlaskClient):
  response = client.post('/api/v1/auth/register', json={})

  assert response.status_code == 400

  response = client.post('/api/v1/auth/register', json={'username':'a'})

  assert response.status_code == 400

def test_user_creation(client: FlaskClient):
  response = client.post('/api/v1/auth/register', json={
    'username':"test2", 
    'password':"password12",
    'email':"pippo@pluto.com"
    })

  user_id = response.json['_id']

  assert response.status_code == 200

  response = client.post('/api/v1/auth/token', json={
    'username':"test2", 
    'password':'wrong-password'
  })

  assert response.status_code == 401

  response = client.post('/api/v1/auth/token', json={
    'username':"test2", 
    'password':"password12"
  })

  assert response.status_code == 200 and response.json['access_token'] is not None

  User.objects(id=user_id).get().delete()

def test_shopping_list_creation_on_registration(client: FlaskClient):
  response = client.post('/api/v1/auth/register', json={
    'username':"test_usr", 
    'password':"password",
    'email':"pippo@pluto.com"
    })

  assert response.status_code == 200

  response = client.post('/api/v1/auth/token', json={
    'username':"test_usr", 
    'password':"password"
  })

  assert response.status_code == 200 and response.json['access_token'] is not None

  response = get_all_shopping_list(client, {'Authorization' : 'Bearer {}'.format(response.json['access_token'])})

  assert response.status_code == 200 and response.json['pages'] == 1 and len(response.json['results']) == 1