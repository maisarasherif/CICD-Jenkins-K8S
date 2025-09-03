from flask import Flask, jsonify, render_template_string
import os
import socket
import hashlib
from datetime import datetime

app = Flask(__name__)

# App configuration
BUILD_DATE = os.environ.get('BUILD_DATE', datetime.utcnow().isoformat())
VCS_REF = os.environ.get('VCS_REF', 'unknown')
VERSION = os.environ.get('VERSION', '2.0.0')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')
DEPLOYMENT_STRATEGY = os.environ.get('DEPLOYMENT_STRATEGY', 'standard')
POD_NAME = os.environ.get('POD_NAME', socket.gethostname())

# Generate unique instance ID based on pod name
INSTANCE_ID = hashlib.md5(POD_NAME.encode()).hexdigest()[:8]

# Determine environment color (static - no randomization)
def get_environment_color():
    """Static color assignment based on pod name"""
    if DEPLOYMENT_STRATEGY == 'bluegreen':
        # Use pod name hash to consistently assign blue or green
        if int(INSTANCE_ID[-1], 16) % 2 == 0:
            return 'blue'
        else:
            return 'green'
    elif DEPLOYMENT_STRATEGY == 'canary':
        if int(INSTANCE_ID[-1], 16) % 2 == 0:
            return 'stable'
        else:
            return 'canary'
    else:
        return 'standard'

CURRENT_COLOR = get_environment_color()

# Color schemes
COLOR_SCHEMES = {
    'bluegreen': {
        'blue': {'primary': '#2563eb', 'secondary': '#60a5fa', 'name': 'Blue Environment'},
        'green': {'primary': '#059669', 'secondary': '#34d399', 'name': 'Green Environment'}
    },
    'canary': {
        'stable': {'primary': '#7c3aed', 'secondary': '#a78bfa', 'name': 'Stable Release'},
        'canary': {'primary': '#ea580c', 'secondary': '#fb923c', 'name': 'Canary Release'}
    },
    'standard': {
        'standard': {'primary': '#1f2937', 'secondary': '#6b7280', 'name': 'Standard Deployment'}
    }
}

# Static HTML Template (no animations or real-time updates)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CI/CD Demo - {{ deployment_strategy.title() }} Deployment</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '{{ primary_color }}',
                        secondary: '{{ secondary_color }}'
                    }
                }
            }
        }
    </script>
    <style>
        .gradient-bg {
            background: linear-gradient(135deg, {{ primary_color }}, {{ secondary_color }});
        }
        .deployment-card {
            backdrop-filter: blur(16px) saturate(180%);
            background-color: rgba(255, 255, 255, 0.75);
            border: 1px solid rgba(209, 213, 219, 0.3);
        }
        .status-dot {
            background-color: {{ primary_color }};
        }
    </style>
