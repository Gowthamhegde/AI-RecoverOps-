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
        type: 'High CPU',
        service: 'web-server-prod',
        severity: 'critical',
        status: 'resolved',
        confidence: 0.94,
        action: 'restart_service',
        timestamp: '2024-01-15 10:30:00',
        resolutionTime: 145,
      },
      {
        id: 'INC-002',
        type: 'Memory Leak',
        service: 'api-gateway',
        severity: 'high',
        status: 'investigating',
        confidence: 0.87,
        action: 'restart_service',
        timestamp: '2024-01-15 10:25:00',
        resolutionTime: null,
      },
      {
        id: 'INC-003',
        type: 'Disk Full',
        service: 'database-primary',
        severity: 'medium',
        status: 'resolved',
        confidence: 0.92,
        action: 'clean_logs',
        timestamp: '2024-01-15 10:20:00',
        resolutionTime: 89,
      },
    ],
  };

  const data = dashboardData || mockData;

  const incidentColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 100,
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      render: (type) => (
        <Tag color="blue">{type}</Tag>
      ),
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
        const icons = {
          resolved: <CheckCircleOutlined />,
          investigating: <ClockCircleOutlined />,
          open: <AlertOutlined />,
        };
        const colors = {
          resolved: 'green',
          investigating: 'blue',
          open: 'red',
        };
        return (
          <Tag icon={icons[status]} color={colors[status]}>
            {status.toUpperCase()}
          </Tag>
        );
      },
    },
    {
      title: 'Confidence',
      dataIndex: 'confidence',
      key: 'confidence',
      render: (confidence) => (
        <Progress
          percent={Math.round(confidence * 100)}
          size="small"
          status={confidence > 0.8 ? 'success' : 'normal'}
        />
      ),
    },
    {
      title: 'Action',
      dataIndex: 'action',
      key: 'action',
      render: (action) => (
        <Tag icon={<RobotOutlined />} color="purple">
          {action.replace('_', ' ')}
        </Tag>
      ),
    },
    {
      title: 'Resolution Time',
      dataIndex: 'resolutionTime',
      key: 'resolutionTime',
      render: (time) => time ? `${time}s` : '-',
    },
  ];

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  return (
    <div>
      {/* System Status Alert */}
      <Alert
        message="AI-RecoverOps System Status"
        description={`System is operating normally. ${data.stats.activeIncidents} active incidents being monitored across ${47} services.`}
        type="success"
        showIcon
        style={{ marginBottom: 24 }}
        action={
          <Button size="small" type="primary">
            View Details
          </Button>
        }
      />

      {/* Key Metrics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Incidents"
              value={data.stats.totalIncidents}
              prefix={<AlertOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Active Incidents"
              value={data.stats.activeIncidents}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Resolved Today"
              value={data.stats.resolvedToday}
              prefix={<CheckCircleOutlined />}
              suffix={<ArrowUpOutlined style={{ color: '#52c41a' }} />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Auto-Remediation Rate"
              value={data.stats.autoRemediationRate}
              precision={1}
              suffix="%"
              prefix={<RobotOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Performance Metrics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={12}>
          <Card>
            <Statistic
              title="Avg Resolution Time"
              value={formatTime(data.stats.avgResolutionTime)}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
            <Progress
              percent={85}
              strokeColor="#52c41a"
              format={() => '15% faster than last month'}
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card>
            <Statistic
              title="System Health Score"
              value={data.stats.systemHealth}
              precision={1}
              suffix="/100"
              valueStyle={{ color: '#52c41a' }}
            />
            <Progress
              percent={data.stats.systemHealth}
              strokeColor="#52c41a"
              format={(percent) => `${percent}%`}
            />
          </Card>
        </Col>
      </Row>

      {/* Charts */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={16}>
          <Card title="Incident Trends (Last 24 Hours)" style={{ height: 400 }}>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={data.incidentTrends}>
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
                  fillOpacity={0.6}
                  name="New Incidents"
                />
                <Area
                  type="monotone"
                  dataKey="resolved"
                  stackId="2"
                  stroke="#52c41a"
                  fill="#52c41a"
                  fillOpacity={0.6}
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
                  data={data.incidentTypes}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {data.incidentTypes.map((entry, index) => (
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
          dataSource={data.recentIncidents}
          rowKey="id"
          pagination={false}
          size="small"
        />
      </Card>

      {/* Quick Actions */}
      <Card title="Quick Actions">
        <Space wrap>
          <Button type="primary" icon={<AlertOutlined />}>
            View All Incidents
          </Button>
          <Button icon={<RobotOutlined />}>
            ML Model Status
          </Button>
          <Button icon={<CheckCircleOutlined />}>
            System Health Check
          </Button>
          <Button icon={<ClockCircleOutlined />}>
            Performance Report
          </Button>
        </Space>
      </Card>
    </div>
  );
};

export default Dashboard;