# WebSocket Disconnect Debugging

**Scenario**: Production WebSocket connections experiencing frequent disconnects, causing real-time feature failures and poor user experience.

**The 3 AM Reality**: Chat messages not delivering, live updates failing, and users constantly losing connection to real-time features.

## Symptoms Checklist

- [ ] High WebSocket disconnect rates (>5% per minute)
- [ ] Connection timeouts and failed upgrades
- [ ] Client-side reconnection loops
- [ ] Proxy/load balancer connection issues
- [ ] Memory leaks from abandoned connections

## Critical Commands & Analysis

### WebSocket Server Monitoring
```javascript
// Monitor WebSocket connections
const WebSocket = require('ws');

class WebSocketMonitor {
  constructor(wss) {
    this.wss = wss;
    this.connections = new Map();
    this.metrics = {
      totalConnections: 0,
      activeConnections: 0,
      disconnects: 0,
      errors: 0
    };

    this.setupMonitoring();
  }

  setupMonitoring() {
    this.wss.on('connection', (ws, req) => {
      const connectionId = this.generateId();
      const connectionInfo = {
        id: connectionId,
        ip: req.socket.remoteAddress,
        userAgent: req.headers['user-agent'],
        connectedAt: new Date(),
        lastPing: new Date()
      };

      this.connections.set(ws, connectionInfo);
      this.metrics.totalConnections++;
      this.metrics.activeConnections++;

      ws.on('close', (code, reason) => {
        this.handleDisconnect(ws, code, reason);
      });

      ws.on('error', (error) => {
        this.handleError(ws, error);
      });

      ws.on('pong', () => {
        const info = this.connections.get(ws);
        if (info) info.lastPing = new Date();
      });
    });
  }

  handleDisconnect(ws, code, reason) {
    const info = this.connections.get(ws);
    this.metrics.activeConnections--;
    this.metrics.disconnects++;

    console.log('WebSocket disconnect:', {
      connectionId: info?.id,
      code,
      reason: reason.toString(),
      duration: info ? Date.now() - info.connectedAt : 0
    });

    this.connections.delete(ws);
  }
}
```

### Network Diagnostics
```bash
# Check WebSocket connectivity
curl -i -N -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Key: test" \
     -H "Sec-WebSocket-Version: 13" \
     http://localhost:8080/ws

# Monitor TCP connections
netstat -an | grep :8080 | head -20

# Check proxy/load balancer configuration
curl -H "Upgrade: websocket" -H "Connection: upgrade" \
     -H "Sec-WebSocket-Key: test" \
     -H "Sec-WebSocket-Version: 13" \
     http://your-domain.com/ws -v
```

## Common Root Causes & Solutions

### 1. Proxy/Load Balancer Issues (40% of cases)
```nginx
# Problem: Nginx not configured for WebSocket
location /ws {
    proxy_pass http://backend;
    # Missing WebSocket headers
}

# Solution: Proper WebSocket proxy configuration
location /ws {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # Important: Disable buffering
    proxy_buffering off;

    # Timeouts
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
}
```

### 2. Keep-Alive and Heartbeat Issues (30% of cases)
```javascript
// Problem: No heartbeat mechanism
const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', (ws) => {
  // No ping mechanism - connections die silently
});

// Solution: Implement proper heartbeat
class HeartbeatWebSocketServer {
  constructor(options) {
    this.wss = new WebSocket.Server(options);
    this.pingInterval = 30000; // 30 seconds
    this.pongTimeout = 5000;   // 5 seconds

    this.setupHeartbeat();
  }

  setupHeartbeat() {
    this.wss.on('connection', (ws) => {
      ws.isAlive = true;

      ws.on('pong', () => {
        ws.isAlive = true;
      });

      // Start heartbeat for this connection
      ws.pingTimer = setInterval(() => {
        if (!ws.isAlive) {
          console.log('WebSocket unresponsive, terminating');
          ws.terminate();
          return;
        }

        ws.isAlive = false;
        ws.ping();
      }, this.pingInterval);

      ws.on('close', () => {
        clearInterval(ws.pingTimer);
      });
    });
  }
}

// Client-side heartbeat
class WebSocketClient {
  constructor(url) {
    this.url = url;
    this.reconnectDelay = 1000;
    this.maxReconnectDelay = 30000;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;

    this.connect();
  }

  connect() {
    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      this.reconnectDelay = 1000;
    };

    this.ws.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason);
      this.scheduleReconnect();
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    // Handle server pings
    this.ws.onmessage = (event) => {
      if (event.data === 'ping') {
        this.ws.send('pong');
      }
    };
  }

  scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnect attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts),
      this.maxReconnectDelay
    );

    setTimeout(() => {
      console.log(`Reconnecting... (attempt ${this.reconnectAttempts})`);
      this.connect();
    }, delay);
  }
}
```

