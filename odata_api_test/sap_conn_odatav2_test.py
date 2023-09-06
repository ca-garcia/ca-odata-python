
from suds.client import Client as Clients
from zeep import Client as Clientz # Utilizada para peticiones de RFC con caracteres especiales.
import requests
import pyodata
import os
from pyodata.v2.service import Service

from urllib3.exceptions import InsecureRequestWarning
# Suppress the warnings from urllib3
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# https://group00-cld900-d052537.prod.apimanagement.eu10.hana.ondemand.com:443/HelloWorldAPI
# https://cld900-001.test.apimanagement.eu10.hana.ondemand.com:443/HelloWorldAPI

ODATA_VERSION = 2
USER= 'P2007061895'
PASSW= 'Sappass23*'
SERVICE_URL = 'https://sapes5.sapdevcenter.com/sap/opu/odata/iwbep/GWSAMPLE_BASIC/'
API_PROVIDER = 'https://1e3deea0trial-trial.integrationsuitetrial-apim.us10.hana.ondemand.com/1e3deea0trial/GWSAMPLE_BASIC'
SERVICE_URL = API_PROVIDER

SERVICE_URL2 = 'https://405e183a-28de-4d81-92fd-4d082cf16a3f.abap-web.us10.hana.ondemand.com/sap/opu/odata/sap/ZSB_NOTES_HC'
# api_url='https://405e183a-28de-4d81-92fd-4d082cf16a3f.abap-web.us10.hana.ondemand.com/sap/opu/odata/sap/ZAPI_RAP_TRAVEL_CA'
content_type='application/xml'

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

# ODATA V2
def connect_odata_api(url=SERVICE_URL, session=False):
    try:
        if not session:
            session = requests.Session()
            session.verify = False
            session.auth = (USER, PASSW)
        print('Headers:', session.headers, 'Auth:', session.auth)
        client = pyodata.Client(url, session)
        print('Client:', client)
        return client
    except Exception as error:
        print("Ha ocurrido un error al conectarse al servicio ODATA: '%s'" % error)

def get_entity_data(entity, id, expand=False):
    client = connect_odata_api()
    if client:
        if expand:
            entity = getattr(client.entity_sets, entity).get_entity(id).expand(expand).execute()
        else:
            entity = getattr(client.entity_sets, entity).get_entity(id).execute()
        return entity

def get_entities_list(entity, client=False):
    if not client:
        client = connect_odata_api()
    if client:
        entities = getattr(client.entity_sets, entity).get_entities().execute()
        return entities
    return []

def get_product(id=1, expand=False):
    product = get_entity_data('ProductSet', id, expand)
    if expand:
        print('ID', product.ProductID, 'N:', product.Name, 'C:', product.Category, 'S:', product.ToSupplier.BusinessPartnerID + '@' + product.ToSupplier.CompanyName)
        # for prop in product._entity_type._properties:
        #     print(prop, getattr(product, prop))
    else:
        print('ID:', product.ProductID, 'N:', product.Name, 'C:', product.Category)
    return product

def get_products():
    products = get_entities_list('ProductSet')
    for product in products:
        print(product.ProductID, product.Name, product.Price)
    return products

def get_count_products():
    client = connect_odata_api()
    if client:
        count = client.entity_sets.ProductSet.get_entities().count().execute()
        print('Products count:', count)
        return count

def get_products_filtered(filter='Price gt 100', order_by='Price desc', top=10):
    client = connect_odata_api()
    if client:
        products = client.entity_sets.ProductSet.get_entities().filter(filter).order_by(order_by).top(top).execute()
        for product in products:
            print(product.ProductID, product.Name, product.Price)

def create_product(new_data):
    # create session
    session = requests.Session()
    # disable ssl check
    session.verify = False
    # add user and passw auth
    session.auth = (USER, PASSW)
    response = session.head(SERVICE_URL, headers={'x-csrf-token': 'fetch'})
    token = response.headers.get('x-csrf-token', '')
    print('Token:', token)
    session.headers.update({'x-csrf-token': token})
    # connect to odata service
    client = connect_odata_api(SERVICE_URL, session)
    
    # Supplier entity set
    # supplier = client.entity_sets.BusinessPartnerSet.get_entity('0100000046').execute()
    # print('Supplier:', supplier.BusinessPartnerID)
    # new_product = client.entity_sets.ProductSet.get_entities().insert(new_data, Supplier=supplier).execute() # form bing not work
    # create_request = client.entity_sets.ProductSet.new_entity() # from chatgpt not work

    create_request = client.entity_sets.ProductSet.create_entity()
    create_request.set(**new_data)

    # create_request.set(
    #     ProductID= 'TH-9999',
    #     Name= 'Test Prod CA',
    #     TypeCode= 'PR',
    #     Category= 'Notebooks',
    #     TaxTarifCode= 1,
    #     MeasureUnit= 'PC',
    #     CurrencyCode= 'MXN',
    #     Description= 'Test Product creation by CA',
    #     Price= 54000.00,
    #     SupplierID= '0100000046',
    # )

    # new_product.ProductID = 1000
    # new_product.ProductName = 'Bing Soda'
    # new_product.UnitPrice = 1.99
    # new_product.Discontinued = True

    try:
        new_product = create_request.execute()
        print('Product created!', new_product.ProductID)
    except pyodata.exceptions.HttpError as error:
        print("Ha ocurrido un error al crear un nuevo Producto ['%s']" % error)

