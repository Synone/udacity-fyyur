# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import datetime

app = Flask(__name__)
moment = Moment(app)
app.config.from_object("config")
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=False)


class Venue(db.Model):
    __tablename__ = "venue"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.String(5), nullable=True)
    seeking_description = db.Column(db.String(500))
    genres = db.Column(db.String(120))
    shows = db.relationship("Show", backref="venue")

    def __repr__(self):
        return f"<Venue: {self.id}, name: {self.name}>"


class Artist(db.Model):
    __tablename__ = "artist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    website = db.Column(db.String(120))
    shows = db.relationship(
        "Show",
        backref="artist",
    )

    def __repr__(self):
        return f"<Artist: {self.id}, name: {self.name}>"


class Show(db.Model):
    __tablename__ = "show"
    title = db.Column(db.String(200))
    venue_id = db.Column(
        db.Integer, db.ForeignKey("venue.id"), nullable=False, primary_key=True
    )
    artist_id = db.Column(
        db.Integer, db.ForeignKey("artist.id"), nullable=False, primary_key=True
    )
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())

    def __repr__(self):
        return f"<VenueID: {self.venue_id} - ArtistId: {self.artist_id}>"


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