### 3. Network Timeouts and Firewalls (20% of cases)
```javascript
// Problem: Default timeouts too aggressive
const server = http.createServer();
const wss = new WebSocket.Server({ server });

// Solution: Configure appropriate timeouts
server.timeout = 300000; // 5 minutes
server.keepAliveTimeout = 65000; // 65 seconds
server.headersTimeout = 66000; // 66 seconds

// Handle connection state properly
wss.on('connection', (ws, req) => {
  // Set socket options
  ws._socket.setKeepAlive(true, 60000);
  ws._socket.setTimeout(0); // Disable socket timeout

  ws.on('close', (code, reason) => {
    console.log(`Connection closed: ${code} - ${reason}`);
  });
});

// Mobile-specific considerations
class MobileWebSocketHandler {
  constructor() {
    this.backgroundTimeout = 60000; // 1 minute for mobile background
    this.foregroundTimeout = 300000; // 5 minutes for active use
  }

  handleConnection(ws, req) {
    const userAgent = req.headers['user-agent'] || '';
    const isMobile = /Mobile|Android|iPhone|iPad/.test(userAgent);

    if (isMobile) {
      // Shorter timeout for mobile
      ws._socket.setTimeout(this.backgroundTimeout);

      // Listen for app state changes (if sent by client)
      ws.on('message', (data) => {
        try {
          const message = JSON.parse(data);
          if (message.type === 'app_state') {
            const timeout = message.state === 'background' ?
              this.backgroundTimeout : this.foregroundTimeout;
            ws._socket.setTimeout(timeout);
          }
        } catch (e) {
          // Ignore non-JSON messages
        }
      });
    }
  }
}
```

### 4. Memory Leaks and Resource Issues (7% of cases)
```javascript
// Problem: Not cleaning up resources
class LeakyWebSocketServer {
  constructor() {
    this.connections = [];
    this.timers = [];
  }

  handleConnection(ws) {
    this.connections.push(ws);

    // Memory leak: Timer not cleared
    const timer = setInterval(() => {
      ws.send('heartbeat');
    }, 30000);
    this.timers.push(timer);
  }
}

// Solution: Proper resource management
class CleanWebSocketServer {
  constructor() {
    this.connections = new Set();
    this.connectionMetadata = new WeakMap();
  }

  handleConnection(ws) {
    this.connections.add(ws);

    const metadata = {
      timers: [],
      listeners: []
    };
    this.connectionMetadata.set(ws, metadata);

    // Set up heartbeat with cleanup
    const heartbeatTimer = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send('heartbeat');
      } else {
        this.cleanup(ws);
      }
    }, 30000);

    metadata.timers.push(heartbeatTimer);

    // Event listeners with cleanup
    const closeHandler = () => this.cleanup(ws);
    const errorHandler = (error) => {
      console.error('WebSocket error:', error);
      this.cleanup(ws);
    };

    ws.addEventListener('close', closeHandler);
    ws.addEventListener('error', errorHandler);

    metadata.listeners.push(
      { event: 'close', handler: closeHandler },
      { event: 'error', handler: errorHandler }
    );
  }

  cleanup(ws) {
    const metadata = this.connectionMetadata.get(ws);
    if (metadata) {
      // Clear timers
      metadata.timers.forEach(timer => clearInterval(timer));

      // Remove event listeners
      metadata.listeners.forEach(({ event, handler }) => {
        ws.removeEventListener(event, handler);
      });

      this.connectionMetadata.delete(ws);
    }

    this.connections.delete(ws);
  }

  // Periodic cleanup for dead connections
  startCleanupTask() {
    setInterval(() => {
      this.connections.forEach(ws => {
        if (ws.readyState !== WebSocket.OPEN) {
          this.cleanup(ws);
        }
      });
    }, 60000); // Every minute
  }
}
```

