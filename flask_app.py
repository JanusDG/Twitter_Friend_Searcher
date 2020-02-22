from flask import Flask, redirect, render_template, request, url_for
import folium
import urllib.request, urllib.parse, urllib.error
import twurl
import json
import ssl


app = Flask(__name__)
app.config["DEBUG"] = True


comments = []

TWITTER_URL = 'https://api.twitter.com/1.1/friends/list.json'

# # Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("main_page.html", comments=comments)
    comments.clear()
    comments.append(request.form["contents"])

    acct = comments[0]
    url = twurl.augment(TWITTER_URL,
                        {'screen_name': acct, 'count': '200'})

    try:
        with urllib.request.urlopen(url) as url:
            data = json.loads(url.read().decode())
    except urllib.error.HTTPError:
        return render_template("main_page.html", comments=comments)

    data_dict = {}
    with open("/home/JanusDG/mysite/city_coordinates.tsv", "r") as file:
        for line in file.readlines()[1:]:
            items = [item.strip() for item in line.split("\t")]

            data_dict[items[1]] = [float(items[2]), float(items[3])]

    friends_dict = {}

    for i in range(len(data["users"])):
        item = data["users"][i]["location"]
        if "," in item:
            item = [element.strip() for element in item.split(",")][0]

        if item not in data_dict.keys():
            continue
        coordinates = data_dict[item]
        friends_dict[data["users"][i]["name"]] = coordinates


    lat = []
    lon = []
    text = []
    for key, value in friends_dict.items():
        lat.append(value[0])
        lon.append(value[1])
        text.append(key)

    startlocation = [39, 8]

    map = folium.Map(location=startlocation, zoom_start=2)

    nearest_films = folium.FeatureGroup(name="Nearby filmography")

    for lat, lon, text in zip(lat, lon, text):
        nearest_films.add_child(folium.Marker(location=[lat, lon],
                                            popup=text,
                                            icon=folium.Icon()))

    map.add_child(nearest_films)

    map.add_child(folium.LayerControl())
    map.save('/home/JanusDG/mysite/templates/Map.html')


    return redirect(url_for('see_map'))

@app.route("/map", methods=["GET", "POST"])
def see_map():
    return render_template("Map.html")