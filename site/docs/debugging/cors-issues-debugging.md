# CORS Issues Debugging: Cross-Origin Resource Sharing Troubleshooting Guide

## Executive Summary

CORS (Cross-Origin Resource Sharing) issues affect 50% of web applications and are among the most misunderstood browser security mechanisms. This guide provides systematic debugging approaches for preflight failures, credential issues, and complex CORS configurations.

## Common CORS Error Patterns

### Browser Console Error Messages
```javascript
// Common CORS error messages to look for:

// 1. Preflight failure
"Access to XMLHttpRequest at 'https://api.example.com/data' from origin 'https://myapp.com' has been blocked by CORS policy: Response to preflight request doesn't pass access control check: No 'Access-Control-Allow-Origin' header is present on the requested resource."

// 2. Credential issues
"Access to XMLHttpRequest at 'https://api.example.com/secure' from origin 'https://myapp.com' has been blocked by CORS policy: The value of the 'Access-Control-Allow-Credentials' header in the response is '' which must be 'true' when the request's credentials mode is 'include'."

// 3. Method not allowed
"Access to XMLHttpRequest at 'https://api.example.com/update' from origin 'https://myapp.com' has been blocked by CORS policy: Method PUT is not allowed by Access-Control-Allow-Methods in preflight response."

// 4. Header not allowed
"Access to XMLHttpRequest at 'https://api.example.com/data' from origin 'https://myapp.com' has been blocked by CORS policy: Request header field authorization is not allowed by Access-Control-Allow-Headers in preflight response."
```

### Network Tab Investigation
```bash
# Check for preflight OPTIONS requests in browser DevTools
# Look for:
# 1. OPTIONS request before actual request
# 2. Response headers: Access-Control-Allow-*
# 3. Request headers: Origin, Access-Control-Request-*

# Command line testing with curl
curl -X OPTIONS https://api.example.com/endpoint \\
  -H "Origin: https://myapp.com" \\
  -H "Access-Control-Request-Method: POST" \\
  -H "Access-Control-Request-Headers: authorization,content-type" \\
  -v

# Test actual request
curl -X POST https://api.example.com/endpoint \\
  -H "Origin: https://myapp.com" \\
  -H "Authorization: Bearer token123" \\
  -H "Content-Type: application/json" \\
  -d '{"data": "test"}' \\
  -v
```

## CORS Configuration Analysis

### Server-Side CORS Implementation

#### Express.js (Node.js) CORS Configuration
```javascript
const express = require('express');
const cors = require('cors');
const app = express();

// Basic CORS configuration
const corsOptions = {
  origin: function (origin, callback) {
    // Allow requests with no origin (mobile apps, curl, etc.)
    if (!origin) return callback(null, true);

    const allowedOrigins = [
      'https://myapp.com',
      'https://staging.myapp.com',
      'http://localhost:3000',  // Development
      'https://preview-*.myapp.com'  // Preview deployments
    ];

    // Support wildcard patterns
    const isAllowed = allowedOrigins.some(allowedOrigin => {
      if (allowedOrigin.includes('*')) {
        const pattern = allowedOrigin.replace('*', '.*');
        return new RegExp(pattern).test(origin);
      }
      return allowedOrigin === origin;
    });

    if (isAllowed) {
      callback(null, true);
    } else {
      console.warn(`CORS blocked origin: ${origin}`);
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true,  // Allow cookies
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: [
    'Origin',
    'X-Requested-With',
    'Content-Type',
    'Accept',
    'Authorization',
    'X-API-Key',
    'X-CSRF-Token'
  ],
  exposedHeaders: [
    'X-Total-Count',
    'X-Page-Count',
    'Link'
  ],
  maxAge: 86400,  // Cache preflight for 24 hours
  optionsSuccessStatus: 200  // For legacy browsers
};

app.use(cors(corsOptions));

// Custom CORS middleware for complex scenarios
app.use('/api/special', (req, res, next) => {
  const origin = req.headers.origin;

  // Dynamic origin validation
  if (origin && origin.endsWith('.trusted-domain.com')) {
    res.header('Access-Control-Allow-Origin', origin);
    res.header('Access-Control-Allow-Credentials', 'true');
  }

  // Handle preflight
  if (req.method === 'OPTIONS') {
    res.header('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE');
    res.header('Access-Control-Allow-Headers', 'authorization,content-type');
    res.header('Access-Control-Max-Age', '86400');
    return res.sendStatus(200);
  }

  next();
});
```

