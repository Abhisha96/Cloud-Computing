from flask import Flask, request, jsonify
import pymysql  # For MySQL
import redis  # For Redis

app = Flask(__name__)

# MySQL Connection Configuration
mysql_host = "your_mysql_host"
mysql_user = "your_mysql_username"
mysql_password = "your_mysql_password"
mysql_db = "your_mysql_db_name"

# Redis Connection Configuration
redis_host = "54.243.7.50"
redis_port = 6379  # Default Redis port

# MySQL Connection
def connect_to_mysql():
    return pymysql.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password,
        db=mysql_db,
        cursorclass=pymysql.cursors.DictCursor
    )

# Redis Connection
def connect_to_redis():
    return redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

@app.route('/store-products', methods=['POST'])
def store_products():
    data = request.json
    if 'products' in data:
        products = data['products']
        try:
            conn = connect_to_mysql()
            with conn.cursor() as cursor:
                for product in products:
                    name = product.get('name')
                    price = product.get('price')
                    availability = product.get('availability')

                    # Insert data into MySQL products table
                    sql = "INSERT INTO products (name, price, availability) VALUES (%s, %s, %s)"
                    cursor.execute(sql, (name, price, availability))
                conn.commit()
                conn.close()

                return jsonify({"message": "Success."}), 200
        except Exception as e:
            return str(e), 500  # Modify error handling as needed
    else:
        return "Invalid input", 400

@app.route('/list-products', methods=['GET'])
def list_products():
    try:
        conn = connect_to_mysql()
        with conn.cursor() as cursor:
            # Query products from MySQL
            cursor.execute("SELECT * FROM products")
            products = cursor.fetchall()
            conn.close()

            # Store products in Redis
            r = connect_to_redis()
            r.set('products_data', str(products))

            return jsonify({
                "products": products,
                "cache": "true"  # Indicates products are retrieved from Redis
            }), 200
    except Exception as e:
        return str(e), 500  # Modify error handling as needed

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Modify host and port as needed
