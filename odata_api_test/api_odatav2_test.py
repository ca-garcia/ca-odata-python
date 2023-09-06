
from suds.client import Client as Clients
from zeep import Client as Clientz # Utilizada para peticiones de RFC con caracteres especiales.
import requests
import pyodata
import os

from urllib3.exceptions import InsecureRequestWarning
 
# Suppress the warnings from urllib3
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

ODATA_VERSION = 2
WEB_API_TEST = 'http://jsonplaceholder.typicode.com/albums'
api_url='https://405e183a-28de-4d81-92fd-4d082cf16a3f.abap-web.us10.hana.ondemand.com/sap/opu/odata/sap/ZAPI_RAP_TRAVEL_CA'
content_type='application/xml'

SERVICE_URL = 'https://services.odata.org/V2/Northwind/Northwind.svc/'

def connect_api(url, string_req=False):
    response = False
    headers = {
        'accept' : content_type
    }
    try:
        response = requests.get(url, headers=headers)

        client_zeep = Clientz(url)
        client_suds = Clients(url)
        cli_conn = client_zeep or client_suds or False
        if cli_conn:
            response = cli_conn.service._operations#Consulta(string_req)

    except Exception as error: # suds.transport.TransportError
        print("Ha ocurrido un error al conectarse al servicio API: '%s'" % error)
    return response

# ODATA
def connect_odata_api(url=SERVICE_URL, session=False):
    try:
        # with requests.Session() as session:
        #     session.get(SERVICE_URL, verify=False)
        
        # req = requests.get(SERVICE_URL, verify=False)
        # print('req: ')
        # print(req)
        # client = pyodata.Client(SERVICE_URL, req)
        # client = pyodata.Client(SERVICE_URL, requests.get("https://services.odata.org/V2/Northwind/Northwind.svc/", verify=False))

        if not session:
            session = requests.Session()
            session.verify = False
        client = pyodata.Client(url, session)

        # print(client)
        return client
    except Exception as error:
        print("Ha ocurrido un error al conectarse al servicio ODATA: '%s'" % error)

def get_product(id=1, expand='Category, Supplier'):
    client = connect_odata_api(SERVICE_URL)
    if client:
        # product = client.entity_sets.Products.get_entity(id).execute()
        product = get_entity_data('Products', id, expand)
        if expand:
            # nav_prop = getattr(client.entity_sets, expand)
            print(product.ProductID, product.ProductName, product.Category.CategoryName, product.Supplier.CompanyName)
            # for prop in product._entity_type._properties:
            #     print(prop, getattr(product, prop))
        else:
            print(product.ProductID, product.ProductName)

def get_products():
    client = connect_odata_api(SERVICE_URL)
    if client:
        # products = client.entity_sets.Products.get_entities().execute()
        products = get_entities_list('Products')
        for product in products:
            print(product.ProductID, product.ProductName, product.UnitPrice)

def get_products_filtered(filter='UnitPrice gt 100', order_by='UnitPrice desc', top=10):
    client = connect_odata_api(SERVICE_URL)
    if client:
        products = client.entity_sets.Products.get_entities().filter(filter).order_by(order_by).top(top).execute()
        for product in products:
            print(product.ProductID, product.ProductName, product.UnitPrice)

def create_product():
    session = requests.Session()
    session.verify = False
    response = session.head(SERVICE_URL, headers={'x-csrf-token': 'fetch'})
    token = response.headers.get('x-csrf-token', '')
    print('Token:', token)
    session.headers.update({'x-csrf-token': token})
    
    client = connect_odata_api(SERVICE_URL, session)

    new_data = {
        'ProductID': 1000,
        'ProductName': 'Test Prod',
        'Discontinued': False,
        # 'Address': {
        # 'HouseNumber': 42,
        # 'Street': 'Paradise',
        # 'City': 'Heaven'
        # }
        }
    try:
        create_request = client.entity_sets.Products.create_entity()
        create_request.set(**new_data)

        # new_product.ProductID = 1000
        # new_product.ProductName = 'Bing Soda'
        # new_product.UnitPrice = 1.99
        # new_product.Discontinued = True

        create_request.execute()
        print('Product created!', create_request.ProductID)
    except pyodata.exceptions.HttpError as error:
        print("Ha ocurrido un error al crear un nuevo Producto ['%s']" % error)

def update_product(id=1):
    client = connect_odata_api(SERVICE_URL)
    if client:
        try:
            update_request = client.entity_sets.Products.update_entity(ProductID=id, method='PUT')
            update_request.set(ProductName='Clara Chia')
            update_request.execute()
            print('Product updated!', update_request.ProductID, update_request.ProductName)
        except pyodata.exceptions.HttpError as error:
            print("Ha ocurrido un error al actualizar el Producto ['%s']" % error)

def get_url_request():
    client = connect_odata_api(SERVICE_URL)
    if client:
        products_query = client.entity_sets.Products.get_entity(1)
        products_query = client.entity_sets.Products.get_entities().filter("ProductName eq 'Chai'")

        urlpath = products_query.get_path()
        params = products_query.get_query_params()
        method = products_query.get_method()
        body = products_query.get_body()
        url = os.path.join(SERVICE_URL,urlpath)
        print(method, urlpath, url, params, body)

def get_entity_data(entity, id, expand=False):
    client = connect_odata_api(SERVICE_URL)
    if client:
        if expand:
            entity = getattr(client.entity_sets, entity).get_entity(id).expand(expand).execute()
        else:
            entity = getattr(client.entity_sets, entity).get_entity(id).execute()
        return entity

def get_entities_list(entity):
    client = connect_odata_api()
    if client:
        entities = getattr(client.entity_sets, entity).get_entities().execute()
        return entities

if __name__ == "__main__":

    resp = connect_api(api_url + '/Travel')
    print('----- SAP WEB API -----')
    print(resp)
    # print(resp.text)
    # print(resp.headers)

    print('----- WEB API -----')
    # response = requests.get(WEB_API_TEST)#all
    response = requests.get(WEB_API_TEST + '/100')#all
    print(response.json())

    print('----- ODATA WEB API -----')
    get_products()
    print('-------------------------')
    get_products_filtered(filter='UnitPrice gt 60', order_by='UnitPrice asc', top=5)
    print('-------------------------')
    create_product()
    print('-------------------------')
    update_product()
    print('-------------------------')
    # get_products()
    print('-------------------------')
    get_url_request()
    print('-------------------------')
    # get_entity_data('Products')
    get_product()
    print('-------------------------')