</head>
<body class="gradient-bg min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <!-- Header -->
        <div class="text-center mb-12">
            <h1 class="text-6xl font-bold text-white mb-4 drop-shadow-lg">
                🚀 CI/CD Pipeline Demo
            </h1>
            <p class="text-xl text-white/90 font-medium">{{ environment_name }} - {{ deployment_strategy.title() }} Strategy</p>
        </div>

        <!-- Main Dashboard -->
        <div class="grid lg:grid-cols-2 gap-8 mb-8">
            <!-- Environment Info Card -->
            <div class="deployment-card rounded-2xl p-8 shadow-2xl">
                <div class="flex items-center justify-between mb-6">
                    <h2 class="text-2xl font-bold text-gray-800">Environment Details</h2>
                    <div class="w-4 h-4 rounded-full status-dot"></div>
                </div>
                
                <div class="space-y-4">
                    <div class="flex justify-between items-center py-3 border-b border-gray-200">
                        <span class="font-semibold text-gray-600">Strategy:</span>
                        <span class="px-4 py-2 rounded-full text-sm font-medium text-white" style="background-color: {{ primary_color }}">
                            {{ deployment_strategy.upper() }}
                        </span>
                    </div>
                    <div class="flex justify-between items-center py-3 border-b border-gray-200">
                        <span class="font-semibold text-gray-600">Environment:</span>
                        <span class="font-mono text-gray-800">{{ environment_name }}</span>
                    </div>
                    <div class="flex justify-between items-center py-3 border-b border-gray-200">
                        <span class="font-semibold text-gray-600">Instance ID:</span>
                        <span class="font-mono text-gray-800">{{ instance_id }}</span>
                    </div>
                    <div class="flex justify-between items-center py-3 border-b border-gray-200">
                        <span class="font-semibold text-gray-600">Pod Name:</span>
                        <span class="font-mono text-sm text-gray-800">{{ pod_name }}</span>
                    </div>
                    <div class="flex justify-between items-center py-3">
                        <span class="font-semibold text-gray-600">Current Time:</span>
                        <span class="font-mono text-sm text-gray-800">{{ current_time }}</span>
                    </div>
                </div>
            </div>

            <!-- Version Info Card -->
            <div class="deployment-card rounded-2xl p-8 shadow-2xl">
                <div class="flex items-center justify-between mb-6">
                    <h2 class="text-2xl font-bold text-gray-800">Version Information</h2>
                    <div class="text-3xl">📦</div>
                </div>
                
                <div class="space-y-4">
                    <div class="flex justify-between items-center py-3 border-b border-gray-200">
                        <span class="font-semibold text-gray-600">Version:</span>
                        <span class="text-2xl font-bold" style="color: {{ primary_color }}">v{{ version }}</span>
                    </div>
                    <div class="flex justify-between items-center py-3 border-b border-gray-200">
                        <span class="font-semibold text-gray-600">Git Commit:</span>
                        <span class="font-mono text-gray-800 bg-gray-100 px-2 py-1 rounded">{{ git_commit }}</span>
                    </div>
                    <div class="flex justify-between items-center py-3 border-b border-gray-200">
                        <span class="font-semibold text-gray-600">Build Date:</span>
                        <span class="font-mono text-sm text-gray-800">{{ build_date }}</span>
                    </div>
                    <div class="flex justify-between items-center py-3">
                        <span class="font-semibold text-gray-600">Deployment:</span>
                        <span class="font-mono text-sm text-gray-800">{{ current_time }}</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Deployment Strategy Explanation -->
        <div class="deployment-card rounded-2xl p-8 shadow-2xl mb-8">
            <h2 class="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                <span class="mr-3">💡</span>
                {{ deployment_strategy.title() }} Deployment Strategy
            </h2>
            
            {% if deployment_strategy == 'bluegreen' %}
            <div class="grid md:grid-cols-2 gap-6">
                <div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
                    <h3 class="font-bold text-blue-800 mb-2">🔵 Blue Environment</h3>
                    <p class="text-sm text-blue-700">Current production version serving live traffic</p>
                </div>
                <div class="bg-green-50 border-l-4 border-green-500 p-4 rounded">
                    <h3 class="font-bold text-green-800 mb-2">🟢 Green Environment</h3>
                    <p class="text-sm text-green-700">New version being tested before promotion</p>
                </div>
            </div>
            <p class="mt-4 text-gray-600">
                <strong>How it works:</strong> Deploy new version alongside current version, test thoroughly, 
                then instantly switch all traffic. Allows immediate rollback.
            </p>
            {% elif deployment_strategy == 'canary' %}
            <div class="grid md:grid-cols-2 gap-6">
                <div class="bg-purple-50 border-l-4 border-purple-500 p-4 rounded">
                    <h3 class="font-bold text-purple-800 mb-2">🟣 Stable Release</h3>
                    <p class="text-sm text-purple-700">Proven version serving most traffic</p>
                </div>
                <div class="bg-orange-50 border-l-4 border-orange-500 p-4 rounded">
                    <h3 class="font-bold text-orange-800 mb-2">🟠 Canary Release</h3>
                    <p class="text-sm text-orange-700">New version serving small percentage of traffic</p>
                </div>
            </div>
            <p class="mt-4 text-gray-600">
                <strong>How it works:</strong> Gradually increase traffic to new version (25% → 50% → 75% → 100%). 
                Monitor metrics at each step.
            </p>
            {% else %}
            <div class="bg-gray-50 border-l-4 border-gray-500 p-4 rounded">
                <h3 class="font-bold text-gray-800 mb-2">📦 Standard Deployment</h3>
                <p class="text-sm text-gray-700">Traditional rolling update deployment</p>
            </div>
            <p class="mt-4 text-gray-600">
                <strong>How it works:</strong> Replace pods one by one with new version. 
                Simple but less control over traffic distribution.
            </p>
            {% endif %}
        </div>

        <!-- API Endpoints -->
        <div class="deployment-card rounded-2xl p-8 shadow-2xl">
            <h2 class="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                <span class="mr-3">🔗</span>
                Available Endpoints
            </h2>
            
            <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                <a href="/health" class="block p-4 bg-green-50 hover:bg-green-100 rounded-lg border-2 border-green-200 transition-colors">
                    <div class="text-green-600 font-semibold">GET /health</div>
                    <div class="text-sm text-green-700 mt-1">Health Check</div>
                </a>
                <a href="/ready" class="block p-4 bg-blue-50 hover:bg-blue-100 rounded-lg border-2 border-blue-200 transition-colors">
                    <div class="text-blue-600 font-semibold">GET /ready</div>
                    <div class="text-sm text-blue-700 mt-1">Readiness Check</div>
                </a>
                <a href="/version" class="block p-4 bg-purple-50 hover:bg-purple-100 rounded-lg border-2 border-purple-200 transition-colors">
                    <div class="text-purple-600 font-semibold">GET /version</div>
                    <div class="text-sm text-purple-700 mt-1">Version Info</div>
                </a>
                <a href="/metrics" class="block p-4 bg-orange-50 hover:bg-orange-100 rounded-lg border-2 border-orange-200 transition-colors">
                    <div class="text-orange-600 font-semibold">GET /metrics</div>
                    <div class="text-sm text-orange-700 mt-1">Application Metrics</div>
                </a>
            </div>
        </div>

        <!-- Footer -->
        <div class="text-center mt-12">
            <p class="text-white/70">
                Deployment completed: {{ current_time }}
            </p>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    """Static home page with visual deployment information"""
    color_config = COLOR_SCHEMES.get(DEPLOYMENT_STRATEGY, COLOR_SCHEMES['standard'])
    current_env = color_config[CURRENT_COLOR]
    
    return render_template_string(HTML_TEMPLATE,
        deployment_strategy=DEPLOYMENT_STRATEGY,
        environment_name=current_env['name'],
        primary_color=current_env['primary'],
        secondary_color=current_env['secondary'],
        instance_id=INSTANCE_ID,
        pod_name=POD_NAME,
        version=VERSION,
        git_commit=VCS_REF[:7] if VCS_REF != 'unknown' else 'unknown',
        build_date=BUILD_DATE,
        current_time=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    )

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'instance_id': INSTANCE_ID,
        'pod_name': POD_NAME,
        'deployment_strategy': DEPLOYMENT_STRATEGY,
        'environment': CURRENT_COLOR
    }), 200

