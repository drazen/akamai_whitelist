import os
import requests
from akamai.edgegrid import EdgeGridAuth, EdgeRc
import json
from jsonpath_ng.ext import parse

# Upsert the provided IP into the CDN whitelist
def upsert_ip(event, context):

    # TODO wire this up in some TBD event source...
    ip_address = event['Records'][0]['ip_address']
    contract_id = event['Records'][0]['contract_id']
    group_id = event['Records'][0]['group_id']

    # Surgically add/replace the IP to whitelist in the ruletree and update the entire
    # Ruletree in Akamai.  Ideally we would use JSON-PATCH to only update the portion we need
    # but Akamai Sandbox API does not support this.  We'd be forced to dev/test on the Staging
    # CDN... Doable but not worth the effort/risk.   PUT of the whole ruletree document we can
    # test in the Sandbox during development and its good enough.

    session = requests.Session()
    session.auth = EdgeGridAuth(client_token = os.environ['AKAMAI_API_CLIENT_TOKEN'],
        client_secret = os.environ['AKAMAI_API_CLIENT_SECRET'],
        access_token = os.environ['AKAMAI_API_ACCESS_TOKEN'])

    # Retrieve the current rule tree JSON document.
    # TODO - change versions... to always get latest... look up how
    rules_doc = session.get(os.environ['AKAMAI_API_URL'] +
        '/papi/v1/properties/{property}/versions/1/rules?contractId={contract_id}?groupId={group_id}')

    # Get the full path to the UNIQUE nested whitelist JSON fragment using JSON Path query
    query = parse('rules.children[?(@.name == "Deny by IP")].criteria[?(@.name == "clientIp")]').options.values
    path_to_whitelist = str(query.find(rules_doc)[0].full_path)

    # Convert JSONPath to JSON Pointer format used by JSONPatch

    # # Patch the whitelist with specified IP address
    # session.body = patch #formatted to AKA format
    # session.patch(os.environ['AKAMAI_API_URL'] +
    #     '/papi/v1/properties/{property}/versions/1/rules)

    # FIXME for now as a test... patch the JSON document locally and print it out...

    
    # Update the ruletree in the CDN

    # Activate the modified ruletree

    return {
        "statusCode": 200,
        "body": json.dumps(data)
    }