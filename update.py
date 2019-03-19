import json
import requests


def lambda_wrapper(event, context):
    users = [('Alan', 100011),
             ('Andrew', 54647),
             ('Niall', 1601)]
    html = _get_header(users) + _get_data(users) + _get_footer(users)
    _storeHtml(html)


def _get_header(users):
    return '''<!DOCTYPE html>
    <html lang="en">
      <head>
        <title>Munro Aggregator</title>
        <meta name="viewport" content="initial-scale=1.0">
        <meta charset="utf-8">
        <style>
          #map {
            height: 100%;
          }
          html, body {
            height: 100%;
            margin: 0;
            padding: 0;
          }
        </style>
          <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
          <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>
      </head>
      <body>
        <div id="map"></div>
        <div class="panel panel-default" style="max-height:100vh; width:15vw; overflow:auto; position:absolute; top:10px; right:10px; z-index:1000">
          <div class="panel-body">
              <b>Exclude Munros climbed by:</b><br />
              <input id="Alan" type="checkbox" checked onchange="hideAsRequired()"> Alan<br />
              <input id="Andrew" type="checkbox" checked onchange="hideAsRequired()"> Andrew<br />
              <input id="Niall" type="checkbox" checked onchange="hideAsRequired()"> Niall
          </div>
        </div>
        <script>
      hills = '''


def _get_data(users):
    hills = _grab_all_hills()
    for name, uid in users:
        usersHasClimbed = _grab_hills_for(uid)
        for hill in hills:
            hill[name] = usersHasClimbed[hill['name']]
    return json.dumps(hills)


def _grab_all_hills():
    resp = requests.get('https://www.walkhighlands.co.uk/Forum/memberlist.php?mode=viewmap')
    all = []
    for line in resp.text.splitlines():
        if 'latlng =' in line:
            lanlng = line.split('[')[1].split(']')[0]
        if 'marker2' in line:
            all.append({'name': line.split(',')[5].replace('"', ''),
                        'lat': float(lanlng.split(',')[0]),
                        'lng': float(lanlng.split(',')[1])})
    return all


def _grab_hills_for(user_id):
    resp = requests.get('https://www.walkhighlands.co.uk/Forum/memberlist.php?mode=viewmap&u={}'.format(user_id))
    return {line.split(',')[5].replace('"', ''): 'blueIcon' in line for line in resp.text.splitlines() if
            'marker2' in line}


def _get_footer(users):
    #
        return '''
      markers = {}

      function hideAsRequired() {
        allUsers = ['Alan','Andrew','Niall']
        for (var i = 0; i < hills.length; i++) {
          var visible = true;
          for (var j=0;j<allUsers.length; j++) {
            if ( document.getElementById(allUsers[j]).checked && hills[i][allUsers[j]] == true ) {
              visible = false
            }
          }
          markers[ hills[i]['name'] ].setVisible( visible )
        }
      }
      var map;
      function initMap() {
        map = new google.maps.Map(document.getElementById('map'), {
          center: {lat: 57.3, lng: -5},
          zoom: 8,
          fullscreenControl: false
        });
        map.setMapTypeId('terrain');
        for (var i = 0; i < hills.length; i++) {
          var myLatLng = {lat: hills[i]['lat'], lng: hills[i]['lng']};
          var marker = new google.maps.Marker({
            position: myLatLng,
            map: map,
            title: hills[i]['name']
          });
          markers[ hills[i]['name'] ] = marker
        }
        hideAsRequired();
      }
        </script>
        <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBO7ta8WEyt4o7hC2aEEoN2pGF7IgN48Lg&callback=initMap"
        async defer></script>
      </body>
    </html>'''


def _storeHtml(html):
    import boto3
    s3 = boto3.resource('s3')
    s3.Object('bikerid.es', 'munros/index.html').put(Body=json.dumps(html), ContentType='text/html')
s