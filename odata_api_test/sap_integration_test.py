
from suds.client import Client as Clients
from zeep import Client as Clientz # Utilizada para peticiones de RFC con caracteres especiales.
import requests
import pyodata
import os
import json
from requests.auth import HTTPBasicAuth

from urllib3.exceptions import InsecureRequestWarning

from sap_conn_odatav2_test import get_product as getProduct
 
# Suppress the warnings from urllib3
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

WEB_API_TEST = 'http://jsonplaceholder.typicode.com/albums'
api_url='https://1e3deea0trial.it-cpitrial05-rt.cfapps.us10-001.hana.ondemand.com/http/'
USER = 'carlosalbertogarcia.b@gmail.com'
PASSW = 'Sappass_23'
content_type='application/xml'

def connect_api(url, string_req, user=USER, password=PASSW, params=False, data=False):
    request = url + string_req
    if params:
        request += f'?{params}'
    response = False
    # headers = {
    #     'accept' : content_type
    # }
    try:
        if data:
            # Send a POST request with JSON data
            # response = requests.post(request, auth=HTTPBasicAuth(user, password), json=data)
            response = requests.get(request, auth=HTTPBasicAuth(user, password), json=data)
        else:
            response = requests.get(request, auth=HTTPBasicAuth(user, password))

        # client_zeep = Clientz(url)
        # client_suds = Clients(url)
        # cli_conn = client_zeep or client_suds or False
        # if cli_conn:
        #     response = cli_conn.service._operations#Consulta(string_req)

    except Exception as error: # suds.transport.TransportError
        print("Ha ocurrido un error al conectarse al servicio API: '%s'" % error)
    return response

if __name__ == "__main__":

    print('----- SAP API INTEGRATION -----')
    # resp = connect_api(api_url, 'products')
    # print(resp.json())
    # # print(resp.text)
    # # print(resp.headers)
    # print('----- DATA -----')
    # for product in resp.json()['ProductSet']['Product']:
    #     print('ID:', product['ProductID'], 'Name:', product['Name'], 'Categ:', product['Category'], 'Supplier:', product['SupplierName'])
    print('----- SINGLE REQUEST -----')
    resp = connect_api(api_url, 'product', params='id=HT-1001')
    try:
        # Try to parse the response as JSON
        json_data = resp.json()
        # If parsing is successful, it's JSON data
        # print("Response is JSON data:")
        print(json.dumps(json_data, indent=2))  # Pretty print the JSON data
        # print(resp.json())

        print('----- DATA -----')
        if 'Product' in resp.json()['ProductSet'].keys() :
            product = resp.json()['ProductSet']['Product']
            print('ID:', product['ProductID'], 'Name:', product['Name'], 'Categ:', product['Category'], 'Supplier:', product['SupplierName'])
            print('----- GET DATA FROM API -----')
            prod_obj_from_api = getProduct(product['ProductID'], expand='ToSupplier')
            data = {
                'ProductID': prod_obj_from_api.ProductID,
                'Price': prod_obj_from_api.Price,
                'BusinessPartnerID': prod_obj_from_api.ToSupplier.BusinessPartnerID,
                'CompanyName': prod_obj_from_api.ToSupplier.CompanyName,
                'WebAddress': prod_obj_from_api.ToSupplier.WebAddress,
            }
            print('JSON:', data)
            print('----- SAVE DATA TO INTEGRATION -----')
            response = connect_api(api_url, 'save', data=data)
            # Handle the response
            print("Response Status Code:", response.status_code)
            print("Response Content:", response.text)
    except json.JSONDecodeError:
        # If parsing fails, it's not JSON data
        # print("Response is not JSON data.")
        print(resp.text)