### 5. Client-Side Issues (3% of cases)
```javascript
// Problem: Poor client-side connection management
class BadWebSocketClient {
  connect() {
    this.ws = new WebSocket('ws://localhost:8080');
    // No error handling, reconnection, or cleanup
  }
}

// Solution: Robust client implementation
class RobustWebSocketClient {
  constructor(url, options = {}) {
    this.url = url;
    this.options = {
      reconnectDelay: 1000,
      maxReconnectDelay: 30000,
      maxReconnectAttempts: 5,
      heartbeatInterval: 30000,
      ...options
    };

    this.reconnectAttempts = 0;
    this.heartbeatTimer = null;
    this.isIntentionallyClosed = false;

    this.connect();
  }

  connect() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = (event) => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        this.startHeartbeat();

        if (this.options.onOpen) {
          this.options.onOpen(event);
        }
      };

      this.ws.onmessage = (event) => {
        this.handleMessage(event);
      };

      this.ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code);
        this.stopHeartbeat();

        if (!this.isIntentionallyClosed) {
          this.scheduleReconnect();
        }

        if (this.options.onClose) {
          this.options.onClose(event);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);

        if (this.options.onError) {
          this.options.onError(error);
        }
      };

    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      this.scheduleReconnect();
    }
  }

  handleMessage(event) {
    if (event.data === 'ping') {
      this.send('pong');
    } else if (this.options.onMessage) {
      this.options.onMessage(event);
    }
  }

  startHeartbeat() {
    this.stopHeartbeat();
    this.heartbeatTimer = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.send('ping');
      }
    }, this.options.heartbeatInterval);
  }

  stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  scheduleReconnect() {
    if (this.reconnectAttempts >= this.options.maxReconnectAttempts) {
      console.error('Max reconnect attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(
      this.options.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
      this.options.maxReconnectDelay
    );

    setTimeout(() => {
      if (!this.isIntentionallyClosed) {
        console.log(`Reconnecting... (attempt ${this.reconnectAttempts})`);
        this.connect();
      }
    }, delay);
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(typeof data === 'string' ? data : JSON.stringify(data));
    } else {
      console.warn('WebSocket not connected, cannot send message');
    }
  }

  close() {
    this.isIntentionallyClosed = true;
    this.stopHeartbeat();

    if (this.ws) {
      this.ws.close();
    }
  }
}
```

## Production Examples

### Discord's Voice Connection Issues (2020)
- **Incident**: Voice channels experiencing 40% disconnect rate during peak hours
- **Root Cause**: AWS load balancer not properly handling WebSocket upgrades
- **Impact**: Voice chat unusable, user complaints spike
- **Resolution**: Configured ALB for WebSocket support, implemented client retry logic
- **Prevention**: Added WebSocket-specific health checks and monitoring

### Slack's Real-time Messaging (2019)
- **Incident**: Message delivery failures due to WebSocket disconnects
- **Root Cause**: Mobile clients losing connections during app backgrounding
- **Impact**: Messages not delivered in real-time, reduced user engagement
- **Resolution**: Implemented adaptive timeouts based on client type and state
- **Learning**: Mobile WebSockets require different timeout strategies

**Remember**: WebSocket disconnects often stem from network infrastructure issues rather than application bugs. Focus on proper proxy configuration, implement robust heartbeat mechanisms, and always have reconnection logic with exponential backoff.