@app.route('/ready')
def readiness_check():
    """Readiness check endpoint"""
    return jsonify({
        'status': 'ready',
        'timestamp': datetime.utcnow().isoformat(),
        'instance_id': INSTANCE_ID,
        'pod_name': POD_NAME
    }), 200

@app.route('/version')
def version_info():
    """Detailed version information"""
    return jsonify({
        'version': VERSION,
        'build_date': BUILD_DATE,
        'git_commit': VCS_REF[:7] if VCS_REF != 'unknown' else 'unknown',
        'git_commit_full': VCS_REF,
        'hostname': socket.gethostname(),
        'pod_name': POD_NAME,
        'instance_id': INSTANCE_ID,
        'environment': ENVIRONMENT,
        'deployment_strategy': DEPLOYMENT_STRATEGY,
        'current_environment': CURRENT_COLOR
    })

@app.route('/metrics')
def metrics():
    """Static application metrics"""
    return jsonify({
        'instance_id': INSTANCE_ID,
        'pod_name': POD_NAME,
        'deployment_strategy': DEPLOYMENT_STRATEGY,
        'environment': CURRENT_COLOR,
        'version': VERSION,
        'git_commit': VCS_REF[:7] if VCS_REF != 'unknown' else 'unknown',
        'build_date': BUILD_DATE,
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)