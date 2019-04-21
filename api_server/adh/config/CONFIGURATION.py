# API server options general
API_CONF = {
    'AUTH_SERVER_ADDRESS': 'https://adh6.minet.net/oauth',
    'APPLICATION_ROOT': '/api',
}
                              
# Permanent database, used to store every object
# PROD_DATABASE = {
#     'drivername': '',  # if using MySQL: 'mysql+mysqldb'
#     'host': '',
#     'port': '',
#     'username': '',
#     'password': '',
#     'database': ''
# }
PROD_DATABASE = {
    'drivername': 'sqlite',
    'database': ':memory:',
}

# Temporary database, that will be clear at every test, used when you launch
# the unit tests. Default settings is in RAM memory.
TEST_DATABASE = {
    'drivername': 'sqlite',
    'database': ':memory:',
}

# Prices for cotisations. If you plan to modify these you will have to modify
# here and in the frontend. It should probably go into its own SQL table, but
# meh... At least you have to take a look at how ADH works :D
PRICES = {
    1: 1, # 1 day = 1 euros
    360: 100, # 360 days = 100 euros
}

# IPs and ports for Elasticsearch nodes
ELK_HOSTS = [
    {'host': '127.0.0.1', 'port': 9200},
    {'host': '192.168.1.1', 'port': 9200},
]