import pytest

from datetime import datetime
from uuid import uuid4

from flask import jsonify
from flask.json import dumps, loads
from flask.testing import FlaskClient

from conftest import add_offline_id

from test_ingredient import create_ingredient, delete_ingredient

@add_offline_id
def create_recipe(client, json, auth_headers, generate_offline_id: bool = True):
  if generate_offline_id == False:
      del json['offline_id']
  
  return client.post('/api/v1/recipes', json=json, headers=auth_headers)

def patch_recipe(client, recipe_id, json, auth_headers):
  return client.patch('/api/v1/recipes/{}'.format(recipe_id), json=json, headers=auth_headers)

def put_recipe(client, recipe_id, json, auth_headers):
  return client.put('/api/v1/recipes/{}'.format(recipe_id), json=json, headers=auth_headers)

def replace_recipe(client, recipe_id, json, auth_headers):
  return client.put('/api/v1/recipes/{}'.format(recipe_id), json=json, headers=auth_headers)

def get_recipe(client, recipe_id, auth_headers):
  return client.get('/api/v1/recipes/{}'.format(recipe_id), headers=auth_headers)

def get_all_recipes(client, auth_headers, page=1, per_page=10, order_by='', desc=False):
  return client.get('/api/v1/recipes?page={}&per_page={}&order_by={}&desc={}'.format(page, per_page, order_by, desc), headers=auth_headers)

def test_not_authorized(client: FlaskClient):
  response = get_all_recipes(client, {})
  
  assert response.status_code == 401

def test_create_with_supplied_id(client: FlaskClient, auth_headers):
    response = create_recipe(client, {
        'name': 'Menu',
        'id': '5e4ae04561fe8235a5a18824'
    }, auth_headers)

    assert response.status_code == 403

    response = patch_recipe(client, '1fe8235a5a5e4ae045618824', {
        'name': 'Menu',
        'id': '1fe8235a5a5e4ae045618824'
    }, auth_headers)

    assert response.status_code == 403

    response = put_recipe(client, '1fe8235a5a5e4ae045618824', {
        'name': 'Menu',
        'id': '1fe8235a5a5e4ae045618824'
    }, auth_headers)

    assert response.status_code == 403

def test_create_with_different_owner_not_allowed(client: FlaskClient, auth_headers):

    response = create_recipe(client, {
        'name': 'ham',
        'owner': 'pippo'
    }, auth_headers)

    assert response.status_code == 403

def test_owner_update(client: FlaskClient, auth_headers):
    response = create_ingredient(client, {
        'name': 'ham'
    }, auth_headers)

    recipe_id = response.json['_id']

    # Try to update owner using an integer instead of a string
    response = patch_recipe(client, response.json['_id'], {
        'owner': 1
    }, auth_headers)

    assert response.status_code == 400

    # Try to update owner using a valid objectId (from recipe_id)
    response = patch_recipe(client, recipe_id, {
        'owner': recipe_id
    }, auth_headers)

    assert response.status_code == 403

def test_create_recipe(client: FlaskClient, auth_headers):
  response = get_all_recipes(client, auth_headers)

  assert response.status_code == 200 and len(response.json['results']) == 0 and response.json['pages'] == 0

  tuna_resp = create_ingredient(client, {
    'name' : 'Tuna'
  }, auth_headers)

  tomato_resp = create_ingredient(client, {
    'name' : 'Tomatoes'
  }, auth_headers)

  response = create_recipe(client, {
    'name': 'Tuna and tomatoes',
    'ingredients' : [
      {
      'ingredient': tuna_resp.json['_id']
      },{
      'ingredient': tomato_resp.json['_id']
      }
    ]
  } , auth_headers)

  assert response.status_code == 201 and response.json['name'] == 'Tuna and tomatoes'

  # Test fail duplicating ingredient
  #response = create_recipe(client, {
  #  'name': 'Tuna and tomatoes'
  #} , auth_headers)

  #assert response.status_code == 409

  response = create_recipe(client, {
    'name': 'Pizza'
  } , auth_headers)

  assert response.status_code == 201 and response.json['name'] == 'Pizza'

  #Check pagination 
  response = get_all_recipes(client, auth_headers, 1, 1)

  assert response.status_code == 200 and response.json['pages'] == 2

