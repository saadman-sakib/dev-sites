from flask import Flask, render_template, request, Response, jsonify
import requests
import json
import os

app = Flask(__name__)

navlist = [{"name": "Home", "link": "/"}, {"name": "About", "link": "/about"}]
# devlist = [
#     {"name": "Arban Hossain", "profile": "https://github.com/arbanhossain"},
#     {"name": "Nabil", "profile": "https://github.com/nirobnabil"}
# ]

@app.route("/")
def index():
    response = requests.get(os.environ['SHEETY_API'])
    return render_template('home.html', title="Home", nav_list=navlist, dev_list=response.json()['devsite'])

@app.route("/about")
def about():
    return render_template('about.html', title="About", nav_list=navlist)

@app.route("/fetch")
def fetch():
    if request.args.get('pass') != os.environ['passwd']:
        print(request.args.get('pass'))
        return Response(status=403)
    trending_devs = requests.get('https://gh-trending-api.herokuapp.com/developers')
    existing_devs = requests.get(os.environ['SHEETY_API'])
    for item in trending_devs.json():
        dev = item['username']
        if dev not in [i['handle'] for i in existing_devs.json()['devsite']]:
            dev_details = requests.get('https://api.github.com/users/' + dev)
            if 'message' in dev_details.json():
                return Response(dev_details.json()['message'], status=500)
            if dev_details.json()['blog'] == '': pass
            else:
                dic = {}
                dic['name'] = dev_details.json()['name']
                dic['site'] = 'https://' + dev_details.json()['blog'] if (dev_details.json()['blog'].count('https://') == 0 and dev_details.json()['blog'].count('http://')==0) else dev_details.json()['blog']
                dic['profile'] = dev_details.json()['html_url']
                dic['handle'] = dev
                post_response = requests.post(os.environ['SHEETY_API'], data=json.dumps({'devsite': dic}), headers={'Content-type': 'application/json'})
                print(post_response.json())
    return Response(status=200)

@app.route("/environ")
def environ():
    return 'No environ'

if __name__ == "__main__":
    app.run()