#### Nginx CORS Configuration
```nginx
# Nginx CORS configuration
server {
    listen 80;
    server_name api.example.com;

    # CORS configuration for API endpoints
    location /api/ {
        # Handle preflight requests
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' '$http_origin' always;
            add_header 'Access-Control-Allow-Credentials' 'true' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'Authorization,Accept,Origin,DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Content-Range,Range' always;
            add_header 'Access-Control-Max-Age' 1728000 always;
            add_header 'Content-Type' 'text/plain; charset=utf-8' always;
            add_header 'Content-Length' 0 always;
            return 204;
        }

        # CORS headers for actual requests
        add_header 'Access-Control-Allow-Origin' '$http_origin' always;
        add_header 'Access-Control-Allow-Credentials' 'true' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Authorization,Accept,Origin,DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Content-Range,Range' always;
        add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range' always;

        proxy_pass http://backend;
    }

    # Specific CORS rules for different endpoints
    location /api/public/ {
        # Allow all origins for public API
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, OPTIONS' always;
        proxy_pass http://backend;
    }

    location /api/secure/ {
        # Strict CORS for secure endpoints
        set $cors_origin "";
        if ($http_origin ~* "^https://(.*\\.)?mycompany\\.com$") {
            set $cors_origin $http_origin;
        }

        add_header 'Access-Control-Allow-Origin' $cors_origin always;
        add_header 'Access-Control-Allow-Credentials' 'true' always;
        proxy_pass http://backend;
    }
}
```

## Client-Side CORS Debugging

### JavaScript Fetch API with CORS
```javascript
// Proper CORS request handling
class ApiClient {
    constructor(baseUrl, options = {}) {
        this.baseUrl = baseUrl;
        this.defaultOptions = {
            credentials: 'include',  // Include cookies
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            ...this.defaultOptions,
            ...options,
            headers: {
                ...this.defaultOptions.headers,
                ...options.headers
            }
        };

        try {
            const response = await fetch(url, config);

            // Log CORS headers for debugging
            this.logCorsHeaders(response);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API request failed:', {
                url,
                error: error.message,
                config
            });
            throw error;
        }
    }

    logCorsHeaders(response) {
        const corsHeaders = [
            'access-control-allow-origin',
            'access-control-allow-credentials',
            'access-control-allow-methods',
            'access-control-allow-headers',
            'access-control-expose-headers',
            'access-control-max-age'
        ];

        const corsInfo = {};
        corsHeaders.forEach(header => {
            const value = response.headers.get(header);
            if (value) corsInfo[header] = value;
        });

        if (Object.keys(corsInfo).length > 0) {
            console.debug('CORS headers:', corsInfo);
        }
    }

    // Test CORS configuration
    async testCors() {
        const testEndpoint = '/api/test';
        console.log('Testing CORS configuration...');

        try {
            // Test preflight
            const preflightResponse = await fetch(`${this.baseUrl}${testEndpoint}`, {
                method: 'OPTIONS',
                headers: {
                    'Origin': window.location.origin,
                    'Access-Control-Request-Method': 'POST',
                    'Access-Control-Request-Headers': 'authorization,content-type'
                }
            });

            console.log('Preflight response:', {
                status: preflightResponse.status,
                headers: Object.fromEntries(preflightResponse.headers.entries())
            });

            // Test actual request
            const actualResponse = await this.request(testEndpoint, {
                method: 'GET'
            });

            console.log('CORS test successful:', actualResponse);
            return true;
        } catch (error) {
            console.error('CORS test failed:', error);
            return false;
        }
    }
}

// Usage
const apiClient = new ApiClient('https://api.example.com');

// Test CORS setup
apiClient.testCors().then(success => {
    if (success) {
        console.log('✅ CORS configured correctly');
    } else {
        console.log('❌ CORS configuration issues detected');
    }
});
```

## Advanced CORS Debugging

