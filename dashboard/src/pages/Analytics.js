import React, { useState } from 'react';
import { Card, Row, Col, Statistic, DatePicker, Select, Space } from 'antd';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import {
  TrendingUpOutlined,
  TrendingDownOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';

const { RangePicker } = DatePicker;
const { Option } = Select;

const Analytics = () => {
  const [timeRange, setTimeRange] = useState('7d');
  const [selectedMetric, setSelectedMetric] = useState('incidents');

  // Mock analytics data
  const performanceData = [
    { date: '2024-01-08', incidents: 12, resolved: 10, mttr: 145 },
    { date: '2024-01-09', incidents: 8, resolved: 7, mttr: 132 },
    { date: '2024-01-10', incidents: 15, resolved: 13, mttr: 167 },
    { date: '2024-01-11', incidents: 6, resolved: 6, mttr: 98 },
    { date: '2024-01-12', incidents: 11, resolved: 9, mttr: 156 },
    { date: '2024-01-13', incidents: 9, resolved: 8, mttr: 143 },
    { date: '2024-01-14', incidents: 14, resolved: 12, mttr: 178 },
  ];

  const incidentTypesTrend = [
    { month: 'Oct', high_cpu: 45, memory_leak: 32, disk_full: 28, network: 15 },
    { month: 'Nov', high_cpu: 38, memory_leak: 28, disk_full: 25, network: 12 },
    { month: 'Dec', high_cpu: 42, memory_leak: 35, disk_full: 22, network: 18 },
    { month: 'Jan', high_cpu: 35, memory_leak: 28, disk_full: 20, network: 17 },
  ];

  const remediationSuccess = [
    { action: 'Restart Service', success: 95, failed: 5 },
    { action: 'Clean Logs', success: 98, failed: 2 },
    { action: 'Scale Horizontally', success: 87, failed: 13 },
    { action: 'Fix Permissions', success: 76, failed: 24 },
    { action: 'Restart Database', success: 83, failed: 17 },
  ];

  const costSavings = [
    { month: 'Oct', manual_cost: 15000, automated_cost: 3200, savings: 11800 },
    { month: 'Nov', manual_cost: 18000, automated_cost: 3800, savings: 14200 },
    { month: 'Dec', manual_cost: 16500, automated_cost: 3500, savings: 13000 },
    { month: 'Jan', manual_cost: 14000, automated_cost: 2800, savings: 11200 },
  ];

  const colors = ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1'];

  return (
    <div>
      {/* Controls */}
      <Card style={{ marginBottom: 24 }}>
        <Space>
          <Select
            value={timeRange}
            onChange={setTimeRange}
            style={{ width: 120 }}
          >
            <Option value="7d">Last 7 days</Option>
            <Option value="30d">Last 30 days</Option>
            <Option value="90d">Last 90 days</Option>
          </Select>
          <RangePicker />
          <Select
            value={selectedMetric}
            onChange={setSelectedMetric}
            style={{ width: 150 }}
          >
            <Option value="incidents">Incidents</Option>
            <Option value="performance">Performance</Option>
            <Option value="costs">Cost Analysis</Option>
          </Select>
        </Space>
      </Card>

      {/* Key Performance Indicators */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="MTTR Improvement"
              value={75}
              precision={1}
              suffix="%"
              prefix={<TrendingDownOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
            <div style={{ fontSize: '12px', color: '#666' }}>
              vs. previous period
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Auto-Resolution Rate"
              value={78.5}
              precision={1}
              suffix="%"
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
            <div style={{ fontSize: '12px', color: '#666' }}>
              +5.2% from last month
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Cost Savings"
              value={12000}
              prefix="$"
              suffix="/month"
              valueStyle={{ color: '#52c41a' }}
            />
            <div style={{ fontSize: '12px', color: '#666' }}>
              Through automation
            </div>
          </Card>
        </Col>
        <Col xs={24} sm12 lg={6}>
          <Card>
            <Statistic
              title="False Positive Rate"
              value={2.1}
              precision={1}
              suffix="%"
              prefix={<TrendingDownOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
            <div style={{ fontSize: '12px', color: '#666' }}>
              ML model accuracy: 97.9%
            </div>
          </Card>
        </Col>
      </Row>

      {/* Performance Trends */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={16}>
          <Card title="Incident Resolution Performance">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                <Bar yAxisId="left" dataKey="incidents" fill="#ff4d4f" name="New Incidents" />
                <Bar yAxisId="left" dataKey="resolved" fill="#52c41a" name="Resolved" />
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="mttr"
                  stroke="#1890ff"
                  strokeWidth={3}
                  name="MTTR (seconds)"
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Remediation Success Rate">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={remediationSuccess} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="action" type="category" width={100} />
                <Tooltip />
                <Bar dataKey="success" stackId="a" fill="#52c41a" />
                <Bar dataKey="failed" stackId="a" fill="#ff4d4f" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Incident Types Analysis */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="Incident Types Trend">
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={incidentTypesTrend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="high_cpu"
                  stackId="1"
                  stroke={colors[0]}
                  fill={colors[0]}
                  name="High CPU"
                />
                <Area
                  type="monotone"
                  dataKey="memory_leak"
                  stackId="1"
                  stroke={colors[1]}
                  fill={colors[1]}
                  name="Memory Leak"
                />
                <Area
                  type="monotone"
                  dataKey="disk_full"
                  stackId="1"
                  stroke={colors[2]}
                  fill={colors[2]}
                  name="Disk Full"
                />
                <Area
                  type="monotone"
                  dataKey="network"
                  stackId="1"
                  stroke={colors[3]}
                  fill={colors[3]}
                  name="Network Issues"
                />
              </AreaChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Cost Analysis">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={costSavings}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
                <Legend />
                <Bar dataKey="manual_cost" fill="#ff4d4f" name="Manual Cost" />
                <Bar dataKey="automated_cost" fill="#1890ff" name="Automated Cost" />
                <Bar dataKey="savings" fill="#52c41a" name="Savings" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Detailed Metrics */}
      <Card title="Detailed Performance Metrics">
        <Row gutter={[16, 16]}>
          <Col xs={24} md={8}>
            <Card size="small" title="Resolution Time Distribution">
              <div style={{ textAlign: 'center' }}>
                <div>< 1 minute: <strong>45%</strong></div>
                <div>1-5 minutes: <strong>32%</strong></div>
                <div>5-15 minutes: <strong>18%</strong></div>
                <div>> 15 minutes: <strong>5%</strong></div>
              </div>
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card size="small" title="Top Affected Services">
              <div>
                <div>web-server-prod: <strong>28 incidents</strong></div>
                <div>api-gateway: <strong>22 incidents</strong></div>
                <div>database-primary: <strong>18 incidents</strong></div>
                <div>cache-service: <strong>15 incidents</strong></div>
                <div>worker-queue: <strong>12 incidents</strong></div>
              </div>
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card size="small" title="ML Model Performance">
              <div>
                <div>Accuracy: <strong>87.1%</strong></div>
                <div>Precision: <strong>89.3%</strong></div>
                <div>Recall: <strong>85.7%</strong></div>
                <div>F1-Score: <strong>87.4%</strong></div>
                <div>Last Updated: <strong>2 hours ago</strong></div>
              </div>
            </Card>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default Analytics;