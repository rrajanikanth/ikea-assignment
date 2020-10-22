import logging
from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster, BatchStatement
from cassandra.query import SimpleStatement
import collections
import json
import flask
from flask import request, jsonify, abort

class PythonCassandraExample:

    def __init__(self):
        self.cluster = None
        self.session = None
        self.keyspace = None
        self.log = None

    def __del__(self):
        self.cluster.shutdown()

    def createsession(self):
        self.cluster = Cluster(['localhost'])
        self.session = self.cluster.connect(self.keyspace)
        self.session.set_keyspace('ikea')

    def getsession(self):
        return self.session

    # How about Adding some log info to see what went wrong
    def setlogger(self):
        log = logging.getLogger()
        log.setLevel('INFO')
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        log.addHandler(handler)
        self.log = log

    def create_tables(self):
        c_sql1 = """
                CREATE TABLE IF NOT EXISTS INVENTORY (art_id int, name varchar, stock int, primary key(name,art_id));
                 """
        c_sql2 = """
                CREATE TABLE IF NOT EXISTS PRODUCTS (name varchar,art_id int,amount_of int, primary key(name,art_id));
                 """
        self.session.execute(c_sql1)
        self.session.execute(c_sql2)
        self.log.info("Tables are Created !!!")

    # lets do some batch insert
    def insert_data(self):
        insert_sql = self.session.prepare("INSERT INTO  employee (emp_id, ename , sal,city) VALUES (?,?,?,?)")
        batch = BatchStatement()
        batch.add(insert_sql, (5, 'Rajani', 2500, 'AMS'))
        batch.add(insert_sql, (6, 'RK', 3000, 'nld'))
        self.session.execute(batch)
        self.log.info('Batch Insert Completed')

    def select_data(self):
        rows = self.session.execute('select * from employee limit 10;')
        for row in rows:
            print(row.ename, row.sal)
    def update_data(self):
        self.session.execute('update employee set sal=4000 where emp_id=5;')


    def delete_data(self):
        self.session.execute('delete * from employee where emp_id=6;')



app = flask.Flask(__name__)
app.config["DEBUG"] = True


#### This is shown in home screen

@app.route('/', methods=['GET'])
def home():
    return '''<h1>API assingment from IKEA </h1>
<p>A prototype API for Inventory demonstration.</p>'''

#### Returns all the inventory in JSON format

@app.route('/api/v1/resources/inventory/all', methods=['GET'])
def inventory_all():
    example1 = PythonCassandraExample()
    example1.createsession()
    rows = example1.session.execute('select * from inventory;')

    # Convert query to objects of key-value pairs
    objects_list = []
    for row in rows:
        d = collections.OrderedDict()
        d["name"] = row[0]
        d["art_id"] = row[1]
        d["stock"] = row[2]
        objects_list.append(d)

    j = json.dumps(objects_list)
    print(j)
    return jsonify(j)


#### Returns all the products in JSON format

@app.route('/api/v1/resources/products/all', methods=['GET'])
def products_all():
    example1 = PythonCassandraExample()
    example1.createsession()
    rows = example1.session.execute('select * from products;')

    # Convert query to objects of key-value pairs
    objects_list = []
    for row in rows:
        d = collections.OrderedDict()
        d["name"] = row[0]
        d["art_id"] = row[1]
        d["amount_of"] = row[2]
        objects_list.append(d)

    j = json.dumps(objects_list)
    print(j)
    return jsonify(j)
#### Page not found handling for Exceptional cases

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@app.route('/api/v1/resources/products/create', methods=['PUT'])
def create_products():
    record = json.loads(request.data)
    print(record)
    example1 = PythonCassandraExample()
    example1.createsession()
    prd_ins_sql = example1.session.prepare("INSERT INTO  products(name, art_id, amount_of ) VALUES (?,?,?)")
    batch = BatchStatement()

    for i in record['products']:
        name = i['name']
        print(name)
        for a in i['contain_articles']:
            art_id = a['art_id']
            amount_of = a['amount_of']
            print(art_id)
            print(amount_of)
            batch.add(prd_ins_sql, (name,int(art_id), int(amount_of)))
            example1.session.execute(batch)

    return jsonify(record)






@app.route('/api/v1/resources/products/update', methods=['POST'])
def update_products():
    record = json.loads(request.data)
    print(record)
    example1 = PythonCassandraExample()
    example1.createsession()
    update_sql = example1.session.prepare("UPDATE PRODUCTS SET  AMOUNT_OF = ? WHERE NAME = ? AND ART_ID = ?")
    batch = BatchStatement()

    for  i in record['products']:
        name = i['name']
        print(name)
        for a in i['contain_articles']:
            art_id = a['art_id']
            amount_of = a['amount_of']
            print(art_id)
            print(amount_of)
            batch.add(update_sql, (int(amount_of), name, int(art_id)))
            example1.session.execute(batch)

    return jsonify(record)


@app.route('/api/v1/resources/products/delete', methods=['DELETE'])
def delte_products():
    record = json.loads(request.data)
    print(record)
    example1 = PythonCassandraExample()
    example1.createsession()
    del_sql = example1.session.prepare("DELETE FROM PRODUCTS WHERE NAME = ? AND ART_ID = ?")
    batch = BatchStatement()

    for  i in record['products']:
        name = i['name']
        print(name)
        for a in i['contain_articles']:
            art_id = a['art_id']
            amount_of = a['amount_of']
            print(art_id)
            print(amount_of)
            batch.add(del_sql, (name, int(art_id)))
            example1.session.execute(batch)

    return jsonify(record)


@app.route('/api/v1/resources/inventory/create', methods=['PUT'])
def create_inventory():
    record = json.loads(request.data)
    print(record)
    example1 = PythonCassandraExample()
    example1.createsession()
    prd_ins_sql = example1.session.prepare("INSERT INTO  inventory(art_id, name, stock ) VALUES (?,?,?)")
    batch = BatchStatement()

    for i in record['inventory']:
        art_id = i['art_id']
        name = i['name']
        stock = i['stock']
        print(art_id)
        print(name)
        print(stock)
        batch.add(prd_ins_sql, (int(art_id), name, int(stock)))
        example1.session.execute(batch)
    return jsonify(record)

@app.route('/api/v1/resources/inventory/update', methods=['POST'])
def update_inventory():
    record = json.loads(request.data)
    print(record)
    example1 = PythonCassandraExample()
    example1.createsession()
    update_sql = example1.session.prepare("UPDATE INVENTORY SET  STOCK = ? WHERE NAME = ? AND ART_ID = ?")
    batch = BatchStatement()

    for i in record['inventory']:
        art_id = i['art_id']
        name = i['name']
        stock = i['stock']
        print(art_id)
        print(name)
        print(stock)
        batch.add(update_sql, (int(stock), name, int(art_id)))
        example1.session.execute(batch)

    return jsonify(record)

@app.route('/api/v1/resources/inventory/delete', methods=['DELETE'])
def delte_inventory():
    record = json.loads(request.data)
    print(record)
    example1 = PythonCassandraExample()
    example1.createsession()
    del_sql = example1.session.prepare("DELETE FROM INVENTORY WHERE NAME = ? AND ART_ID = ?")
    batch = BatchStatement()

    for i in record['inventory']:
        art_id = i['art_id']
        name = i['name']
        stock = i['stock']
        print(art_id)
        print(name)
        print(stock)
        batch.add(del_sql, (name, int(art_id)))
        example1.session.execute(batch)

    return jsonify(record)

if __name__ == '__main__':
    example1 = PythonCassandraExample()
    example1.createsession()
    example1.setlogger()
    example1.create_tables()
    app.run()
