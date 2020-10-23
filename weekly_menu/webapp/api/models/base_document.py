from datetime import datetime

from .. import mongo

class BaseDocument(mongo.Document):

  owner = mongo.ReferenceField('User', required=True)

  insert_timestamp = mongo.LongField(required=True, default=lambda: int(datetime.utcnow().timestamp()*1000))
  update_timestamp = mongo.LongField(required=True, default=lambda: int(datetime.utcnow().timestamp()*1000))

  meta = {
    'abstract': True,
    'strict': False
  }
