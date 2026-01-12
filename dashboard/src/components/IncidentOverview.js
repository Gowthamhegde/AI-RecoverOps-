import React from 'react';
import { 
  ExclamationTriangleIcon, 
  FireIcon, 
  InformationCircleIcon,
  CheckCircleIcon 
} from '@heroicons/react/24/outline';

const IncidentOverview = ({ incidents }) => {
  // Calculate incident statistics
  const stats = incidents.reduce((acc, incident) => {
    const severity = incident.severity || 'medium';
    const status = incident.status || 'open';
    
    acc.total++;
    acc.bySeverity[severity] = (acc.bySeverity[severity] || 0) + 1;
    acc.byStatus[status] = (acc.byStatus[status] || 0) + 1;
    
    return acc;
  }, {
    total: 0,
    bySeverity: {},
    byStatus: {},
  });

  // Calculate incident types
  const incidentTypes = incidents.reduce((acc, incident) => {
    const type = incident.prediction?.incident_type || 'unknown';
    acc[type] = (acc[type] || 0) + 1;
    return acc;
  }, {});

  const topIncidentTypes = Object.entries(incidentTypes)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 5);

  // Calculate remediation success rate
  const remediatedIncidents = incidents.filter(i => i.remediation_status === 'completed');
  const successfulRemediations = remediatedIncidents.filter(i => i.remediation_success);
  const successRate = remediatedIncidents.length > 0 
    ? (successfulRemediations.length / remediatedIncidents.length * 100).toFixed(1)
    : 0;

  const StatCard = ({ title, value, icon: Icon, color, subtitle }) => (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center">
        <div className={`flex-shrink-0 p-3 rounded-md ${color}`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
        <div className="ml-4">
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className="text-2xl font-semibold text-gray-900">{value}</p>
          {subtitle && (
            <p className="text-sm text-gray-600">{subtitle}</p>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Incident Overview
        </h2>
        
        {/* Main Statistics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <StatCard
            title="Total Incidents"
            value={stats.total}
            icon={ExclamationTriangleIcon}
            color="bg-blue-500"
          />
          <StatCard
            title="Critical"
            value={stats.bySeverity.critical || 0}
            icon={FireIcon}
            color="bg-red-500"
          />
          <StatCard
            title="High Priority"
            value={stats.bySeverity.high || 0}
            icon={ExclamationTriangleIcon}
            color="bg-orange-500"
          />
          <StatCard
            title="Resolved"
            value={stats.byStatus.resolved || 0}
            icon={CheckCircleIcon}
            color="bg-green-500"
          />
        </div>

        {/* Remediation Success Rate */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              Auto-Remediation Success Rate
            </span>
            <span className="text-sm text-gray-500">
              {successfulRemediations.length}/{remediatedIncidents.length} successful
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-green-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${successRate}%` }}
            ></div>
          </div>
          <div className="text-right mt-1">
            <span className="text-lg font-semibold text-green-600">
              {successRate}%
            </span>
          </div>
        </div>

        {/* Top Incident Types */}
        <div>
          <h3 className="text-md font-medium text-gray-900 mb-3">
            Top Incident Types
          </h3>
          <div className="space-y-2">
            {topIncidentTypes.map(([type, count]) => (
              <div key={type} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-blue-500 rounded-full mr-3"></div>
                  <span className="text-sm text-gray-700 capitalize">
                    {type.replace(/_/g, ' ')}
                  </span>
                </div>
                <div className="flex items-center">
                  <span className="text-sm font-medium text-gray-900 mr-2">
                    {count}
                  </span>
                  <div className="w-16 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ 
                        width: `${(count / stats.total * 100)}%` 
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Severity Distribution Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-md font-medium text-gray-900 mb-4">
          Severity Distribution
        </h3>
        <div className="grid grid-cols-3 gap-4">
          {[
            { severity: 'critical', color: 'bg-red-500', label: 'Critical' },
            { severity: 'high', color: 'bg-orange-500', label: 'High' },
            { severity: 'medium', color: 'bg-yellow-500', label: 'Medium' }
          ].map(({ severity, color, label }) => {
            const count = stats.bySeverity[severity] || 0;
            const percentage = stats.total > 0 ? (count / stats.total * 100).toFixed(1) : 0;
            
            return (
              <div key={severity} className="text-center">
                <div className={`${color} rounded-lg p-4 mb-2`}>
                  <div className="text-white text-2xl font-bold">{count}</div>
                </div>
                <div className="text-sm text-gray-600">{label}</div>
                <div className="text-xs text-gray-500">{percentage}%</div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default IncidentOverview;