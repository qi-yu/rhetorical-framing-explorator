from sqlalchemy import Column, String
from marshmallow import Schema, fields
from .entity import Entity, Base


class Feature(Entity, Base):
    __tablename__ = 'features'

    def __init__(self, id, name, dimension):
        Entity.__init__(self, id, name, dimension)

class FeatureSchema(Schema):
    id = fields.Number()
    name = fields.Str()
    dimension = fields.Str()