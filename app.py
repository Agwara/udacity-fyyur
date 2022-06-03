#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler

from sqlalchemy import true
from forms import *
from flask_migrate import Migrate

from models import db, Artist, Venue, Show

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# TODO: connect to a local postgresql database
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:dopiferrdk1234!A@localhost:5432/fyyur"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  allVenues = db.session().query(Venue).all()

  unique_list = []

  response = []

  # Differenciate between states and cities
  for data in allVenues:
    state_city = [data.city, data.state]
    if not ((state_city in unique_list)):
      unique_list.append(state_city)

  for data in unique_list: 
    temp_city = data[0]
    temp_state = data[1]
    temp_venue = []

    for dataTwo in allVenues:
      if (temp_city == dataTwo.city and temp_state == dataTwo.state):
        temp_venue.append({
          'id': dataTwo.id,
          'name': dataTwo.name,
          'num_upcoming_shows': len(list(filter(lambda x: x.start_time > datetime.today(), dataTwo.shows)))
        })

    response.append({
       'city': temp_city,
       'state': temp_state,
       'venues': temp_venue
    })   

  return render_template('pages/venues.html', areas=response)
  

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search=  request.form.get('search_term', '')
  venues =  Venue.query.filter(Venue.name.ilike(f'%{search}%')).all()

  data = []

  for venue in venues: 
    data.append({
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': len(venue.shows)
    })
  response = {
    'count': len(venues),
    'data': data
  }  

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)

  past_shows = list(filter(lambda x: x.start_time < datetime.today(), venue.shows))

  upcoming_shows = list(filter(lambda x: x.start_time >= datetime.today(), venue.shows))

  def display_artist(show_param):
    temp_list = []
    for show in show_param:
      testShow = Show.query.get(show.id)

      temp_list.append({
        'artist_id': testShow.artist.id,
        'artist_name': testShow.artist.name,
        'artist_image_link': testShow.artist.image_link,
        'start_time': str(testShow.start_time)
      })
    return temp_list

  dataDict = venue.venue_dict()

  dataDict['past_shows'] = display_artist(past_shows)
  dataDict['upcoming_shows'] = display_artist(upcoming_shows)
  dataDict['past_shows_count'] = len(past_shows)
  dataDict['upcoming_shows_count'] = len(upcoming_shows)

  return render_template('pages/show_venue.html', venue=dataDict)


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  try:
    venue = Venue()
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.address = request.form['address']
    venue.genres = ','.join(request.form.getlist('genres'))
    venue.website_link = request.form['website_link']
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.seeking_description = request.form['seeking_description']

    if(request.form.get('seeking_talent')):
      venue.seeking_talent = True
    else:
      venue.seeking_talent = False

    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    else:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  form.name.data = venue.name
  form.city.data = venue.city
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  form.website_link.data = venue.website_link
  form.image_link.data = venue.image_link
  form.seeking_description.data = venue.seeking_description
  form.seeking_talent.data = venue.seeking_talent

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  venue = Venue.query.get(venue_id)

  initial_name = venue.name

  error = False
  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = ','.join(request.form.getlist('genres')) 
    venue.facebook_link = request.form['facebook_link']
    venue.website_link = request.form['website_link']
    venue.image_link = request.form['image_link']

    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
    else:
      flash('Venue ' + initial_name + ' was successfully updated!')
  return redirect(url_for('show_venue', venue_id=venue_id))



