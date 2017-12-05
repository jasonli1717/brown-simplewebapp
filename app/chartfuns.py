from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from app import getsql

#function to return the count of articles per year in a ColumnDataSource (dictionary) for chart()
def countsOfYears():
    #results = []
    paperdict = getsql.getSQLThing()
    results = [entry['year'] for entry in paperdict]
    results_with_yrs=[x for x in results if x != 1900] #removes entries that didn't have a publication date
    yeartup = [(x, results_with_yrs.count(x)) for x in set(results_with_yrs)]
    
    unzipped_years = zip(*yeartup)
    d = {}
    d["x"] = unzipped_years[0]
    d["y"] = unzipped_years[1]

    return d

# function where you can modify the Bokeh figure parameters
def chart():
    #source = ColumnDataSource(data={
    #    'x' : [1, 2, 3, 4, 5],
    #    'y' : [3, 7, 8, 5, 1],
    #})

    source = ColumnDataSource(data=countsOfYears())

    p = figure(plot_width=400, plot_height=400)
    #p.circle('x', 'y', size=20, source=source)
    p.vbar(x='x', width=0.5, bottom=0,
           top='y', color="navy", source=source)

    return p