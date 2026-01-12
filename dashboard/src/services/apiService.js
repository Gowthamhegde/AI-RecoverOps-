// API Service for AI-RecoverOps Dashboard

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Incident Management
  async getIncidents(timeRange = '24h') {
    // Mock data for demonstration - replace with actual API call
    return this.generateMockIncidents();
  }

  async getIncidentById(incidentId) {
    return this.request(`/incidents/${incidentId}`);
  }

  async performIncidentAction(incidentId, action) {
    return this.request(`/incidents/${incidentId}/actions`, {
      method: 'POST',
      body: JSON.stringify({ action }),
    });
  }

  // Remediation Management
  async getRemediations(timeRange = '24h') {
    // Mock data for demonstration
    return this.generateMockRemediations();
  }

  async getRemediationById(remediationId) {
    return this.request(`/remediations/${remediationId}`);
  }

  // System Metrics
  async getMetrics(timeRange = '24h') {
    // Mock data for demonstration
    return this.generateMockMetrics();
  }

  // ML Model Management
  async getModelStatus() {
    return this.request('/models');
  }

  async predictIncidents(logs) {
    return this.request('/predict', {
      method: 'POST',
      body: JSON.stringify({ logs }),
    });
  }

  // Health Check
  async getHealth() {
    return this.request('/health');
  }

  // Mock data generators (replace with actual API calls in production)
  generateMockIncidents() {
    const incidentTypes = [
      'high_cpu', 'memory_leak', 'disk_full', 'permission_denied',
      'service_crash', 'port_in_use', 'db_connection_failure', 'container_oom'
    ];
    
    const services = ['web-server', 'api-service', 'database', 'cache-service', 'worker'];
    const severities = ['critical', 'high', 'medium'];
    const statuses = ['open', 'investigating', 'remediating', 'resolved'];

    const incidents = [];
    const now = new Date();

    for (let i = 0; i < 25; i++) {
      const incidentType = incidentTypes[Math.floor(Math.random() * incidentTypes.length)];
      const service = services[Math.floor(Math.random() * services.length)];
      const severity = severities[Math.floor(Math.random() * severities.length)];
      const status = statuses[Math.floor(Math.random() * statuses.length)];
      
      const timestamp = new Date(now.getTime() - Math.random() * 24 * 60 * 60 * 1000);
      
      incidents.push({
        id: `incident-${i + 1}`,
        timestamp: timestamp.toISOString(),
        severity,
        status,
        service,
        instance_id: `i-${Math.random().toString(36).substr(2, 9)}`,
        prediction: {
          incident_type: incidentType,
          confidence: 0.7 + Math.random() * 0.3,
          recommended_action: this.getRecommendedAction(incidentType),
        },
        log: {
          message: this.generateLogMessage(incidentType, service),
          log_level: severity === 'critical' ? 'ERROR' : 'WARN',
        },
        remediation_status: Math.random() > 0.3 ? 'completed' : 'pending',
        remediation_success: Math.random() > 0.2,
        auto_remediated: Math.random() > 0.4,
      });
    }

    return incidents.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  }

  generateMockRemediations() {
    const actions = [
      'restart_service', 'scale_horizontally', 'clean_logs', 'fix_permissions',
      'restart_database', 'kill_conflicting_process', 'clear_cache'
    ];

    const remediations = [];
    const now = new Date();

    for (let i = 0; i < 15; i++) {
      const action = actions[Math.floor(Math.random() * actions.length)];
      const success = Math.random() > 0.2;
      const timestamp = new Date(now.getTime() - Math.random() * 24 * 60 * 60 * 1000);
      
      remediations.push({
        id: `remediation-${i + 1}`,
        incident_id: `incident-${Math.floor(Math.random() * 25) + 1}`,
        timestamp: timestamp.toISOString(),
        action,
        success,
        duration_seconds: Math.floor(Math.random() * 300) + 30,
        instance_id: `i-${Math.random().toString(36).substr(2, 9)}`,
        service: ['web-server', 'api-service', 'database'][Math.floor(Math.random() * 3)],
        error: success ? null : 'Connection timeout during remediation',
        auto_triggered: Math.random() > 0.3,
      });
    }

    return remediations.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  }

  generateMockMetrics() {
    const now = new Date();
    const hours = [];
    
    // Generate hourly data for the last 24 hours
    for (let i = 23; i >= 0; i--) {
      const timestamp = new Date(now.getTime() - i * 60 * 60 * 1000);
      hours.push({
        timestamp: timestamp.toISOString(),
        incidents_detected: Math.floor(Math.random() * 10),
        incidents_resolved: Math.floor(Math.random() * 8),
        auto_remediations: Math.floor(Math.random() * 6),
        manual_interventions: Math.floor(Math.random() * 3),
        avg_resolution_time: Math.floor(Math.random() * 300) + 60,
        system_health_score: 85 + Math.random() * 15,
      });
    }

    return {
      current: {
        total_incidents: 156,
        resolved_incidents: 142,
        pending_incidents: 14,
        auto_remediation_rate: 78.5,
        avg_resolution_time: 245,
        system_health_score: 92.3,
        uptime_percentage: 99.7,
      },
      trends: {
        incidents_by_hour: hours,
        top_services: [
          { name: 'web-server', incidents: 45, resolved: 42 },
          { name: 'api-service', incidents: 38, resolved: 35 },
          { name: 'database', incidents: 32, resolved: 30 },
          { name: 'cache-service', incidents: 25, resolved: 23 },
          { name: 'worker', incidents: 16, resolved: 12 },
        ],
        remediation_success_by_type: [
          { action: 'restart_service', success_rate: 95.2, count: 42 },
          { action: 'clean_logs', success_rate: 98.1, count: 31 },
          { action: 'scale_horizontally', success_rate: 87.5, count: 24 },
          { action: 'fix_permissions', success_rate: 76.9, count: 13 },
          { action: 'restart_database', success_rate: 83.3, count: 12 },
        ],
      },
    };
  }

  getRecommendedAction(incidentType) {
    const actionMap = {
      high_cpu: 'restart_service',
      memory_leak: 'restart_service',
      disk_full: 'clean_logs',
      permission_denied: 'fix_permissions',
      service_crash: 'restart_service',
      port_in_use: 'kill_conflicting_process',
      db_connection_failure: 'restart_database',
      container_oom: 'increase_memory_limit',
    };
    
    return actionMap[incidentType] || 'manual_investigation';
  }

  generateLogMessage(incidentType, service) {
    const messages = {
      high_cpu: `High CPU usage detected on ${service}: 95.2%`,
      memory_leak: `Memory usage increased to 98% on ${service}`,
      disk_full: `Disk usage at 97% on ${service} volume`,
      permission_denied: `Permission denied accessing /var/log/${service}.log`,
      service_crash: `Service ${service} crashed with exit code 1`,
      port_in_use: `Port 8080 already in use by ${service}`,
      db_connection_failure: `Database connection timeout to ${service}`,
      container_oom: `Container ${service} killed due to OOM`,
    };
    
    return messages[incidentType] || `Unknown error in ${service}`;
  }
}

export const apiService = new ApiService();