@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False

  try:
    Venue.query.filter(Venue.id == venue_id).delete()
    db.session.commit()
  except Exception as e:
    print(e)
    db.session.rollback()
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Venue ' + 'with ID: ' + venue_id + ' could not be deleted.')
    else:
      flash(' Venue ' + 'with ID: ' + venue_id + ' have been successfully deleted.')
    return redirect(url_for('index'))

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
 

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.with_entities(Artist.id, Artist.name).group_by(Artist.id).all()
  return render_template('pages/artists.html', artists=artists )

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search=  request.form.get('search_term', '')
  artists =  Artist.query.filter(Artist.name.ilike(f'%{search}%')).all()
    
  data = []

  for artist in artists: 
    data.append({
      'id': artist.id,
      'name': artist.name,
      'num_upcoming_shows': len(artist.shows)
    })

  response = {
    'count': len(artists),
    'data': data
  }  
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  artist = Artist.query.get(artist_id)

  past_shows = list(filter(lambda x: x.start_time < datetime.today(), artist.shows))

  upcoming_shows = list(filter(lambda x: x.start_time >= datetime.today(), artist.shows))

  def display_venue(show_param):
    temp_list = []
    for show in show_param:
      testShow = Show.query.get(show.id)

      temp_list.append({
        'venue_id': testShow.artist.id,
        'venue_name': testShow.venue.name,
        'venue_image_link': testShow.venue.image_link,
        'start_time': str(testShow.start_time)
      })
    return temp_list

  dataDict = artist.artist_dict()

  dataDict['past_shows'] = display_venue(past_shows)
  dataDict['upcoming_shows'] = display_venue(upcoming_shows)
  dataDict['past_shows_count'] = len(past_shows)
  dataDict['upcoming_shows_count'] = len(upcoming_shows)

  return render_template('pages/show_artist.html', artist=dataDict)


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)

  form = ArtistForm()

  form.name.data = artist.name
  form.city.data = artist.city
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  form.website_link.data = artist.website_link
  form.image_link.data = artist.image_link
  form.seeking_description.data = artist.seeking_description
  form.seeking_venue.data = artist.seeking_venue
  form.start_availability.data = artist.start_availability
  form.end_availability.data = artist.end_availability

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = ','.join(request.form.getlist('genres'))
    artist.website_link = request.form['website_link']
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.seeking_description = request.form['seeking_description']
    artist.start_availability = request.form['start_availability']
    artist.end_availability = request.form['end_availability']

    if request.form['start_availability'] > request.form['end_availability']:
      error = True
      flash('Start availability time should not be greater than end availability time')
    else:
      db.session.add(artist)
      db.session.commit() 

  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
    else:
      flash('Venue ' + request.form['name'] + ' was successfully updated!')
    return redirect(url_for('show_artist', artist_id=artist_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()

  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False

  dateError = False

  try:
    artist = Artist()
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = ','.join(request.form.getlist('genres'))
    artist.website_link = request.form['website_link']
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.seeking_description = request.form['seeking_description']
    artist.start_availability = request.form['start_availability']
    artist.end_availability = request.form['end_availability']

    if(request.form.get('seeking_venue')):
      artist.seeking_venue = False
    else:
      artist.seeking_venue = True

    if request.form['start_availability'] > request.form['end_availability']:
      dateError = True
    else:
      db.session.add(artist)
      db.session.commit()  

  except:
    error = True
    db.session.rollback()
  finally:
    form = ArtistForm()
    db.session.close()
    if error:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      return render_template('forms/new_artist.html', form=form)
    elif dateError:
      flash('Start  availability time should be less than end availability time!')  
      return render_template('forms/new_artist.html', form=form)
    else:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  allShows = Show.query.join(Artist, Artist.id == Show.artist_id).join(Venue, Venue.id == Show.venue_id).all()

  destructuredData = []

  for show in allShows:
    print("Testing: ", show.venue.id)

    destructuredData.append({
      'venue_id': show.venue.id,
      'venue_name': show.venue.name,
      'artist_id': show.artist.id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time.isoformat()
    })

  return render_template('pages/shows.html', shows=destructuredData)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  availability_error = False
  try:
    show = Show()
    show.artist_id = request.form['artist_id']
    show.venue_id = request.form['venue_id']
    show.start_time = request.form['start_time']

    show_artist = Artist.query.get(request.form['artist_id'])

    date_time_obj = datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S')

    # Check to see if Artist is available
    if ((date_time_obj < show_artist.start_availability) or (date_time_obj > show_artist.end_availability)):
      availability_error = True
    else:
      db.session.add(show)
      db.session.commit()

  except Exception as e:
    print(e)
    db.session.rollback()
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Show could not be crated!.')
    elif availability_error:
      flash('Artist ' + show_artist.name + ' is unavailable at this time')
    else:
      flash('Requested show was successfully listed')
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
  app.debug = True
  app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''