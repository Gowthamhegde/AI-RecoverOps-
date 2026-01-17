import React, { useState, useEffect } from 'react';
import { 
  Row, 
  Col, 
  Card, 
  Statistic, 
  Progress, 
  Timeline, 
  Table, 
  Tag, 
  Button,
  Alert,
  Spin,
  Typography,
  Space,
  Tooltip
} from 'antd';
import {
  BugOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  RobotOutlined,
  ThunderboltOutlined,
  HeartOutlined,
  AlertOutlined,
  ToolOutlined
} from '@ant-design/icons';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { useQuery } from 'react-query';
import moment from 'moment';

import { apiService } from '../services/apiService';

const { Title, Text } = Typography;

const Dashboard = ({ socket, realTimeData, systemStatus }) => {
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState({
    stats: {
      totalIncidents: 0,
      activeIncidents: 0,
      resolvedToday: 0,
      autoRemediationRate: 0,
      avgResolutionTime: 0,
      systemHealth: 0
    },
    recentIncidents: [],
    trends: [],
    topFailures: []
  });

  // Fetch dashboard data
  const { data: stats, isLoading: statsLoading } = useQuery(
    'dashboard-stats',
    apiService.getDashboardData,
    {
      refetchInterval: 30000, // Refresh every 30 seconds
      onSuccess: (data) => {
        setDashboardData(prev => ({
          ...prev,
          stats: data.stats,
          recentIncidents: data.recentIncidents || []
        }));
      }
    }
  );

  // Fetch incident trends
  const { data: trends } = useQuery(
    'incident-trends',
    () => apiService.getIncidentTrends(7), // Last 7 days
    {
      refetchInterval: 60000, // Refresh every minute
      onSuccess: (data) => {
        setDashboardData(prev => ({
          ...prev,
          trends: data || []
        }));
      }
    }
  );

  useEffect(() => {
    setLoading(statsLoading);
  }, [statsLoading]);

  // Real-time updates from WebSocket
  useEffect(() => {
    if (realTimeData.activeIncidents.length > 0) {
      setDashboardData(prev => ({
        ...prev,
        stats: {
          ...prev.stats,
          activeIncidents: realTimeData.activeIncidents.length
        }
      }));
    }
  }, [realTimeData.activeIncidents]);

  // Status color mapping
  const getStatusColor = (status) => {
    const colors = {
      'detected': '#faad14',
      'analyzing': '#1890ff',
      'fixing': '#722ed1',
      'resolved': '#52c41a',
      'failed': '#ff4d4f'
    };
    return colors[status] || '#d9d9d9';
  };

  // Severity color mapping
  const getSeverityColor = (severity) => {
    const colors = {
      'low': '#52c41a',
      'medium': '#faad14',
      'high': '#ff7a45',
      'critical': '#ff4d4f'
    };
    return colors[severity] || '#d9d9d9';
  };

  // Chart colors
  const chartColors = ['#1890ff', '#52c41a', '#faad14', '#ff4d4f', '#722ed1'];

  // Incident table columns
  const incidentColumns = [
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
      render: (text, record) => (
        <Space direction="vertical" size={0}>
          <Text strong>{text}</Text>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            {record.repository} • {record.branch}
          </Text>
        </Space>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={getStatusColor(status)}>
          {status.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Severity',
      dataIndex: 'severity',
      key: 'severity',
      render: (severity) => (
        <Tag color={getSeverityColor(severity)}>
          {severity.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Detected',
      dataIndex: 'detected_at',
      key: 'detected_at',
      render: (date) => moment(date).fromNow(),
    },
  ];

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <div style={{ marginTop: '20px' }}>
          <Text>Loading AI-RecoverOps Dashboard...</Text>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>
          <RobotOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
          AI-RecoverOps Dashboard
        </Title>
        <Text type="secondary">
          Real-time DevOps recovery monitoring and automation
        </Text>
      </div>

      {/* System Status Alert */}
      {systemStatus.status !== 'healthy' && (
        <Alert
          message="System Status Warning"
          description={`AI-RecoverOps is currently ${systemStatus.status}. Some features may be limited.`}
          type="warning"
          showIcon
          closable
          style={{ marginBottom: '24px' }}
        />
      )}

      {/* Key Metrics */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Active Incidents"
              value={dashboardData.stats.activeIncidents}
              prefix={<BugOutlined style={{ color: '#ff4d4f' }} />}
              valueStyle={{ color: dashboardData.stats.activeIncidents > 0 ? '#ff4d4f' : '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Resolved Today"
              value={dashboardData.stats.resolvedToday}
              prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Auto-Remediation Rate"
              value={dashboardData.stats.autoRemediationRate}
              suffix="%"
              prefix={<RobotOutlined style={{ color: '#1890ff' }} />}
              valueStyle={{ color: '#1890ff' }}
            />
            <Progress 
              percent={dashboardData.stats.autoRemediationRate} 
              showInfo={false} 
              strokeColor="#1890ff"
              size="small"
              style={{ marginTop: '8px' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="System Health"
              value={dashboardData.stats.systemHealth}
              suffix="%"
              prefix={<HeartOutlined style={{ color: '#52c41a' }} />}
              valueStyle={{ color: '#52c41a' }}
            />
            <Progress 
              percent={dashboardData.stats.systemHealth} 
              showInfo={false} 
              strokeColor="#52c41a"
              size="small"
              style={{ marginTop: '8px' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Charts Row */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} lg={16}>
          <Card title="Incident Trends (Last 7 Days)" extra={<ThunderboltOutlined />}>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={dashboardData.trends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <RechartsTooltip />
                <Line 
                  type="monotone" 
                  dataKey="incidents" 
                  stroke="#1890ff" 
                  strokeWidth={2}
                  dot={{ fill: '#1890ff', strokeWidth: 2, r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Resolution Time" extra={<ClockCircleOutlined />}>
            <div style={{ textAlign: 'center', padding: '20px' }}>
              <Statistic
                title="Average Resolution Time"
                value={dashboardData.stats.avgResolutionTime}
                suffix="min"
                valueStyle={{ fontSize: '32px', color: '#1890ff' }}
              />
              <div style={{ marginTop: '20px' }}>
                <Text type="secondary">
                  {dashboardData.stats.avgResolutionTime < 300 ? '🚀 Excellent' : 
                   dashboardData.stats.avgResolutionTime < 600 ? '✅ Good' : 
                   '⚠️ Needs Improvement'}
                </Text>
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Real-time Activity and Recent Incidents */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card 
            title="Real-time Activity" 
            extra={
              <Space>
                <div style={{ 
                  width: '8px', 
                  height: '8px', 
                  borderRadius: '50%', 
                  backgroundColor: socket?.connected ? '#52c41a' : '#ff4d4f',
                  display: 'inline-block'
                }} />
                <Text type="secondary">
                  {socket?.connected ? 'Live' : 'Disconnected'}
                </Text>
              </Space>
            }
          >
            <Timeline
              mode="left"
              style={{ maxHeight: '400px', overflowY: 'auto' }}
            >
              {realTimeData.recentEvents.slice(0, 10).map((event, index) => {
                const getTimelineColor = (type) => {
                  switch (type) {
                    case 'incident': return 'red';
                    case 'resolution': return 'green';
                    case 'remediation': return 'blue';
                    case 'pipeline': return 'orange';
                    default: return 'gray';
                  }
                };

                const getTimelineIcon = (type) => {
                  switch (type) {
                    case 'incident': return <AlertOutlined />;
                    case 'resolution': return <CheckCircleOutlined />;
                    case 'remediation': return <ToolOutlined />;
                    case 'pipeline': return <ThunderboltOutlined />;
                    default: return <ClockCircleOutlined />;
                  }
                };

                return (
                  <Timeline.Item
                    key={index}
                    color={getTimelineColor(event.type)}
                    dot={getTimelineIcon(event.type)}
                  >
                    <div>
                      <Text strong>{event.data.title || event.data.description}</Text>
                      <br />
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        {moment(event.timestamp).fromNow()}
                      </Text>
                    </div>
                  </Timeline.Item>
                );
              })}
              {realTimeData.recentEvents.length === 0 && (
                <Timeline.Item color="gray">
                  <Text type="secondary">No recent activity</Text>
                </Timeline.Item>
              )}
            </Timeline>
          </Card>
        </Col>
        
        <Col xs={24} lg={12}>
          <Card 
            title="Recent Incidents" 
            extra={
              <Button 
                type="primary" 
                size="small"
                onClick={() => window.location.href = '/incidents'}
              >
                View All
              </Button>
            }
          >
            <Table
              dataSource={dashboardData.recentIncidents}
              columns={incidentColumns}
              pagination={false}
              size="small"
              scroll={{ y: 350 }}
              rowKey="id"
            />
          </Card>
        </Col>
      </Row>

      {/* System Metrics */}
      {realTimeData.systemMetrics && Object.keys(realTimeData.systemMetrics).length > 0 && (
        <Row gutter={[16, 16]} style={{ marginTop: '24px' }}>
          <Col span={24}>
            <Card title="System Metrics" extra={<HeartOutlined />}>
              <Row gutter={[16, 16]}>
                <Col xs={24} sm={8}>
                  <div style={{ textAlign: 'center' }}>
                    <Progress
                      type="circle"
                      percent={Math.round(realTimeData.systemMetrics.cpu_usage || 0)}
                      format={percent => `${percent}%`}
                      strokeColor="#1890ff"
                    />
                    <div style={{ marginTop: '8px' }}>
                      <Text>CPU Usage</Text>
                    </div>
                  </div>
                </Col>
                <Col xs={24} sm={8}>
                  <div style={{ textAlign: 'center' }}>
                    <Progress
                      type="circle"
                      percent={Math.round(realTimeData.systemMetrics.memory_usage || 0)}
                      format={percent => `${percent}%`}
                      strokeColor="#52c41a"
                    />
                    <div style={{ marginTop: '8px' }}>
                      <Text>Memory Usage</Text>
                    </div>
                  </div>
                </Col>
                <Col xs={24} sm={8}>
                  <div style={{ textAlign: 'center' }}>
                    <Progress
                      type="circle"
                      percent={Math.round(realTimeData.systemMetrics.disk_usage || 0)}
                      format={percent => `${percent}%`}
                      strokeColor="#faad14"
                    />
                    <div style={{ marginTop: '8px' }}>
                      <Text>Disk Usage</Text>
                    </div>
                  </div>
                </Col>
              </Row>
            </Card>
          </Col>
        </Row>
      )}
    </div>
  );
};

export default Dashboard;