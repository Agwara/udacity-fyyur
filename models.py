
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
  __tablename__ = 'venues'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  genres = db.Column(db.String(120))

  website_link = db.Column(db.String(120))
  seeking_talent = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String(120))
  shows = db.relationship('Show', backref='venue', lazy=True, cascade="all, delete")

  def venue_dict(self):
    return {
      'id': self.id,
      'name': self.name,
      'city': self.city,
      'state': self.state,
      'address': self.address,
      'phone': self.phone,
      'genres': self.genres.split(','),  
      'image_link': self.image_link,
      'facebook_link': self.facebook_link,
      'website_link': self.website_link,
      'seeking_talent': self.seeking_talent,
      'seeking_description': self.seeking_description,
    }

  def __repr__(self):
    return f'<Venue {self.id} {self.name} {self.city}>'

class Artist(db.Model):
  __tablename__ = 'artists'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  
  website_link = db.Column(db.String(120))
  seeking_venue = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String(120))

  start_availability = db.Column(db.DateTime)

  end_availability = db.Column(db.DateTime)

  shows = db.relationship('Show', backref='artist', lazy=True)

  def artist_dict(self):
    return {
      'id': self.id,
      'name': self.name,
      'city': self.city,
      'state': self.state,
      'phone': self.phone,
      'genres': self.genres.split(','),
      'image_link': self.image_link,
      'facebook_link': self.facebook_link,
      'website_link': self.website_link,
      'seeking_venue': self.seeking_venue,
      'seeking_description': self.seeking_description,
    }

  def __repr__(self):
    return f'<Artist {self.id} {self.name} {self.city}>'


class Show(db.Model):
  __tablename__ = 'shows'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id', ondelete="CASCADE"), nullable=False,)
  start_time = db.Column(db.DateTime, nullable=False)

  def __repr__(self):
      return f'<Show {self.id} {self.artist_id} {self.venue_id} {self.start_time}>'