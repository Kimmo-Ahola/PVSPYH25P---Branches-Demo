import os
from flask import Flask, render_template, request
from flask_migrate import Migrate
from livereload import Server
from sqlalchemy import asc, desc
from database import db
from models.model import Customer, seedData
from dotenv import load_dotenv
from models.model import seedData

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
environment = os.getenv("FLASK_DEBUG")
db.init_app(app)
migrate = Migrate(app, db)


@app.route("/")
def home():
    sort_by = request.args.get("sort_by", "Id")
    sort_order = request.args.get("sort_order", "asc")
    per_page = request.args.get("per_page", default=50, type=int)
    page = request.args.get("page", default=1, type=int)

    column_map = {
        "Id": Customer.Id,
        "Name": Customer.GivenName,  # optional: concatenate GivenName + Surname if you want
        "Address": Customer.Streetaddress,
        "City": Customer.City,
        "Zipcode": Customer.Zipcode,
        "Country": Customer.Country,
        "Birthday": Customer.Birthday,
        "NationalId": Customer.NationalId,
        "Email": Customer.EmailAddress,
    }

    # Get column object
    sort_column = column_map.get(sort_by, Customer.Id)

    query = db.session.query(Customer)

    if sort_order == "asc":
        query = query.order_by(asc(sort_column))
    elif sort_order == "desc":
        query = query.order_by(desc(sort_column))

    pagination = db.paginate(query, page=page, per_page=per_page)
    return render_template(
        "user/index.html",
        customers=pagination.items,
        pagination=pagination,
        sort_by=sort_by,
        sort_order=sort_order,
        endpoint=request.endpoint
    )


if __name__ == "__main__":

    if os.environ.get("FLASK_DEBUG") == "1":
        with app.app_context():
            # We need the app_context when using the db outside of a request
            seedData(db)
        server = Server(app.wsgi_app)
        server.watch("templates/**/*.html")  # all HTML files recursively
        server.watch("templates/components/*.html")  # or specific subfolder
        server.watch("static/**/*.css")  # watch CSS recursively
        server.watch("static/**/*.js")  # watch JS

        server.serve(open_url_delay=True)
    else:
        app.run()
