import requests
import json
dict_watchlist = {}
new_report_ids = []
iocs_v2_fields_array = []
report_ids_with_issues = []

#CB
#Create a config Json file with the credentials you need as bellow
with open('config_cb.json') as configFile:
    config = json.load(configFile)
    apiKeyOrigin = config['ApiKey_Origin']
    customerIdOrigin = config['customerId_Origin']
    apiKeyDestination = config['ApiKey_Destination']
    customerIdDestination = config['customerId_Destination']
    orgKeyOrigin = config['OrgKey_ORIGIN']
    orgKeyDestination = config['OrgKey_DESTINATION']
    url_cb_origin = config['URL_ORIGIN']
    url_cb_destination = config['URL_DESTINATION']

#CREATE A WATCHLIST ON THE DESTINATION CONSOLE

print(f"Creating a watchlist on the following console: {url_cb_destination}")
url_watchlist = f"{url_cb_destination}/threathunter/watchlistmgr/v3/orgs/{orgKeyDestination}/watchlists"
headers_post = {
            'X-AUTH-TOKEN': f'{apiKeyDestination}/{customerIdDestination}',
            'Content-Type': 'application/json'
         }

payload = json.dumps({
  "name": "NAME EXAMPLE - Watchlist - XXX",
  "description": "DESCRIPTION EXAMPLE",
  "tags_enabled": "true",
  "alerts_enabled": "true",
  "alert_classification_enabled": "true",
 })

response = requests.request("POST", url_watchlist, headers=headers_post, data=payload)
print("Creating the watchlist!\n", response)
if (response.status_code == 200):
    response_data = response.json()
    watchlist_id = response_data["id"]
    print("Watchlist created! ID = ", watchlist_id)
else:
    print("Issue creating the watchlist! \n", response)

#GET THIS VIA POSTMAN (Future improvement needed to do it automatically)
list_of_report_ids = ["XXXXXXXXXXXXXXXXXXXXXXX", "YYYYYYYYYYYYYYYYYYYYY"]

#READ WATCHLIST FROM ORIGIN
for report_id in list_of_report_ids:
    print("Original report ID: ", report_id)
    url_get = f'{url_cb_origin}/threathunter/watchlistmgr/v3/orgs/{orgKeyOrigin}/reports/{report_id}'

    headers_get = {
        'X-AUTH-TOKEN': f'{apiKeyOrigin}/{customerIdOrigin}'
    }

    try:
        response = requests.get(url_get, headers=headers_get)
        #print("Getting the report Id from the Origin Console! Response = ", response)

    except Exception as exc:
        print("Exception on getting the report ID related Data:", Exception)

    if (response.status_code == 200):
        response_data = response.json()

        response_data.pop("id")
        response_data.pop("link")
        response_data.pop("tags")

        response_data.pop("iocs_total_count")

        if ("https://" or "http://") in response_data['description']: response_data['description'] = ""
        else: response_data['description'] = response_data['description'].replace("'", "").replace("\n", " ")

        response_data['iocs_v2'][0]['values'][0] = response_data['iocs_v2'][0]['values'][0].replace("'", "@").replace('"', "@")

        if response_data["visibility"] == None:
            response_data.update({"visibility": "visible"})

        if response_data["iocs"] == None:
            response_data.pop("iocs")
        if response_data["iocs_v2"] == None:
            response_data.pop("iocs_v2")

        iocs_v2_fields = response_data["iocs_v2"][0]
        if iocs_v2_fields["link"] == None:
            iocs_v2_fields.pop("link")
        if iocs_v2_fields["field"] == None:
            iocs_v2_fields.pop("field")

        response_data.update({"iocs_v2":[iocs_v2_fields]})


        payload = str(response_data)
        payload = payload.replace("'", "\"")
        payload = payload.replace("@", "\'")

    # CREATE REPORT ID IN THE DESTINATION
    url_post = f'{url_cb_destination}/threathunter/watchlistmgr/v3/orgs/{orgKeyDestination}/reports'
    headers_post = {
            'X-AUTH-TOKEN': f'{apiKeyDestination}/{customerIdDestination}',
            'Content-Type': 'application/json'
        }

    try:
        response = requests.request("POST", url_post, headers=headers_post, data=payload)
    #print("#####Response to the POST of the payload with the report ID:", response)
    except Exception as exc:
        print("Exception while posting the report ID to the Destination Console! ", response)

    if response.status_code == 200:
        response_data = response.json()
        unique_new_id = response_data["id"]
        print(f"Saving report id {unique_new_id} to the list")
        print("Response:\n", response_data)
        new_report_ids.append(unique_new_id)
    else:
        report_ids_with_issues.append(report_id)

print(">>>>New report ids - sucess = ", new_report_ids)
print(">>>>Old report ids with issues = ", report_ids_with_issues)

###########################################################################
#SEND TO THE NEW WATCHLIST THE REPORT ID'S ALREADY ON THE CONSOLE
headers_post = {
            'X-AUTH-TOKEN': f'{apiKeyDestination}/{customerIdDestination}',
            'Content-Type': 'application/json'
        }
url_watchlist_put = f"{url_cb_destination}/threathunter/watchlistmgr/v3/orgs/{orgKeyDestination}/watchlists/{watchlist_id}"
print("Updating the following Console/Watchlist: ", url_watchlist_put)


payload = json.dumps({
    "name": "NAME EXAMPLE - Watchlist - XXX",
    "report_ids": new_report_ids
    })
print(payload)
response = requests.request("PUT", url_watchlist_put, headers=headers_post, data=payload)

print("Adding report IDs to the watchlist!\n", response)
if (response.status_code == 200):
    response_data = response.json()
    print("Status 200!\n", response_data)
else:
    print("Check the status code!")