def test_replace_recipe(client: FlaskClient, auth_headers):
  response = create_recipe(client, {
    'name': 'Tuna and tomatoes',
    'servs': 2
  } , auth_headers)

  assert response.status_code == 201 and response.json['servs'] == 2

  response = replace_recipe(client, response.json['_id'], {
    'name': 'Tuna and tomatoes',
    'servs': 3
  }, auth_headers)
  
  assert response.status_code == 200 and response.json['servs'] == 3

def test_duplicate_recipe_allowed(client: FlaskClient, auth_headers):
  response = create_recipe(client, {
    'name': 'Tuna and tomatoes',
    'servs': 2
  } , auth_headers)

  assert response.status_code == 201

  response = create_recipe(client, {
    'name': 'Tuna and tomatoes',
    'servs': 3
  }, auth_headers)
  
  assert response.status_code == 201

  response = get_all_recipes(client, auth_headers)

  assert response.status_code == 200 and len(response.json['results']) == 2 and response.json['pages'] == 1

def test_update_recipe(client: FlaskClient, auth_headers):
  response = create_recipe(client, {
    'name': 'Tuna and tomatoes'
  } , auth_headers)

  assert response.status_code == 201 and 'description' not in response.json

  response = patch_recipe(client, response.json['_id'], {
    'name': 'Tuna and tomatoes',
    'description': 'Test description'
  }, auth_headers)
  
  assert response.status_code == 200 and response.json['description'] == 'Test description'