def update_product(id=1):
    # create session
    session = requests.Session()
    # disable ssl check
    session.verify = False
    # add user and passw auth
    session.auth = (USER, PASSW)
    response = session.head(SERVICE_URL, headers={'x-csrf-token': 'fetch'})
    token = response.headers.get('x-csrf-token', '')
    print('Token:', token)
    session.headers.update({'x-csrf-token': token})
    # connect to odata service
    client = connect_odata_api(SERVICE_URL, session)

    # client = connect_odata_api()
    if client:
        try:
            update_request = client.entity_sets.ProductSet.update_entity(ProductID=id, method='PUT')
            update_request.set(Name='Notebook Basic 15 Custom CA')
            print('Upd request:', update_request)
            res= update_request.execute()
            print('Product updated!', res.ProductID, res.Name)
        except pyodata.exceptions.HttpError as error:
            print("Ha ocurrido un error al actualizar el Producto ['%s']" % error)

def get_url_request():
    client = connect_odata_api()
    if client:
        products_query = client.entity_sets.ProductSet.get_entity(1)
        products_query = client.entity_sets.ProductSet.get_entities().filter("ProductName eq 'Chai'")
        
        create_request = client.entity_sets.ProductSet.create_entity()
        new_product_data = {
            "ProductID": 'New-1001',
            "Name": "New Product",
            "Category": "Electronics",
            "Price": 299.99
        }
        create_request.set(**new_product_data)
        products_query = create_request

        method = products_query.get_method()
        urlpath = products_query.get_path()
        params = products_query.get_query_params()
        body = products_query.get_body()
        url = os.path.join(SERVICE_URL,urlpath)
        print('URL:', method, urlpath, url, params, body)


if __name__ == "__main__":

    # resp = connect_api(api_url + '/Travel')
    # print('----- SAP WEB API -----')
    # print('Response:', resp)
    # print(resp.text)
    # print(resp.headers)

    print('----- SAP ODATA WEB API -----')
    # get_products()
    print('-------------------------')
    get_product('HT-1000','ToSupplier')
    print('-------------------------')
    get_products_filtered(filter='Price gt 60', order_by='Price desc', top=5)
    print('-------------------------')
    get_url_request()
    print('-------------------------')
    get_count_products()
    print('-------------------------')
    new_data = {
        "ProductID": "string",
        "TypeCode": "st",
        "Category": "string",
        "Name": "string",
        "Description": "string",
        "SupplierID": "string",
        "TaxTarifCode": 0,
        "MeasureUnit": "str",
        "WeightMeasure": "0",
        "WeightUnit": "str",
        "CurrencyCode": "strin",
        "Price": "0",
        "Width": "0",
        "Depth": "0",
        "Height": "0",
        "DimUnit": "str",
        # 'ProductID': 'TH-0000',
        # 'Name': 'Test Prod CA',
        # 'TypeCode': 'st',
        # 'Category': 'Notebooks',
        # 'SupplierID': '0100000046',
        # 'TaxTarifCode': 1,
        # 'MeasureUnit': 'PC',
        # 'CurrencyCode': 'MXN',
        # 'Description': 'Test Product creation by CA',
        # 'Price': 54000.00,
        }
    create_product(new_data)
    print('-------------------------')
    update_product('HT-1000')
    print('-------------------------')
    # # get_entity_data('Products')

    # try:
    #     headers = {
    #         'accept' : '*/*'
    #     }
    #     session = requests.Session()
    #     session.verify = False
    #     # session.auth = (USER, PASSW)
    #     session.auth = ('198D90AB9512AFBE97CFA117E339EEHT')
    #     print('Headers:', session.headers, 'Auth:', session.auth)
    #     # print('Headers:', session.headers)
    #     client = pyodata.Client(SERVICE_URL2, session)
    #     print('Client:', client)
    # except Exception as error:
    #     print("Ha ocurrido un error al conectarse al servicio ODATA: '%s'" % error)
