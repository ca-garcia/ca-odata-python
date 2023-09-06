
from suds.client import Client as Clients
from zeep import Client as Clientz # Utilizada para peticiones de RFC con caracteres especiales.
import requests
import pyodata
import os

from urllib3.exceptions import InsecureRequestWarning
 
# Suppress the warnings from urllib3
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

ODATA_VERSION = 4
# content_type='application/xml'
# SERVICE_URL1 = 'https://services.odata.org/V2/Northwind/Northwind.svc/'
SERVICE_URL1 = 'https://services.odata.org/V4/TripPinServiceRW/'
# SERVICE_URL0 = 'https://services.odata.org/V4/(S(2hrx0cuofhzotg1vopidr11w))/TripPinServiceRW/'
SERVICE_URL2 = 'https://services.odata.org/V3/OData/OData.svc'

# ODATA
def connect_odata_api(url=SERVICE_URL1, session=False):
    try:
        if not session:
            session = requests.Session()
            session.verify = False
        client = pyodata.Client(url, session, odata_version=4)

        print(client)
        return client
    except Exception as error:
        print("Ha ocurrido un error al conectarse al servicio ODATA: '%s'" % error)

def get_entity_data(entity, id=1):
    client = connect_odata_api()
    if client:
        # entity = getattr(client.entity_sets, entity).get_entity(id).execute()
        entity = client.entity_sets.Persons.get_entity(id).execute()
        print(entity.ID, entity.Name)

# def get_products():
#     client = connect_odata_api(SERVICE_URL)
#     if client:
#         products = client.entity_sets.Products.get_entities().execute()
#         for product in products:
#             print(product.ProductID, product.ProductName, product.UnitPrice)

# def get_products_filtered(filter='UnitPrice gt 100', order_by='UnitPrice desc', top=10):
#     client = connect_odata_api(SERVICE_URL)
#     if client:
#         products = client.entity_sets.Products.get_entities().filter(filter).order_by(order_by).top(top).execute()
#         for product in products:
#             print(product.ProductID, product.ProductName, product.UnitPrice)

# def create_product():
#     session = requests.Session()
#     session.verify = False
#     response = session.head(SERVICE_URL, headers={'x-csrf-token': 'fetch'})
#     token = response.headers.get('x-csrf-token', '')
#     print('Token:', token)
#     session.headers.update({'x-csrf-token': token})
    
#     client = connect_odata_api(SERVICE_URL, session)

#     new_data = {
#         'ProductID': 1000,
#         'ProductName': 'Test Prod',
#         'Discontinued': False,
#         # 'Address': {
#         # 'HouseNumber': 42,
#         # 'Street': 'Paradise',
#         # 'City': 'Heaven'
#         # }
#         }
#     try:
#         create_request = client.entity_sets.Products.create_entity()
#         create_request.set(**new_data)

#         # new_product.ProductID = 1000
#         # new_product.ProductName = 'Bing Soda'
#         # new_product.UnitPrice = 1.99
#         # new_product.Discontinued = True

#         create_request.execute()
#         print('Product created!', create_request.ProductID)
#     except pyodata.exceptions.HttpError as error:
#         print("Ha ocurrido un error al crear un nuevo Producto ['%s']" % error)

# def update_product(id=1):
#     client = connect_odata_api(SERVICE_URL)
#     if client:
#         try:
#             update_request = client.entity_sets.Products.update_entity(ProductID=id, method='PUT')
#             update_request.set(ProductName='Clara Chia')
#             update_request.execute()
#             print('Product updated!', update_request.ProductID, update_request.ProductName)
#         except pyodata.exceptions.HttpError as error:
#             print("Ha ocurrido un error al actualizar el Producto ['%s']" % error)

# def get_url_request():
#     client = connect_odata_api(SERVICE_URL)
#     if client:
#         products_query = client.entity_sets.Products.get_entity(1)
#         products_query = client.entity_sets.Products.get_entities().filter("ProductName eq 'Chai'")

#         urlpath = products_query.get_path()
#         params = products_query.get_query_params()
#         method = products_query.get_method()
#         body = products_query.get_body()
#         url = os.path.join(SERVICE_URL,urlpath)
#         print(method, urlpath, url, params, body)



if __name__ == "__main__":

    print('----- ODATA WEB API -----')
    get_entity_data('Persons')
    print('-------------------------')
    # get_products()
    # print('-------------------------')
    # get_products_filtered(filter='UnitPrice gt 60', order_by='UnitPrice asc', top=5)
    # print('-------------------------')
    # create_product()
    # print('-------------------------')
    # update_product()
    # print('-------------------------')
    # # get_products()
    # print('-------------------------')
    # get_url_request()
