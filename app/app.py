from flask import Flask, jsonify
import os
import socket
from datetime import datetime

app = Flask(__name__)

BUILD_DATE = os.environ.get('BUILD_DATE', 'unknown')
VCS_REF = os.environ.get('VCS_REF', 'unknown')
VERSION = os.environ.get('VERSION', '1.0.0')

@app.route('/')
def hello_world():
    return jsonify({
        'message': 'Bye bye CI/CD!',
        'hostname': socket.gethostname(),
        'timestamp': datetime.utcnow().isoformat(),
        'version': VERSION,
        'build_date': BUILD_DATE,
        'git_commit': VCS_REF[:7] if VCS_REF != 'unknown' else 'unknown',
        'environment': os.environ.get('ENVIRONMENT', 'development')
    })

@app.route('/version')
def version_info():
    return jsonify({
        'version': VERSION,
        'build_date': BUILD_DATE,
        'git_commit': VCS_REF[:7] if VCS_REF != 'unknown' else 'unknown',
        'hostname': socket.gethostname(),
        'environment': os.environ.get('ENVIRONMENT', 'development')
    })

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/ready')
def readiness_check():
    return jsonify({
        'status': 'ready',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
