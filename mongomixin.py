from mongoengine import *
import mongoengine
from pymongo.objectid import ObjectId
from types import ModuleType
from itertools import groupby

import colander
import deform

class MongoMixin(object):
    """
    MongoMixin is, as it's name implies, a mixin class that is meant to be "injected" into your
    mongoengine Document sub-classes to provide a slew of useful functionality for web applications
    that aren't provided for with the base Document class from mongoengine.
    
    If you need a primer on what a mixin is and why they are useful, see the aptly titled:
    http://stackoverflow.com/questions/533631/what-is-a-mixin-and-why-are-they-useful
    
    For example, say you have a mongoengine Document class like this:
    class Person(Document):
        firstname = StringField(required=True)
        lastname = StringField(required=True)
        dob = DateTimeField()
        
    mongoengine is awesome, but when used in a web environment, there are common things that you're going
    to want to do with instances of Documents that it will feel very repetitive very quickly. For example, 
    if you are trying to write a service call for an AJAX callback and you want
    to "jsonify" a mongoengine Document, it will complain that it doesn't know how. If you do this...
    class Person(Document, MongoMixin):
        ...
        
    THEN, your Person class will be jsonifiable. You can can also call Person._to_dict() to get a plain
    old python dictionary out of an instance of a mongoengine Document.
    
    Probably the biggest piece though is the integration of Colander and Deform to provide an automated
    way to generate Colander schemas and Deform form objects so that you don't have to build CRUD forms
    by hand.
    """
    
    #the ambigious one is ListField...not clear right away how you intend to display that
    TYPEMAP = {
        StringField : colander.String,
        URLField : colander.String,
        EmailField : colander.String,
        IntField : colander.Integer,
        FloatField : colander.Float,
        DecimalField : colander.Decimal,
        DateTimeField : colander.DateTime,
        ComplexDateTimeField : colander.DateTime,
        ListField : None,
        SortedListField : None,
        DictField : None,
        MapField : None,
        ObjectIdField : colander.String,
        ReferenceField : None,
        GenericReferenceField : None,
        EmbeddedDocumentField : colander.Mapping,
        GenericEmbeddedDocumentField : colander.Mapping,
        BooleanField : colander.Boolean,
        FileField : None,
        BinaryField : None,
        GeoPointField : None,
        SequenceField : colander.Integer,
    }
    
    CREATE_BUTTONS = ('submit','cancel',)
    EDIT_BUTTONS = ('submit','cancel','delete',)
    
    def __json__(self):
        if isinstance(self, (mongoengine.Document, mongoengine.EmbeddedDocument)):
            out = dict(self._data)
            for k,v in out.items():
                if isinstance(v, ObjectId):
                    out[k] = str(v)
                elif isinstance(v, datetime.datetime):
                    out[k] = str(v)
        elif isinstance(self, mongoengine.queryset.QuerySet):
            out = list(self)
        elif isinstance(self, types.ModuleType):
            out = None
        elif isinstance(self, groupby):
            out = [ (g,list(l)) for g,l in self]
        elif isinstance(self, (list,dict)):
            out = self
        else:
            raise TypeError, "Could not JSON-encode type '%s': %s" % (type(self), str(self))
        return out
        
    def _to_dict(self):
        retval = {}
        for k, v in self._fields.iteritems():
            if isinstance(v, (ListField,)):
                retval[k] = []
                for listelement in getattr(self, k):
                    if hasattr(listelement,'_to_dict'):
                        retval[k].append(listelement._to_dict())
            else:
                retval[k] = getattr(self, k)
        return retval
        
    def _construct_node(self, nodetype, **kwargs):
        return colander.SchemaNode(nodetype, kwargs)
        
    def _mtype2ctype(self, mongofield):
        return self.TYPEMAP.get(type(mongofield), None)
            
    @property
    def colanderschema(self):
        cschema = self._construct_node(Mapping())
        for k, v in self._fields.iteritems():
            newnodetype = self._mtype2ctype(v)
            if newnodetype is None:
                continue
            cschema.add(newnodetype())
        return cschema
        
    def make_htmlform(self, entry=False, schema=None):
        buttons = EDIT_BUTTONS
        if entry:
            buttons = CREATE_BUTTONS
        if schema is None:
            schema = self.colanderschema
        return deform.Form(schema, buttons=buttons)
            