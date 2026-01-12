import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Progress, Table, Tag, Button, Space, Alert } from 'antd';
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  AlertOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  RobotOutlined,
} from '@ant-design/icons';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { useQuery } from 'react-query';
import toast from 'react-hot-toast';

const Dashboard = ({ socket }) => {
  const [realtimeData, setRealtimeData] = useState({
    incidents: [],
    metrics: {},
  });

  // Fetch dashboard data
  const { data: dashboardData, isLoading } = useQuery(
    'dashboard',
    async () => {
      const response = await fetch('/api/dashboard');
      if (!response.ok) {
        throw new Error('Failed to fetch dashboard data');
      }
      return response.json();
    },
    {
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  );

  // Listen for real-time updates
  useEffect(() => {
    if (socket) {
      socket.on('incident_update', (data) => {
        setRealtimeData(prev => ({
          ...prev,
          incidents: [data, ...prev.incidents.slice(0, 9)],
        }));
        
        if (data.severity === 'critical') {
          toast.error(`Critical incident detected: ${data.type}`);
        }
      });

      socket.on('remediation_success', (data) => {
        toast.success(`Auto-remediation successful: ${data.action}`);
      });

      socket.on('remediation_failed', (data) => {
        toast.error(`Auto-remediation failed: ${data.action}`);
      });
    }

    return () => {
      if (socket) {
        socket.off('incident_update');
        socket.off('remediation_success');
        socket.off('remediation_failed');
      }
    };
  }, [socket]);

  // Mock data for demonstration
  const mockData = {
    stats: {
      totalIncidents: 156,
      activeIncidents: 12,
      resolvedToday: 23,
      autoRemediationRate: 78.5,
      avgResolutionTime: 245, // seconds
      systemHealth: 94.2,
    },
    incidentTrends: [
      { time: '00:00', incidents: 2, resolved: 1 },
      { time: '04:00', incidents: 1, resolved: 3 },
      { time: '08:00', incidents: 8, resolved: 6 },
      { time: '12:00', incidents: 12, resolved: 10 },
      { time: '16:00', incidents: 6, resolved: 8 },
      { time: '20:00', incidents: 4, resolved: 5 },
    ],
    incidentTypes: [
      { name: 'High CPU', value: 35, color: '#ff4d4f' },
      { name: 'Memory Leak', value: 28, color: '#faad14' },
      { name: 'Disk Full', value: 20, color: '#1890ff' },
      { name: 'Network Issues', value: 17, color: '#52c41a' },
    ],
    recentIncidents: [
      {
        id: 'INC-001',
        type: 'high_cpu',
        service: 'web-server',
        severity: 'critical',
        status: 'resolved',
        timestamp: '2024-01-15 14:30:00',
        confidence: 0.94,
      },
      {
        id: 'INC-002',
        type: 'memory_leak',
        service: 'api-service',
        severity: 'high',
        status: 'investigating',
        timestamp: '2024-01-15 14:25:00',
        confidence: 0.87,
      },
    ],
  };

  // Use dashboardData if available, otherwise use mockData
  const data = dashboardData || mockData;

  // Helper function to format time
  const formatTime = (seconds) => {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
  };

  // Table columns for recent incidents
  const incidentColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 120,
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      render: (type) => type.replace('_', ' ').toUpperCase(),
    },
    {
      title: 'Service',
      dataIndex: 'service',
      key: 'service',
    },
    {
      title: 'Severity',
      dataIndex: 'severity',
      key: 'severity',
      render: (severity) => {
        const colors = {
          critical: 'red',
          high: 'orange',
          medium: 'yellow',
          low: 'green',
        };
        return <Tag color={colors[severity]}>{severity.toUpperCase()}</Tag>;
      },
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const colors = {
          open: 'red',
          investigating: 'orange',
          resolved: 'green',
        };
        return <Tag color={colors[status]}>{status.toUpperCase()}</Tag>;
      },
    },
    {
      title: 'Confidence',
      dataIndex: 'confidence',
      key: 'confidence',
      render: (confidence) => `${(confidence * 100).toFixed(1)}%`,
    },
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
    },
  ];

  if (isLoading) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <Card>
          <p>Loading dashboard data...</p>
        </Card>
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      {/* System Status Alert */}
      <Alert
        message="AI-RecoverOps System Status"
        description={`System is operating normally. ${data.stats?.activeIncidents || 0} active incidents being monitored across ${47} services.`}
        type="success"
        showIcon
        style={{ marginBottom: 24 }}
      />

      {/* Key Metrics Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={8} lg={4}>
          <Card>
            <Statistic
              title="Total Incidents"
              value={data.stats?.totalIncidents || 0}
              prefix={<AlertOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={4}>
          <Card>
            <Statistic
              title="Active Incidents"
              value={data.stats?.activeIncidents || 0}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={4}>
          <Card>
            <Statistic
              title="Resolved Today"
              value={data.stats?.resolvedToday || 0}
              prefix={<CheckCircleOutlined />}
              suffix={<ArrowUpOutlined style={{ color: '#52c41a' }} />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={4}>
          <Card>
            <Statistic
              title="Auto-Remediation Rate"
              value={data.stats?.autoRemediationRate || 0}
              precision={1}
              suffix="%"
              prefix={<RobotOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={4}>
          <Card>
            <Statistic
              title="Avg Resolution Time"
              value={formatTime(data.stats?.avgResolutionTime || 0)}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={4}>
          <Card>
            <Statistic
              title="System Health Score"
              value={data.stats?.systemHealth || 0}
              precision={1}
              suffix="/100"
              valueStyle={{ color: '#52c41a' }}
            />
            <Progress
              percent={data.stats?.systemHealth || 0}
              strokeColor="#52c41a"
              format={(percent) => `${percent}%`}
            />
          </Card>
        </Col>
      </Row>

      {/* Charts Row */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={16}>
          <Card title="Incident Trends (Last 24 Hours)" style={{ height: 400 }}>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={data.incidentTrends || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="incidents"
                  stackId="1"
                  stroke="#ff4d4f"
                  fill="#ff4d4f"
                  name="New Incidents"
                />
                <Area
                  type="monotone"
                  dataKey="resolved"
                  stackId="2"
                  stroke="#52c41a"
                  fill="#52c41a"
                  name="Resolved"
                />
              </AreaChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Incident Types Distribution" style={{ height: 400 }}>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={data.incidentTypes || []}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {(data.incidentTypes || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Recent Incidents Table */}
      <Card title="Recent Incidents" style={{ marginBottom: 24 }}>
        <Table
          columns={incidentColumns}
          dataSource={data.recentIncidents || []}
          rowKey="id"
          pagination={false}
          size="small"
        />
      </Card>

      {/* Action Buttons */}
      <Row gutter={[16, 16]}>
        <Col>
          <Button type="primary" icon={<AlertOutlined />}>
            View All Incidents
          </Button>
        </Col>
        <Col>
          <Button icon={<RobotOutlined />}>
            Configure Auto-Remediation
          </Button>
        </Col>
        <Col>
          <Button icon={<CheckCircleOutlined />}>
            System Health Report
          </Button>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;