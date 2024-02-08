from flask import Flask, jsonify, request
import random
import string

app = Flask(__name__)

active_connections = {}

def generate_connection_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

@app.route('/get_connection_code', methods=['POST'])
def get_connection_code():
    connection_code = generate_connection_code()
    active_connections[connection_code] = request.remote_addr
    return jsonify({'connection_code': connection_code})

@app.route('/get_server_ip', methods=['GET'])
def get_server_ip():
    return jsonify({'server_ip': request.host})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