### CORS Testing Utility
```python
#!/usr/bin/env python3
# cors_tester.py

import requests
import json
import sys
from urllib.parse import urlparse

class CORSTester:
    def __init__(self, target_url, origin):
        self.target_url = target_url
        self.origin = origin
        self.session = requests.Session()

    def test_simple_request(self):
        """Test simple CORS request (GET, HEAD, POST with simple headers)"""
        print(f"\\n🧪 Testing simple CORS request...")

        headers = {
            'Origin': self.origin,
            'User-Agent': 'CORS-Tester/1.0'
        }

        response = self.session.get(self.target_url, headers=headers)

        print(f"Status: {response.status_code}")
        print(f"Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'Not present')}")
        print(f"Access-Control-Allow-Credentials: {response.headers.get('Access-Control-Allow-Credentials', 'Not present')}")

        return response.headers.get('Access-Control-Allow-Origin') is not None

    def test_preflight_request(self, method='POST', headers=None):
        """Test preflight CORS request"""
        print(f"\\n🧪 Testing preflight request for {method}...")

        if headers is None:
            headers = ['authorization', 'content-type']

        preflight_headers = {
            'Origin': self.origin,
            'Access-Control-Request-Method': method,
            'Access-Control-Request-Headers': ','.join(headers)
        }

        response = self.session.options(self.target_url, headers=preflight_headers)

        print(f"Preflight Status: {response.status_code}")
        print(f"Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'Not present')}")
        print(f"Access-Control-Allow-Methods: {response.headers.get('Access-Control-Allow-Methods', 'Not present')}")
        print(f"Access-Control-Allow-Headers: {response.headers.get('Access-Control-Allow-Headers', 'Not present')}")
        print(f"Access-Control-Max-Age: {response.headers.get('Access-Control-Max-Age', 'Not present')}")

        # Validate preflight response
        allowed_methods = response.headers.get('Access-Control-Allow-Methods', '')
        allowed_headers = response.headers.get('Access-Control-Allow-Headers', '').lower()

        method_allowed = method.upper() in allowed_methods.upper()
        headers_allowed = all(h.lower() in allowed_headers for h in headers)

        print(f"Method {method} allowed: {method_allowed}")
        print(f"Headers {headers} allowed: {headers_allowed}")

        return response.status_code == 200 and method_allowed and headers_allowed

    def test_credentials_request(self):
        """Test CORS request with credentials"""
        print(f"\\n🧪 Testing CORS with credentials...")

        headers = {
            'Origin': self.origin,
            'Cookie': 'session=test123'
        }

        response = self.session.get(self.target_url, headers=headers)

        allow_credentials = response.headers.get('Access-Control-Allow-Credentials', '').lower()
        allow_origin = response.headers.get('Access-Control-Allow-Origin', '')

        print(f"Access-Control-Allow-Credentials: {allow_credentials}")
        print(f"Access-Control-Allow-Origin: {allow_origin}")

        # For credentialed requests, origin cannot be '*'
        credentials_valid = (
            allow_credentials == 'true' and
            allow_origin != '*' and
            allow_origin == self.origin
        )

        print(f"Credentials configuration valid: {credentials_valid}")
        return credentials_valid

    def run_full_test(self):
        """Run comprehensive CORS test suite"""
        print(f"🔍 Testing CORS for {self.target_url} from origin {self.origin}")
        print("=" * 60)

        results = {
            'simple_request': self.test_simple_request(),
            'preflight_get': self.test_preflight_request('GET'),
            'preflight_post': self.test_preflight_request('POST'),
            'preflight_put': self.test_preflight_request('PUT'),
            'preflight_delete': self.test_preflight_request('DELETE'),
            'credentials': self.test_credentials_request()
        }

        print(f"\\n📊 CORS Test Results:")
        print("=" * 30)
        for test, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{test}: {status}")

        overall_pass = all(results.values())
        print(f"\\nOverall: {'✅ CORS configured correctly' if overall_pass else '❌ CORS issues detected'}")

        return results

def main():
    if len(sys.argv) != 3:
        print("Usage: python cors_tester.py <target_url> <origin>")
        print("Example: python cors_tester.py https://api.example.com/test https://myapp.com")
        sys.exit(1)

    target_url = sys.argv[1]
    origin = sys.argv[2]

    tester = CORSTester(target_url, origin)
    tester.run_full_test()

if __name__ == "__main__":
    main()
```

## Common CORS Troubleshooting Scenarios

### Development vs Production Issues
```javascript
// Environment-specific CORS configuration
const corsConfig = {
    development: {
        origin: ['http://localhost:3000', 'http://localhost:3001'],
        credentials: true,
        optionsSuccessStatus: 200
    },
    staging: {
        origin: ['https://staging.myapp.com', 'https://preview-*.myapp.com'],
        credentials: true,
        optionsSuccessStatus: 200
    },
    production: {
        origin: ['https://myapp.com', 'https://www.myapp.com'],
        credentials: true,
        optionsSuccessStatus: 200
    }
};

const environment = process.env.NODE_ENV || 'development';
app.use(cors(corsConfig[environment]));
```

### Mobile App CORS Considerations
```javascript
// CORS for mobile applications
const mobileApiCors = {
    origin: function (origin, callback) {
        // Mobile apps don't send Origin header
        if (!origin) {
            return callback(null, true);
        }

        // Web origins
        const webOrigins = ['https://myapp.com', 'https://admin.myapp.com'];
        if (webOrigins.includes(origin)) {
            return callback(null, true);
        }

        callback(new Error('Not allowed by CORS'));
    },
    credentials: false,  // Usually not needed for mobile
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-App-Version']
};
```

This comprehensive CORS debugging guide provides systematic approaches for identifying and resolving cross-origin resource sharing issues in web applications.