from flask import Flask, jsonify
import os
import socket
from datetime import datetime

app = Flask(__name__)

# Simple configuration
VERSION = os.environ.get('VERSION', '2.0.0')
GIT_COMMIT = os.environ.get('VCS_REF', 'unknown')[:7]
BUILD_DATE = os.environ.get('BUILD_DATE', 'unknown')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')
DEPLOYMENT_STRATEGY = os.environ.get('DEPLOYMENT_STRATEGY', 'standard')
POD_NAME = os.environ.get('POD_NAME', socket.gethostname())

@app.route('/')
def home():
    """Simple home page with deployment information"""
    return {
        'message': f' Testing Webhook (again) in CI/CD - {DEPLOYMENT_STRATEGY.title()} Deployment',
        'version': VERSION,
        'git_commit': GIT_COMMIT,
        'build_date': BUILD_DATE,
        'pod_name': POD_NAME,
        'deployment_strategy': DEPLOYMENT_STRATEGY,
        'environment': ENVIRONMENT,
        'timestamp': datetime.utcnow().isoformat()
    }

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'instance_id': POD_NAME[-8:],  # Simple instance ID
        'pod_name': POD_NAME,
        'deployment_strategy': DEPLOYMENT_STRATEGY,
        'environment': DEPLOYMENT_STRATEGY
    }), 200

@app.route('/ready')
def readiness_check():
    """Readiness check endpoint"""
    return jsonify({
        'status': 'ready',
        'timestamp': datetime.utcnow().isoformat(),
        'instance_id': POD_NAME[-8:],
        'pod_name': POD_NAME
    }), 200

@app.route('/version')
def version_info():
    """Version information"""
    return jsonify({
        'version': VERSION,
        'build_date': BUILD_DATE,
        'git_commit': GIT_COMMIT,
        'hostname': socket.gethostname(),
        'pod_name': POD_NAME,
        'instance_id': POD_NAME[-8:],
        'environment': ENVIRONMENT,
        'deployment_strategy': DEPLOYMENT_STRATEGY
    })

@app.route('/metrics')
def metrics():
    """Simple metrics endpoint"""
    return jsonify({
        'instance_id': POD_NAME[-8:],
        'pod_name': POD_NAME,
        'deployment_strategy': DEPLOYMENT_STRATEGY,
        'environment': DEPLOYMENT_STRATEGY,
        'version': VERSION,
        'git_commit': GIT_COMMIT,
        'build_date': BUILD_DATE,
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)