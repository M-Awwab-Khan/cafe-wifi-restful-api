from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random


app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route('/random')
def random_cafe():
    with app.app_context():
        # cafes = Cafe.query.all()
        result = db.session.execute(db.select(Cafe))
        cafes = result.scalars().all()
        cafe = random.choice(cafes)

        return jsonify(cafe=cafe.to_dict())

@app.route('/all')
def all():
    with app.app_context():
        cafes = db.session.execute(db.select(Cafe)).scalars().all()
        all_cafes = [cafe.to_dict() for cafe in cafes]
        return jsonify(all_cafes)

@app.route('/search')
def search():
    location = request.args.get('location')
    with app.app_context():
        cafes = db.session.execute(db.select(Cafe).where(Cafe.location==location)).scalars().all()
        all_cafes = [cafe.to_dict() for cafe in cafes]
        if all_cafes:
            return jsonify(all_cafes)
        else:
            return jsonify(
                error={
                    "Not Found": "Sorry, we don't have a coffee at that location."
                }
            )


# HTTP POST - Create Record

@app.route('/add', methods=['POST'])
def add():
    new_cafe = Cafe(
        name=request.args.get('name'),
        map_url=request.args.get('map_url'),
        img_url = request.args.get('img_url'),
        location = request.args.get('location'),
        seats = request.args.get('seats'),
        has_toilet = request.args.get('has_toilet'),
        has_wifi = request.args.get('has_wifi'),
        has_sockets = request.args.get('has_sockets'),
        can_take_calls = request.args.get('can_take_calls'),
        coffee_price = request.args.get('coffee_price')
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(
        response = {
            "success": "Successfully added the new cafe."
        }
    )

# HTTP PUT/PATCH - Update Record

@app.route('/update-price/<int:id>', methods=['PATCH'])
def update_price(id):
    cafe = db.get_or_404(Cafe, id)
    if cafe:
        cafe.coffee_price = request.args.get('new_price')
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."})
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."})


# HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
