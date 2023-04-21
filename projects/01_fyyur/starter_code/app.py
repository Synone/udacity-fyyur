# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
    Flask,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for,
    jsonify,
    abort,
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
import datetime
from model import Venue, Artist, Show, app

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#


# TODO: connect to a local postgresql database


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------
def merge_identical_data(list, key_field):
    group = {}
    for item in list:
        key = item[key_field]
        if key in group:
            group[key].append(item)
        else:
            group[key] = [item]
    return group


@app.route("/venues")
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    real_data = []
    load_venues = Venue.query.all()
    for venue in load_venues:
        real_data.append(
            {
                "id": venue.id,
                "city": venue.city,
                "state": venue.state,
                "name": venue.name,
            }
        )
    group_data = merge_identical_data(real_data, "city")
    data = []
    for key, value in group_data.items():
        venues = []
        for val in value:
            venues.append(
                {"id": val["id"], "name": val["name"], "num_upcoming_shows": 0}
            )
        data.append({"city": key, "state": val["state"], "venues": venues})
    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_string = request.form.get("search_term")
    data = []
    if search_string != "":
        result = Venue.query.filter(Venue.name.ilike(f"%{search_string}%")).all()
        for res in result:
            data.append({"id": res.id, "name": res.name, "num_upcoming_shows": 0})
    else:
        result = []
    response = {"count": len(result), "data": data}
    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    res_data = Venue.query.filter_by(id=venue_id).first()
    shows = Show.query.filter_by(venue_id=venue_id).all()
    past_shows = []
    upcoming_shows = []
    now = datetime.datetime.now()
    for show in shows:
        artist = Artist.query.filter_by(id=show.artist_id).first()
        if show.start_time < now:
            past_shows.append(
                {
                    "artist_id": artist.id,
                    "artist_name": artist.name,
                    "artist_image_link": artist.image_link,
                    "start_time": show.start_time.strftime("%Y/%m/%d %H:%M:%S"),
                }
            )
        else:
            upcoming_shows.append(
                {
                    "artist_id": artist.id,
                    "artist_name": artist.name,
                    "artist_image_link": artist.image_link,
                    "start_time": show.start_time.strftime("%Y/%m/%d %H:%M:%S"),
                }
            )
    # data = {
    #     "id": res_data.id,
    #     "name": res_data.name,
    #     "genres": res_data.genres.strip("{}").split(","),
    #     "address": res_data.address,
    #     "city": res_data.city,
    #     "state": res_data.state,
    #     "phone": res_data.phone,
    #     "website": res_data.website,
    #     "facebook_link": res_data.facebook_link,
    #     "seeking_talent": True if res_data.seeking_talent == "y" else False,
    #     "seeking_description": res_data.seeking_description,
    #     "image_link": res_data.image_link,
    #     "past_shows": past_shows,
    #     "upcoming_shows": upcoming_shows,
    #     "past_shows_count": len(past_shows),
    #     "upcoming_shows_count": len(upcoming_shows),
    # }
    res_data.upcoming_shows = upcoming_shows
    res_data.past_shows = past_shows
    res_data.genres = res_data.genres.strip("{}").split(",")
    res_data.upcoming_shows_count = len(upcoming_shows)
    res_data.past_shows = past_shows
    res_data.past_shows_count = len(past_shows)
    return render_template("pages/show_venue.html", venue=res_data)


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    error = False
    try:
        form_data = request.form
        venue = Venue(
            city=form_data["city"],
            state=form_data["state"],
            name=form_data["name"],
            address=form_data["address"],
            phone=form_data["phone"],
            image_link=form_data["image_link"],
            genres=form_data.getlist("genres"),
            facebook_link=form_data["facebook_link"],
            website=form_data["website_link"],
            seeking_description=form_data["seeking_description"],
            seeking_talent=form_data.get("seeking_talent", False),
        )
        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if not error:
            print("Create venue successfully")
        else:
            abort(400)
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    flash("Venue " + request.form["name"] + " was successfully listed!")
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    try:
        venue = Venue.query.get(venue_id)
        for show in venue.shows:
            db.session.delete(show)
        db.session.delete(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        flash("Something went wrong when deleting a venue")
    finally:
        if not error:
            flash("Delete venue successfully")
        else:
            abort(500)
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return render_template("pages/home.html")


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    # TODO: replace with real data returned from querying the database
    return_data = Artist.query.all()
    data = []
    for item in return_data:
        data.append({"id": item.id, "name": item.name})
    return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_string = request.form.get("search_term")
    data = []
    if search_string != "":
        result = Artist.query.filter(Artist.name.ilike(f"%{search_string}%")).all()
        for res in result:
            data.append({"id": res.id, "name": res.name})
    else:
        result = []
    response = {"count": len(result), "data": data}
    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    res_data = Artist.query.filter_by(id=artist_id).first()
    shows = Show.query.filter_by(artist_id=artist_id).all()
    upcoming_shows = []
    past_shows = []
    now = datetime.datetime.now()
    for show in shows:
        venue = Venue.query.filter_by(id=show.venue_id).first()
        if show.start_time < now:
            past_shows.append(
                {
                    "venue_id": show.venue_id,
                    "venue_name": venue.name,
                    "venue_image_link": venue.image_link,
                    "start_time": show.start_time.strftime("%Y/%m/%d %H:%M:%S"),
                }
            )
        else:
            upcoming_shows.append(
                {
                    "venue_id": show.venue_id,
                    "venue_name": venue.name,
                    "venue_image_link": venue.image_link,
                    "start_time": show.start_time.strftime("%Y/%m/%d %H:%M:%S"),
                }
            )
    # data = {
    #     "id": res_data.id,
    #     "name": res_data.name,
    #     "genres": res_data.genres.strip("{}").split(","),
    #     "city": res_data.city,
    #     "state": res_data.state,
    #     "phone": res_data.phone,
    #     "website": res_data.website,
    #     "facebook_link": res_data.facebook_link,
    #     "seeking_venue": res_data.seeking_venue,
    #     "seeking_description": res_data.seeking_description,
    #     "image_link": res_data.image_link,
    #     "past_shows": past_shows,
    #     "upcoming_shows": upcoming_shows,
    #     "past_shows_count": len(past_shows),
    #     "upcoming_shows_count": len(upcoming_shows),
    # }
    res_data.upcoming_shows = upcoming_shows
    res_data.past_shows = past_shows
    res_data.genres = res_data.genres.strip("{}").split(",")
    res_data.past_shows_count = len(past_shows)
    res_data.upcoming_shows_count = len(upcoming_shows)
    return render_template("pages/show_artist.html", artist=res_data)


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.filter_by(id=artist_id).first()
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    update_info = request.form
    artist = Artist.query.filter_by(id=artist_id).first()
    error = False
    try:
        artist.name = update_info["name"]
        artist.genres = update_info.getlist("genres")
        artist.city = update_info["city"]
        artist.state = update_info["state"]
        artist.phone = update_info["phone"]
        artist.website = update_info["website_link"]
        artist.facebook_link = update_info["facebook_link"]
        artist.seeking_venue = update_info.get("seeking_venue", False)
        artist.seeking_description = update_info["seeking_description"]
        artist.image_link = update_info["image_link"]
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
        if not error:
            print("Update successfully")
            flash("Update sucessfully", "success")
        else:
            flash("Something went wrong!", "error")
    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.filter_by(id=venue_id).first()
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    venue_update = request.form
    venue = Venue.query.filter_by(id=venue_id).first()
    error = False
    try:
        venue.name = venue_update["name"]
        venue.genres = venue_update.getlist("genres")
        venue.city = venue_update["city"]
        venue.state = venue_update["state"]
        venue.phone = venue_update["phone"]
        venue.address = venue_update["address"]
        venue.website = venue_update["website_link"]
        venue.facebook_link = venue_update["facebook_link"]
        venue.seeking_talent = venue_update.get("seeking_talent", False)
        venue.seeking_description = venue_update["seeking_description"]
        venue.image_link = venue_update["image_link"]
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
        if not error:
            flash("Updated venue successfully!")
        else:
            flash("Something went wrong when updating venue!", "error")
    return redirect(url_for("show_venue", venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    error = False
    try:
        form_data = request.form
        artist = Artist(
            city=form_data["city"],
            state=form_data["state"],
            name=form_data["name"],
            phone=form_data["phone"],
            image_link=form_data["image_link"],
            genres=form_data.getlist("genres"),
            facebook_link=form_data["facebook_link"],
            website=form_data["website_link"],
            seeking_description=form_data["seeking_description"],
            seeking_venue=bool(form_data.get("seeking_venue", False)),
        )
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if not error:
            print("Artist created successfully!")
        else:
            abort(400)
    # on successful db insert, flash success
    flash("Artist " + request.form["name"] + " was successfully listed!")
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template("pages/home.html")


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    shows = Show.query.all()
    data1 = []
    for show in shows:
        venue = Venue.query.filter_by(id=show.venue_id).first()
        artist = Artist.query.filter_by(id=show.artist_id).first()
        data1.append(
            {
                "venue_id": show.venue_id,
                "venue_name": venue.name,
                "artist_id": show.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": show.start_time.strftime("%Y/%m/%d %H:%M:%S"),
            }
        )
    return render_template("pages/shows.html", shows=data1)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    artist_id = request.form["artist_id"]
    venue_id = request.form["venue_id"]
    start_time = request.form["start_time"]
    error = False
    try:
        show = Show(venue_id=venue_id, artist_id=artist_id, start_time=start_time)
        db.session.add(show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
        if not error:
            flash("Show was successfully listed!")
        else:
            flash("Something went wrong", "error")
    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
