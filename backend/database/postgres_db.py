"""Small SQLAlchemy-backed adapters preserving existing service contracts."""
from uuid import uuid4
from sqlalchemy import select
from backend.database.postgres import session_scope
from backend.database.models import User, StoredDocument, Chat, Message, FaceEmbedding

class Snapshot:
    def __init__(self, collection, key, data=None): self.collection, self.id, self._data = collection, str(key), data
    @property
    def exists(self): return self._data is not None
    @property
    def reference(self): return self
    def to_dict(self): return dict(self._data) if self._data else {}
    def get(self):
        with session_scope() as s: self._data = self.collection.get_data(s, self.id)
        return self
    def set(self, value): self.collection.save(self.id, value, replace=True)
    def update(self, value): self.collection.save(self.id, value, replace=False)
    def delete(self): self.collection.delete(self.id)
class Query:
    def __init__(self, collection, field, value): self.collection,self.field,self.value,self.count=collection,field,value,None
    def limit(self, count): self.count=count; return self
    def stream(self): return self.collection.find(self.field, self.value, self.count)
class Collection:
    def __init__(self, model, key): self.model,self.key=model,key
    def document(self, key=None): return Snapshot(self, key or str(uuid4()))
    def add(self, value): ref=self.document(); ref.set(value); return None,ref
    def where(self, field, _operator, value): return Query(self,field,value)
    def stream(self): return self.find(None,None,None)
    def get_data(self,s,key):
        row = self._row(s, key)
        return self.to_data(row) if row else None
    def to_data(self,row): return {column.name:getattr(row,column.name) for column in row.__table__.columns}
    def save(self,key,value,replace):
        with session_scope() as s:
            row = self._row(s, key)
            if row is None: row=self.model(**{self.key:key, **value}); s.add(row)
            else:
                for field,item in value.items(): setattr(row,field,item)
    def delete(self,key):
        with session_scope() as s:
            row = self._row(s, key)
            if row: s.delete(row)
    def _row(self, session, key):
        primary_key = next(column.name for column in self.model.__table__.primary_key.columns)
        if self.key == primary_key:
            return session.get(self.model, key)
        return session.scalar(select(self.model).where(getattr(self.model, self.key) == key))
    def find(self,field,value,count):
        with session_scope() as s:
            statement=select(self.model)
            if field: statement=statement.where(getattr(self.model,field)==value)
            if count: statement=statement.limit(count)
            return [Snapshot(self,getattr(row,self.key),self.to_data(row)) for row in s.scalars(statement).all()]
users_collection=Collection(User,"id")
documents_collection=Collection(StoredDocument,"document_id")
chats_collection=Collection(Chat,"chat_id")
messages_collection=Collection(Message,"id")
face_embeddings_collection=Collection(FaceEmbedding,"user_id")
