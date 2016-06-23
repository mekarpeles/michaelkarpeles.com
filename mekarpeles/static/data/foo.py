import requests
import json
docs = json.load(open('biblissima.json'))
url = "http://iiif.biblissima.fr/manifests/get_item.php?id="
for i, j in enumerate(docs['manifests']):
    docs['manifests'][i]['@id'] =  requests.get(url + docs['manifests'][i]['_id']).json()['@id']
    del docs['manifests'][i]['_id']
json.dump(docs, open('biblissima2.json', 'w'), indent=4)
