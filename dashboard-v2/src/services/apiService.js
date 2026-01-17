/**
 * API Service for AI-RecoverOps Dashboard
 * Handles all HTTP requests to the backend API
 */

import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth tokens
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('ai-recoverops-token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error);
    
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('ai-recoverops-token');
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

export const apiService = {
  // Health and Status
  async getHealth() {
    return api.get('/health');
  },

  async getSystemStatus() {
    return api.get('/api/system-status');
  },

  async getMetrics() {
    return api.get('/metrics');
  },

  // Dashboard
  async getDashboardData() {
    return api.get('/api/dashboard');
  },

  // Incidents
  async getIncidents(params = {}) {
    return api.get('/api/incidents', { params });
  },

  async getIncident(id) {
    return api.get(`/api/incidents/${id}`);
  },

  async updateIncident(id, data) {
    return api.put(`/api/incidents/${id}`, data);
  },

  async getIncidentRemediations(id) {
    return api.get(`/api/incidents/${id}/remediations`);
  },

  async triggerRemediation(id) {
    return api.post(`/api/incidents/${id}/remediate`);
  },

  async rollbackIncident(id) {
    return api.post(`/api/incidents/${id}/rollback`);
  },

  async getIncidentStats() {
    return api.get('/api/incidents/stats/summary');
  },

  async getIncidentTrends(days = 30) {
    return api.get(`/api/incidents/trends/daily?days=${days}`);
  },

  // Pipelines
  async getPipelines(params = {}) {
    return api.get('/api/pipelines', { params });
  },

  async getPipeline(id) {
    return api.get(`/api/pipelines/${id}`);
  },

  async getPipelineRuns(pipelineId, params = {}) {
    return api.get(`/api/pipelines/${pipelineId}/runs`, { params });
  },

  async retriggerPipeline(id) {
    return api.post(`/api/pipelines/${id}/retrigger`);
  },

  async getPipelineStats() {
    return api.get('/api/pipelines/stats/summary');
  },

  // Recovery
  async getRecoveryActions(params = {}) {
    return api.get('/api/recovery/actions', { params });
  },

  async getRecoveryAction(id) {
    return api.get(`/api/recovery/actions/${id}`);
  },

  async executeRecoveryAction(id, params = {}) {
    return api.post(`/api/recovery/actions/${id}/execute`, params);
  },

  async getAWSResources(params = {}) {
    return api.get('/api/recovery/aws/resources', { params });
  },

  async restartAWSResource(resourceId, resourceType) {
    return api.post(`/api/recovery/aws/resources/${resourceId}/restart`, {
      resource_type: resourceType
    });
  },

  async getKubernetesResources(params = {}) {
    return api.get('/api/recovery/k8s/resources', { params });
  },

  async restartKubernetesResource(resourceId, namespace) {
    return api.post(`/api/recovery/k8s/resources/${resourceId}/restart`, {
      namespace
    });
  },

  // Analytics
  async getAnalytics(timeRange = '7d') {
    return api.get(`/api/analytics?range=${timeRange}`);
  },

  async getFailurePatterns() {
    return api.get('/api/analytics/failure-patterns');
  },

  async getResolutionTimes() {
    return api.get('/api/analytics/resolution-times');
  },

  async getSuccessRates() {
    return api.get('/api/analytics/success-rates');
  },

  async getTopFailures(limit = 10) {
    return api.get(`/api/analytics/top-failures?limit=${limit}`);
  },

  // Real-time Monitoring
  async getRealTimeEvents(limit = 50) {
    return api.get(`/api/monitor/events?limit=${limit}`);
  },

  async getActiveMonitors() {
    return api.get('/api/monitor/active');
  },

  async createMonitor(config) {
    return api.post('/api/monitor/create', config);
  },

  async updateMonitor(id, config) {
    return api.put(`/api/monitor/${id}`, config);
  },

  async deleteMonitor(id) {
    return api.delete(`/api/monitor/${id}`);
  },

  // Settings
  async getSettings() {
    return api.get('/api/settings');
  },

  async updateSettings(settings) {
    return api.put('/api/settings', settings);
  },

  async getIntegrations() {
    return api.get('/api/settings/integrations');
  },

  async updateIntegration(name, config) {
    return api.put(`/api/settings/integrations/${name}`, config);
  },

  async testIntegration(name, config) {
    return api.post(`/api/settings/integrations/${name}/test`, config);
  },

  // Users and Authentication
  async login(credentials) {
    return api.post('/api/auth/login', credentials);
  },

  async logout() {
    return api.post('/api/auth/logout');
  },

  async getCurrentUser() {
    return api.get('/api/auth/me');
  },

  async getUsers() {
    return api.get('/api/users');
  },

  async createUser(userData) {
    return api.post('/api/users', userData);
  },

  async updateUser(id, userData) {
    return api.put(`/api/users/${id}`, userData);
  },

  async deleteUser(id) {
    return api.delete(`/api/users/${id}`);
  },

  // Logs
  async getLogs(params = {}) {
    return api.get('/api/logs', { params });
  },

  async searchLogs(query, params = {}) {
    return api.get('/api/logs/search', { 
      params: { q: query, ...params } 
    });
  },

  // Webhooks
  async getWebhookHistory(params = {}) {
    return api.get('/api/webhooks/history', { params });
  },

  async getWebhookStats() {
    return api.get('/api/webhooks/stats');
  },

  // Emergency Controls
  async emergencyStop() {
    return api.post('/api/emergency-stop');
  },

  async emergencyResume() {
    return api.post('/api/emergency-resume');
  },

  // Audit Logs
  async getAuditLogs(params = {}) {
    return api.get('/api/audit', { params });
  },

  // Export/Import
  async exportData(type, params = {}) {
    return api.get(`/api/export/${type}`, { 
      params,
      responseType: 'blob'
    });
  },

  async importData(type, file) {
    const formData = new FormData();
    formData.append('file', file);
    
    return api.post(`/api/import/${type}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // AI/ML Model Management
  async getModels() {
    return api.get('/api/models');
  },

  async getModelMetrics(modelId) {
    return api.get(`/api/models/${modelId}/metrics`);
  },

  async retrainModel(modelId) {
    return api.post(`/api/models/${modelId}/retrain`);
  },

  async updateModelConfig(modelId, config) {
    return api.put(`/api/models/${modelId}/config`, config);
  },

  // Notifications
  async getNotifications(params = {}) {
    return api.get('/api/notifications', { params });
  },

  async markNotificationRead(id) {
    return api.put(`/api/notifications/${id}/read`);
  },

  async getNotificationSettings() {
    return api.get('/api/notifications/settings');
  },

  async updateNotificationSettings(settings) {
    return api.put('/api/notifications/settings', settings);
  },

  // Testing and Simulation
  async simulateIncident(config) {
    return api.post('/api/test/simulate-incident', config);
  },

  async runHealthCheck() {
    return api.post('/api/test/health-check');
  },

  async validateConfiguration() {
    return api.post('/api/test/validate-config');
  },

  // Batch Operations
  async batchUpdateIncidents(ids, updates) {
    return api.put('/api/incidents/batch', {
      incident_ids: ids,
      updates
    });
  },

  async batchDeleteIncidents(ids) {
    return api.delete('/api/incidents/batch', {
      data: { incident_ids: ids }
    });
  },

  // Custom Queries
  async customQuery(endpoint, method = 'GET', data = null, params = {}) {
    const config = { params };
    
    switch (method.toUpperCase()) {
      case 'GET':
        return api.get(endpoint, config);
      case 'POST':
        return api.post(endpoint, data, config);
      case 'PUT':
        return api.put(endpoint, data, config);
      case 'DELETE':
        return api.delete(endpoint, config);
      default:
        throw new Error(`Unsupported HTTP method: ${method}`);
    }
  }
};

// Utility functions
export const apiUtils = {
  // Format error messages
  formatError(error) {
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    }
    if (error.response?.data?.message) {
      return error.response.data.message;
    }
    if (error.message) {
      return error.message;
    }
    return 'An unexpected error occurred';
  },

  // Check if API is available
  async checkApiHealth() {
    try {
      await apiService.getHealth();
      return true;
    } catch (error) {
      return false;
    }
  },

  // Retry failed requests
  async retryRequest(requestFn, maxRetries = 3, delay = 1000) {
    for (let i = 0; i < maxRetries; i++) {
      try {
        return await requestFn();
      } catch (error) {
        if (i === maxRetries - 1) throw error;
        await new Promise(resolve => setTimeout(resolve, delay * (i + 1)));
      }
    }
  }
};

export default apiService;