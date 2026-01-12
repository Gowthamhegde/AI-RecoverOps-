import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Tag,
  Button,
  Space,
  Input,
  Select,
  DatePicker,
  Modal,
  Descriptions,
  Progress,
  Timeline,
  Alert,
  Drawer,
  Form,
  Switch,
  Divider,
} from 'antd';
import {
  SearchOutlined,
  ReloadOutlined,
  ExclamationCircleOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  AlertOutlined,
  RobotOutlined,
  EyeOutlined,
  PlayCircleOutlined,
  StopOutlined,
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import toast from 'react-hot-toast';
import moment from 'moment';

const { Search } = Input;
const { Option } = Select;
const { RangePicker } = DatePicker;
const { confirm } = Modal;

const Incidents = ({ socket }) => {
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [filters, setFilters] = useState({
    search: '',
    severity: 'all',
    status: 'all',
    dateRange: null,
  });

  const queryClient = useQueryClient();

  // Fetch incidents
  const { data: incidents, isLoading, refetch } = useQuery(
    ['incidents', filters],
    async () => {
      const params = new URLSearchParams();
      if (filters.search) params.append('search', filters.search);
      if (filters.severity !== 'all') params.append('severity', filters.severity);
      if (filters.status !== 'all') params.append('status', filters.status);
      if (filters.dateRange) {
        params.append('start_date', filters.dateRange[0].format('YYYY-MM-DD'));
        params.append('end_date', filters.dateRange[1].format('YYYY-MM-DD'));
      }

      const response = await fetch(`/api/incidents?${params}`);
      if (!response.ok) {
        throw new Error('Failed to fetch incidents');
      }
      return response.json();
    },
    {
      refetchInterval: 30000,
    }
  );

  // Remediation mutation
  const remediationMutation = useMutation(
    async ({ incidentId, action }) => {
      const response = await fetch(`/api/incidents/${incidentId}/remediate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action }),
      });
      if (!response.ok) {
        throw new Error('Failed to trigger remediation');
      }
      return response.json();
    },
    {
      onSuccess: (data, variables) => {
        toast.success(`Remediation triggered for incident ${variables.incidentId}`);
        queryClient.invalidateQueries('incidents');
      },
      onError: (error) => {
        toast.error(`Failed to trigger remediation: ${error.message}`);
      },
    }
  );

  // Status update mutation
  const statusMutation = useMutation(
    async ({ incidentId, status }) => {
      const response = await fetch(`/api/incidents/${incidentId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status }),
      });
      if (!response.ok) {
        throw new Error('Failed to update status');
      }
      return response.json();
    },
    {
      onSuccess: (data, variables) => {
        toast.success(`Incident ${variables.incidentId} status updated`);
        queryClient.invalidateQueries('incidents');
      },
      onError: (error) => {
        toast.error(`Failed to update status: ${error.message}`);
      },
    }
  );

  // Mock data for demonstration
  const mockIncidents = [
    {
      id: 'INC-2024-001',
      type: 'high_cpu',
      service: 'web-server-prod',
      instance: 'i-0abc123def456789',
      severity: 'critical',
      status: 'open',
      confidence: 0.94,
      recommendedAction: 'restart_service',
      timestamp: '2024-01-15T10:30:00Z',
      description: 'CPU usage exceeded 95% for 5 minutes on web-server-prod',
      metadata: {
        cpu_usage: 97.2,
        memory_usage: 68.5,
        disk_usage: 45.2,
        response_time: 2500,
      },
      timeline: [
        {
          timestamp: '2024-01-15T10:30:00Z',
          event: 'Incident detected',
          details: 'High CPU usage pattern identified by ML model',
        },
        {
          timestamp: '2024-01-15T10:30:15Z',
          event: 'Root cause analysis completed',
          details: 'Confidence: 94% - Recommended action: restart_service',
        },
        {
          timestamp: '2024-01-15T10:30:30Z',
          event: 'Awaiting remediation approval',
          details: 'Auto-remediation pending manual approval',
        },
      ],
    },
    {
      id: 'INC-2024-002',
      type: 'memory_leak',
      service: 'api-gateway',
      instance: 'i-0def456ghi789abc',
      severity: 'high',
      status: 'investigating',
      confidence: 0.87,
      recommendedAction: 'restart_service',
      timestamp: '2024-01-15T10:25:00Z',
      description: 'Memory usage increased to 98% over 10 minutes',
      metadata: {
        cpu_usage: 45.2,
        memory_usage: 98.1,
        disk_usage: 67.3,
        response_time: 1200,
      },
      timeline: [
        {
          timestamp: '2024-01-15T10:25:00Z',
          event: 'Incident detected',
          details: 'Memory leak pattern identified',
        },
        {
          timestamp: '2024-01-15T10:25:20Z',
          event: 'Investigation started',
          details: 'Analyzing memory allocation patterns',
        },
      ],
    },
    {
      id: 'INC-2024-003',
      type: 'disk_full',
      service: 'database-primary',
      instance: 'i-0ghi789jkl012def',
      severity: 'medium',
      status: 'resolved',
      confidence: 0.96,
      recommendedAction: 'clean_logs',
      timestamp: '2024-01-15T10:20:00Z',
      description: 'Disk usage at 97% on /var/log partition',
      metadata: {
        cpu_usage: 32.1,
        memory_usage: 54.8,
        disk_usage: 97.2,
        response_time: 800,
      },
      timeline: [
        {
          timestamp: '2024-01-15T10:20:00Z',
          event: 'Incident detected',
          details: 'Disk usage threshold exceeded',
        },
        {
          timestamp: '2024-01-15T10:20:30Z',
          event: 'Auto-remediation triggered',
          details: 'Executing log cleanup procedure',
        },
        {
          timestamp: '2024-01-15T10:21:15Z',
          event: 'Remediation completed',
          details: 'Disk usage reduced to 78%',
        },
        {
          timestamp: '2024-01-15T10:21:30Z',
          event: 'Incident resolved',
          details: 'System returned to normal operation',
        },
      ],
    },
  ];

  const data = incidents || mockIncidents;

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 120,
      fixed: 'left',
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      render: (type) => (
        <Tag color="blue">{type.replace('_', ' ').toUpperCase()}</Tag>
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
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (timestamp) => moment(timestamp).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 200,
      fixed: 'right',
      render: (_, record) => (
        <Space>
          <Button
            size="small"
            icon={<EyeOutlined />}
            onClick={() => {
              setSelectedIncident(record);
              setDrawerVisible(true);
            }}
          >
            View
          </Button>
          {record.status !== 'resolved' && (
            <Button
              size="small"
              type="primary"
              icon={<RobotOutlined />}
              onClick={() => handleRemediation(record)}
              loading={remediationMutation.isLoading}
            >
              Remediate
            </Button>
          )}
        </Space>
      ),
    },
  ];

  const handleRemediation = (incident) => {
    confirm({
      title: 'Trigger Auto-Remediation',
      icon: <ExclamationCircleOutlined />,
      content: (
        <div>
          <p>Are you sure you want to trigger auto-remediation for this incident?</p>
          <p><strong>Action:</strong> {incident.recommendedAction.replace('_', ' ')}</p>
          <p><strong>Confidence:</strong> {Math.round(incident.confidence * 100)}%</p>
        </div>
      ),
      onOk() {
        remediationMutation.mutate({
          incidentId: incident.id,
          action: incident.recommendedAction,
        });
      },
    });
  };

  const handleStatusUpdate = (incidentId, newStatus) => {
    statusMutation.mutate({
      incidentId,
      status: newStatus,
    });
  };

  return (
    <div>
      {/* Filters */}
      <Card style={{ marginBottom: 16 }}>
        <Space wrap>
          <Search
            placeholder="Search incidents..."
            style={{ width: 200 }}
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            onSearch={() => refetch()}
          />
          
          <Select
            style={{ width: 120 }}
            value={filters.severity}
            onChange={(value) => setFilters({ ...filters, severity: value })}
          >
            <Option value="all">All Severity</Option>
            <Option value="critical">Critical</Option>
            <Option value="high">High</Option>
            <Option value="medium">Medium</Option>
            <Option value="low">Low</Option>
          </Select>
          
          <Select
            style={{ width: 120 }}
            value={filters.status}
            onChange={(value) => setFilters({ ...filters, status: value })}
          >
            <Option value="all">All Status</Option>
            <Option value="open">Open</Option>
            <Option value="investigating">Investigating</Option>
            <Option value="resolved">Resolved</Option>
          </Select>
          
          <RangePicker
            value={filters.dateRange}
            onChange={(dates) => setFilters({ ...filters, dateRange: dates })}
          />
          
          <Button
            icon={<ReloadOutlined />}
            onClick={() => refetch()}
            loading={isLoading}
          >
            Refresh
          </Button>
        </Space>
      </Card>

      {/* Incidents Table */}
      <Card title="Incidents">
        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={isLoading}
          scroll={{ x: 1200 }}
          pagination={{
            pageSize: 20,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `${range[0]}-${range[1]} of ${total} incidents`,
          }}
        />
      </Card>

      {/* Incident Details Drawer */}
      <Drawer
        title={`Incident Details - ${selectedIncident?.id}`}
        width={720}
        open={drawerVisible}
        onClose={() => setDrawerVisible(false)}
        extra={
          selectedIncident?.status !== 'resolved' && (
            <Space>
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                onClick={() => handleRemediation(selectedIncident)}
              >
                Trigger Remediation
              </Button>
              <Button
                icon={<StopOutlined />}
                onClick={() => handleStatusUpdate(selectedIncident?.id, 'resolved')}
              >
                Mark Resolved
              </Button>
            </Space>
          )
        }
      >
        {selectedIncident && (
          <div>
            <Alert
              message={selectedIncident.description}
              type={selectedIncident.severity === 'critical' ? 'error' : 'warning'}
              showIcon
              style={{ marginBottom: 16 }}
            />

            <Descriptions title="Incident Information" bordered>
              <Descriptions.Item label="ID">{selectedIncident.id}</Descriptions.Item>
              <Descriptions.Item label="Type">
                <Tag color="blue">{selectedIncident.type.replace('_', ' ').toUpperCase()}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Service">{selectedIncident.service}</Descriptions.Item>
              <Descriptions.Item label="Instance">{selectedIncident.instance}</Descriptions.Item>
              <Descriptions.Item label="Severity">
                <Tag color={selectedIncident.severity === 'critical' ? 'red' : 'orange'}>
                  {selectedIncident.severity.toUpperCase()}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Status">
                <Tag color={selectedIncident.status === 'resolved' ? 'green' : 'blue'}>
                  {selectedIncident.status.toUpperCase()}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Confidence">
                <Progress
                  percent={Math.round(selectedIncident.confidence * 100)}
                  size="small"
                  status={selectedIncident.confidence > 0.8 ? 'success' : 'normal'}
                />
              </Descriptions.Item>
              <Descriptions.Item label="Recommended Action">
                <Tag icon={<RobotOutlined />} color="purple">
                  {selectedIncident.recommendedAction.replace('_', ' ')}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Timestamp">
                {moment(selectedIncident.timestamp).format('YYYY-MM-DD HH:mm:ss')}
              </Descriptions.Item>
            </Descriptions>

            <Divider />

            <Card title="System Metrics" size="small" style={{ marginBottom: 16 }}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>
                  <span>CPU Usage: </span>
                  <Progress
                    percent={selectedIncident.metadata.cpu_usage}
                    size="small"
                    status={selectedIncident.metadata.cpu_usage > 80 ? 'exception' : 'normal'}
                  />
                </div>
                <div>
                  <span>Memory Usage: </span>
                  <Progress
                    percent={selectedIncident.metadata.memory_usage}
                    size="small"
                    status={selectedIncident.metadata.memory_usage > 80 ? 'exception' : 'normal'}
                  />
                </div>
                <div>
                  <span>Disk Usage: </span>
                  <Progress
                    percent={selectedIncident.metadata.disk_usage}
                    size="small"
                    status={selectedIncident.metadata.disk_usage > 80 ? 'exception' : 'normal'}
                  />
                </div>
                <div>
                  <span>Response Time: {selectedIncident.metadata.response_time}ms</span>
                </div>
              </Space>
            </Card>

            <Card title="Timeline" size="small">
              <Timeline>
                {selectedIncident.timeline.map((event, index) => (
                  <Timeline.Item key={index}>
                    <div>
                      <strong>{event.event}</strong>
                      <div style={{ fontSize: '12px', color: '#666' }}>
                        {moment(event.timestamp).format('YYYY-MM-DD HH:mm:ss')}
                      </div>
                      <div>{event.details}</div>
                    </div>
                  </Timeline.Item>
                ))}
              </Timeline>
            </Card>
          </div>
        )}
      </Drawer>
    </div>
  );
};

export default Incidents;