def test_offline_id(client: FlaskClient, auth_headers):
    response = create_recipe(client, {
        'name' : 'Fish'
    }, auth_headers, False)

    assert response.status_code == 400

    response = create_recipe(client, {
        'name' : 'Fish'
    }, auth_headers)

    assert response.status_code == 201 \
        and response.json['_id'] is not None \
        and response.json['offline_id'] is not None

    idx = response.json['_id']
    offline_id = response.json['offline_id']

    response = put_recipe(client, idx, {
        'name' : 'Fish',
        'offline_id': str(uuid4())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_ID'

    response = patch_recipe(client, idx, {
        'name' : 'Fish',
        'offline_id': str(uuid4())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_ID'
    
    response = get_recipe(client, idx, auth_headers)

    assert response.status_code == 200 \
        and response.json['offline_id'] == offline_id

def test_create_update_timestamp(client: FlaskClient, auth_headers):
    response = create_recipe(client, {
        'name': 'Rice',
        'insert_timestamp': str(datetime.now())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'
    
    response = create_recipe(client, {
        'name': 'Rice',
        'update_timestamp': str(datetime.now())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = create_recipe(client, {
        'name': 'Rice',
        'update_timestamp': str(datetime.now()),
        'insert_timestamp': str(datetime.now())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'
    
    response = create_recipe(client, {
        'name': 'Rice',
    }, auth_headers)

    assert response.status_code == 201 \
        and response.json['insert_timestamp'] is not None \
            and isinstance(response.json['insert_timestamp'], int) \
        and response.json['update_timestamp'] is not None \
            and isinstance(response.json['update_timestamp'], int)    
    
    idx = response.json['_id']
    insert_timestamp = response.json['insert_timestamp']
    update_timestamp = response.json['update_timestamp']
    
    response = put_recipe(client, idx, {
        'name': 'Tomato',
        'update_timestamp': str(datetime.now())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = patch_recipe(client, idx, {
        'name': 'Tomato',
        'insert_timestamp': str(datetime.now())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = patch_recipe(client, idx, {
        'name': 'Tomato',
        'insert_timestamp': str(datetime.now()),
        'update_timestamp': str(datetime.now())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = put_recipe(client, idx, {
        'name': 'Tomato',
        'insert_timestamp': str(datetime.now()),
        'update_timestamp': str(datetime.now())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = patch_recipe(client, idx, {
        'name': 'Tomato',
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['insert_timestamp'] == insert_timestamp \
        and response.json['update_timestamp'] > update_timestamp
    
    update_timestamp = response.json['update_timestamp']

    response = put_recipe(client, idx, {
        'name': 'Tomato',
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['name'] == 'Tomato' \
        and response.json['insert_timestamp'] == insert_timestamp \
        and response.json['update_timestamp'] > update_timestamp
      
def test_get_last_updated(client: FlaskClient, auth_headers):
    response = create_recipe(client, {
        'name': 'Rice',
    }, auth_headers)

    assert response.status_code == 201  
    
    idx_1 = response.json['_id']
    insert_timestamp_1 = response.json['insert_timestamp']
    update_timestamp_1 = response.json['update_timestamp']

    response = create_recipe(client, {
        'name': 'Tomato',
    }, auth_headers)

    assert response.status_code == 201  
    
    idx_2 = response.json['_id']
    insert_timestamp_2 = response.json['insert_timestamp']
    update_timestamp_2 = response.json['update_timestamp']

    response = get_all_recipes(client, auth_headers, order_by='update_timestamp', desc=True, page=1, per_page=1)

    assert response.status_code == 200 \
        and len(response.json['results']) == 1 \
        and response.json['results'][0]['_id'] == idx_2

    response = patch_recipe(client, idx_1, {
        'name': 'Rice',
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['insert_timestamp'] == insert_timestamp_1 \
        and response.json['update_timestamp'] > update_timestamp_1
    
    update_timestamp_1 = response.json['update_timestamp']

    response = get_all_recipes(client, auth_headers, order_by='update_timestamp', desc=True, page=1, per_page=1)

    assert response.status_code == 200 \
        and len(response.json['results']) == 1 \
        and response.json['results'][0]['_id'] == idx_1 \
        and response.json['results'][0]['update_timestamp'] == update_timestamp_1

    response = put_recipe(client, idx_1, {
        'name': 'Rice',
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['insert_timestamp'] == insert_timestamp_1 \
        and response.json['update_timestamp'] > update_timestamp_1

    update_timestamp_1 = response.json['update_timestamp']

    response = get_all_recipes(client, auth_headers, order_by='update_timestamp', desc=True, page=1, per_page=1)

    assert response.status_code == 200 \
        and len(response.json['results']) == 1 \
        and response.json['results'][0]['_id'] == idx_1 \
        and response.json['results'][0]['update_timestamp'] == update_timestamp_1
    
    response = patch_recipe(client, idx_2, {
        'name': 'Tomato',
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['insert_timestamp'] == insert_timestamp_2 \
        and response.json['update_timestamp'] > update_timestamp_2
    
    update_timestamp_2 = response.json['update_timestamp']

    response = get_all_recipes(client, auth_headers, order_by='update_timestamp', desc=True, page=1, per_page=1)

    assert response.status_code == 200 \
        and len(response.json['results']) == 1 \
        and response.json['results'][0]['_id'] == idx_2 \
        and response.json['results'][0]['update_timestamp'] == update_timestamp_2

    response = put_recipe(client, idx_2, {
        'name': 'Tomato',
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['insert_timestamp'] == insert_timestamp_2 \
        and response.json['update_timestamp'] > update_timestamp_2

    update_timestamp_2 = response.json['update_timestamp']

    response = get_all_recipes(client, auth_headers, order_by='update_timestamp', desc=True, page=1, per_page=1)

    assert response.status_code == 200 \
        and len(response.json['results']) == 1 \
        and response.json['results'][0]['_id'] == idx_2 \
        and response.json['results'][0]['update_timestamp'] == update_timestamp_2
        