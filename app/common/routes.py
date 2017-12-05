from flask import Blueprint, render_template

from bokeh.embed import components
from app import getsql, chartfuns


main = Blueprint('main', __name__, url_prefix='')


@main.route("/")
def index():
    return render_template("index.html")

@main.route("/barchart")
#def clientside_table():
#    return render_template("clientside_table.html")
def barchart():
    plot=chartfuns.chart()
    the_script, the_div=components(plot)
    return render_template("barchart.html", script=the_script, div=the_div)
#route to data viz



@main.route("/serverside_table")
def serverside_table():
    return render_template("serverside_table.html")
