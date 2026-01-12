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
  ArrowUpOutlined,
  ArrowDownOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';

const { RangePicker } = DatePicker;
const { Option } = Select;

const Analytics = () => {
  const [timeRange, setTimeRange] = useState('24h');

  // Mock data for charts
  const incidentTrendData = [
    { time: '00:00', high_cpu: 4, memory_leak: 2, disk_full: 1, network: 3 },
    { time: '04:00', high_cpu: 3, memory_leak: 1, disk_full: 2, network: 2 },
    { time: '08:00', high_cpu: 7, memory_leak: 4, disk_full: 1, network: 5 },
    { time: '12:00', high_cpu: 5, memory_leak: 3, disk_full: 3, network: 4 },
    { time: '16:00', high_cpu: 8, memory_leak: 2, disk_full: 2, network: 6 },
    { time: '20:00', high_cpu: 6, memory_leak: 5, disk_full: 1, network: 3 },
  ];

  const resolutionTimeData = [
    { name: 'Under 1 min', value: 45, color: '#52c41a' },
    { name: '1-5 min', value: 32, color: '#1890ff' },
    { name: '5-15 min', value: 18, color: '#faad14' },
    { name: 'Over 15 min', value: 5, color: '#ff4d4f' },
  ];

  const servicePerformanceData = [
    { service: 'web-server', incidents: 45, resolved: 42, success_rate: 93.3 },
    { service: 'api-service', incidents: 38, resolved: 35, success_rate: 92.1 },
    { service: 'database', incidents: 32, resolved: 30, success_rate: 93.8 },
    { service: 'cache-service', incidents: 25, resolved: 23, success_rate: 92.0 },
    { service: 'worker', incidents: 16, resolved: 12, success_rate: 75.0 },
  ];

  const colors = ['#1890ff', '#52c41a', '#faad14', '#ff4d4f', '#722ed1'];

  return (
    <div style={{ padding: '24px' }}>
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <Card>
            <Space>
              <span>Time Range:</span>
              <Select
                value={timeRange}
                onChange={setTimeRange}
                style={{ width: 120 }}
              >
                <Option value="1h">Last Hour</Option>
                <Option value="24h">Last 24h</Option>
                <Option value="7d">Last 7 days</Option>
                <Option value="30d">Last 30 days</Option>
              </Select>
              <RangePicker showTime />
            </Space>
          </Card>
        </Col>
      </Row>

      {/* Key Metrics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Total Incidents"
              value={156}
              prefix={<ArrowUpOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Auto-Resolved"
              value={142}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
              suffix="/ 156"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Avg Resolution Time"
              value={245}
              prefix={<ClockCircleOutlined />}
              suffix="sec"
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Success Rate"
              value={91.0}
              prefix={<ArrowUpOutlined />}
              suffix="%"
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Incident Trends */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <Card title="Incident Trends by Type">
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={incidentTrendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
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
      </Row>

      {/* Resolution Time and Service Performance */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="Resolution Time Distribution">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={resolutionTimeData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {resolutionTimeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Service Performance">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={servicePerformanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="service" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="incidents" fill={colors[0]} name="Total Incidents" />
                <Bar dataKey="resolved" fill={colors[1]} name="Resolved" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Additional Analytics */}
      <Row gutter={[16, 16]}>
        <Col xs={24} md={8}>
          <Card size="small" title="Resolution Time Distribution">
            <div style={{ textAlign: 'center' }}>
              <div>Under 1 minute: <strong>45%</strong></div>
              <div>1-5 minutes: <strong>32%</strong></div>
              <div>5-15 minutes: <strong>18%</strong></div>
              <div>Over 15 minutes: <strong>5%</strong></div>
            </div>
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card size="small" title="Top Affected Services">
            <div>
              <div>web-server: <strong>45 incidents</strong></div>
              <div>api-service: <strong>38 incidents</strong></div>
              <div>database: <strong>32 incidents</strong></div>
              <div>cache-service: <strong>25 incidents</strong></div>
            </div>
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card size="small" title="Auto-Remediation Success">
            <div style={{ textAlign: 'center' }}>
              <div>Successful: <strong>91.0%</strong></div>
              <div>Failed: <strong>6.4%</strong></div>
              <div>Manual: <strong>2.6%</strong></div>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Analytics;