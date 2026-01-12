import React, { useState, useEffect } from 'react';
import { Card, Table, Input, Select, Button, Tag, Space, DatePicker, message } from 'antd';
import { SearchOutlined, ReloadOutlined, DownloadOutlined } from '@ant-design/icons';
import { apiService } from '../services/apiService';

const { Search } = Input;
const { Option } = Select;
const { RangePicker } = DatePicker;

const Logs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    service: 'all',
    logLevel: 'all',
    timeRange: null
  });

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      // Generate mock logs for demonstration
      const mockLogs = generateMockLogs();
      setLogs(mockLogs);
    } catch (error) {
      message.error('Failed to fetch logs');
    } finally {
      setLoading(false);
    }
  };

  const generateMockLogs = () => {
    const services = ['web-server', 'api-service', 'database', 'cache-service', 'worker'];
    const logLevels = ['INFO', 'WARN', 'ERROR', 'DEBUG'];
    const messages = [
      'Request processed successfully',
      'High CPU usage detected',
      'Memory usage at 85%',
      'Database connection established',
      'Cache miss for key: user_123',
      'Authentication successful',
      'File upload completed',
      'Backup process started',
      'Configuration updated',
      'Service health check passed'
    ];

    const logs = [];
    const now = new Date();

    for (let i = 0; i < 100; i++) {
      const timestamp = new Date(now.getTime() - Math.random() * 24 * 60 * 60 * 1000);
      const service = services[Math.floor(Math.random() * services.length)];
      const logLevel = logLevels[Math.floor(Math.random() * logLevels.length)];
      const message = messages[Math.floor(Math.random() * messages.length)];

      logs.push({
        id: `log-${i + 1}`,
        timestamp: timestamp.toISOString(),
        service,
        logLevel,
        message,
        instanceId: `i-${Math.random().toString(36).substr(2, 9)}`,
        region: 'us-east-1',
        environment: 'production'
      });
    }

    return logs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  };

  const handleSearch = (value) => {
    if (value) {
      const filtered = logs.filter(log => 
        log.message.toLowerCase().includes(value.toLowerCase()) ||
        log.service.toLowerCase().includes(value.toLowerCase())
      );
      setLogs(filtered);
    } else {
      fetchLogs();
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const getLogLevelColor = (level) => {
    const colors = {
      ERROR: 'red',
      WARN: 'orange',
      INFO: 'blue',
      DEBUG: 'gray'
    };
    return colors[level] || 'default';
  };

  const columns = [
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 180,
      render: (timestamp) => new Date(timestamp).toLocaleString(),
      sorter: (a, b) => new Date(a.timestamp) - new Date(b.timestamp),
    },
    {
      title: 'Service',
      dataIndex: 'service',
      key: 'service',
      width: 120,
      filters: [
        { text: 'Web Server', value: 'web-server' },
        { text: 'API Service', value: 'api-service' },
        { text: 'Database', value: 'database' },
        { text: 'Cache Service', value: 'cache-service' },
        { text: 'Worker', value: 'worker' },
      ],
      onFilter: (value, record) => record.service === value,
    },
    {
      title: 'Level',
      dataIndex: 'logLevel',
      key: 'logLevel',
      width: 80,
      render: (level) => (
        <Tag color={getLogLevelColor(level)}>{level}</Tag>
      ),
      filters: [
        { text: 'ERROR', value: 'ERROR' },
        { text: 'WARN', value: 'WARN' },
        { text: 'INFO', value: 'INFO' },
        { text: 'DEBUG', value: 'DEBUG' },
      ],
      onFilter: (value, record) => record.logLevel === value,
    },
    {
      title: 'Message',
      dataIndex: 'message',
      key: 'message',
      ellipsis: true,
    },
    {
      title: 'Instance',
      dataIndex: 'instanceId',
      key: 'instanceId',
      width: 120,
      ellipsis: true,
    },
    {
      title: 'Region',
      dataIndex: 'region',
      key: 'region',
      width: 100,
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card 
        title="System Logs" 
        extra={
          <Space>
            <Button 
              icon={<ReloadOutlined />} 
              onClick={fetchLogs}
              loading={loading}
            >
              Refresh
            </Button>
            <Button icon={<DownloadOutlined />}>
              Export
            </Button>
          </Space>
        }
      >
        <Space style={{ marginBottom: 16, width: '100%' }} direction="vertical">
          <Space wrap>
            <Search
              placeholder="Search logs..."
              allowClear
              enterButton={<SearchOutlined />}
              size="large"
              onSearch={handleSearch}
              style={{ width: 300 }}
            />
            
            <Select
              placeholder="Service"
              style={{ width: 150 }}
              value={filters.service}
              onChange={(value) => handleFilterChange('service', value)}
            >
              <Option value="all">All Services</Option>
              <Option value="web-server">Web Server</Option>
              <Option value="api-service">API Service</Option>
              <Option value="database">Database</Option>
              <Option value="cache-service">Cache Service</Option>
              <Option value="worker">Worker</Option>
            </Select>

            <Select
              placeholder="Log Level"
              style={{ width: 120 }}
              value={filters.logLevel}
              onChange={(value) => handleFilterChange('logLevel', value)}
            >
              <Option value="all">All Levels</Option>
              <Option value="ERROR">ERROR</Option>
              <Option value="WARN">WARN</Option>
              <Option value="INFO">INFO</Option>
              <Option value="DEBUG">DEBUG</Option>
            </Select>

            <RangePicker
              showTime
              onChange={(dates) => handleFilterChange('timeRange', dates)}
            />
          </Space>
        </Space>

        <Table
          columns={columns}
          dataSource={logs}
          rowKey="id"
          loading={loading}
          pagination={{
            total: logs.length,
            pageSize: 50,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => 
              `${range[0]}-${range[1]} of ${total} logs`,
          }}
          scroll={{ x: 1200 }}
          size="small"
        />
      </Card>
    </div>
  );
};

export default Logs;