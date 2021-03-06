from . import *

class Authors(Base):
  __tablename__ = 'authors'

  index = db.Column(db.Integer, nullable=False)
  name = db.Column(db.Text, nullable=False)
  vector = db.Column(db.Text, nullable=False)




  def __repr__(self):
    return '<Name: %r, Index: %r>' % (self.name, self.index)
    #print("Total score for %s is %s" % (name, score))


class Authorschema(ModelSchema):
  class Meta:
    model = Authors
