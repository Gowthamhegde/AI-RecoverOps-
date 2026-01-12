import React, { useState } from 'react';
import {
  Card,
  Table,
  Tag,
  Button,
  Space,
  Progress,
  Statistic,
  Row,
  Col,
  Modal,
  Form,
  Input,
  Upload,
  Select,
  Alert,
  Descriptions,
} from 'antd';
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  UploadOutlined,
  DownloadOutlined,
  DeleteOutlined,
  EyeOutlined,
  ExperimentOutlined,
} from '@ant-design/icons';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';

const { Option } = Select;

const Models = () => {
  const [selectedModel, setSelectedModel] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [uploadModalVisible, setUploadModalVisible] = useState(false);

  // Mock model data
  const models = [
    {
      id: 'xgboost-v2.1.0',
      name: 'XGBoost Classifier',
      version: 'v2.1.0',
      type: 'Classification',
      status: 'active',
      accuracy: 87.2,
      precision: 89.1,
      recall: 85.3,
      f1Score: 87.1,
      trainingDate: '2024-01-10',
      lastUsed: '2024-01-15 10:30:00',
      predictions: 15420,
      size: '45.2 MB',
    },
    {
      id: 'lstm-v1.8.3',
      name: 'LSTM Sequence Model',
      version: 'v1.8.3',
      type: 'Sequence Analysis',
      status: 'active',
      accuracy: 82.7,
      precision: 84.2,
      recall: 81.1,
      f1Score: 82.6,
      trainingDate: '2024-01-08',
      lastUsed: '2024-01-15 10:30:00',
      predictions: 12850,
      size: '128.7 MB',
    },
    {
      id: 'ensemble-v3.0.1',
      name: 'Ensemble Predictor',
      version: 'v3.0.1',
      type: 'Ensemble',
      status: 'active',
      accuracy: 91.4,
      precision: 92.8,
      recall: 90.1,
      f1Score: 91.4,
      trainingDate: '2024-01-12',
      lastUsed: '2024-01-15 10:30:00',
      predictions: 8750,
      size: '89.3 MB',
    },
    {
      id: 'xgboost-v2.0.5',
      name: 'XGBoost Classifier',
      version: 'v2.0.5',
      type: 'Classification',
      status: 'inactive',
      accuracy: 85.1,
      precision: 86.7,
      recall: 83.4,
      f1Score: 85.0,
      trainingDate: '2024-01-05',
      lastUsed: '2024-01-10 15:22:00',
      predictions: 45230,
      size: '42.8 MB',
    },
  ];

  // Mock performance data
  const performanceData = [
    { date: '2024-01-08', accuracy: 85.2, predictions: 1200 },
    { date: '2024-01-09', accuracy: 86.1, predictions: 1350 },
    { date: '2024-01-10', accuracy: 87.2, predictions: 1180 },
    { date: '2024-01-11', accuracy: 86.8, predictions: 1420 },
    { date: '2024-01-12', accuracy: 87.5, predictions: 1290 },
    { date: '2024-01-13', accuracy: 87.1, predictions: 1380 },
    { date: '2024-01-14', accuracy: 87.8, predictions: 1150 },
  ];

  const predictionDistribution = [
    { type: 'High CPU', count: 450, accuracy: 94.2 },
    { type: 'Memory Leak', count: 320, accuracy: 89.1 },
    { type: 'Disk Full', count: 280, accuracy: 92.7 },
    { type: 'Service Crash', count: 190, accuracy: 87.3 },
    { type: 'DB Connection', count: 150, accuracy: 85.8 },
  ];

  const columns = [
    {
      title: 'Model',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <div>
          <div style={{ fontWeight: 'bold' }}>{text}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>
            {record.version} • {record.type}
          </div>
        </div>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={status === 'active' ? 'green' : 'default'}>
          {status.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Accuracy',
      dataIndex: 'accuracy',
      key: 'accuracy',
      render: (accuracy) => (
        <Progress
          percent={accuracy}
          size="small"
          status={accuracy > 85 ? 'success' : 'normal'}
          format={(percent) => `${percent}%`}
        />
      ),
    },
    {
      title: 'F1-Score',
      dataIndex: 'f1Score',
      key: 'f1Score',
      render: (score) => `${score}%`,
    },
    {
      title: 'Predictions',
      dataIndex: 'predictions',
      key: 'predictions',
      render: (count) => count.toLocaleString(),
    },
    {
      title: 'Size',
      dataIndex: 'size',
      key: 'size',
    },
    {
      title: 'Last Used',
      dataIndex: 'lastUsed',
      key: 'lastUsed',
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            size="small"
            icon={<EyeOutlined />}
            onClick={() => {
              setSelectedModel(record);
              setModalVisible(true);
            }}
          >
            View
          </Button>
          {record.status === 'active' ? (
            <Button
              size="small"
              icon={<PauseCircleOutlined />}
              onClick={() => handleModelAction(record.id, 'deactivate')}
            >
              Deactivate
            </Button>
          ) : (
            <Button
              size="small"
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={() => handleModelAction(record.id, 'activate')}
            >
              Activate
            </Button>
          )}
          <Button
            size="small"
            icon={<DownloadOutlined />}
            onClick={() => handleModelAction(record.id, 'download')}
          >
            Export
          </Button>
          {record.status !== 'active' && (
            <Button
              size="small"
              danger
              icon={<DeleteOutlined />}
              onClick={() => handleModelAction(record.id, 'delete')}
            >
              Delete
            </Button>
          )}
        </Space>
      ),
    },
  ];

  const handleModelAction = (modelId, action) => {
    console.log(`${action} model:`, modelId);
    // Implement model actions
  };

  const handleUploadModel = (values) => {
    console.log('Upload model:', values);
    setUploadModalVisible(false);
  };

  return (
    <div>
      {/* Overview Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Active Models"
              value={models.filter(m => m.status === 'active').length}
              suffix={`/ ${models.length}`}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Average Accuracy"
              value={87.1}
              precision={1}
              suffix="%"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Predictions"
              value={42250}
              suffix="today"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Model Storage"
              value={305.0}
              precision={1}
              suffix="MB"
            />
          </Card>
        </Col>
      </Row>

      {/* Performance Charts */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={16}>
          <Card title="Model Performance Trend">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis yAxisId="left" domain={[80, 90]} />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Line
                  yAxisId="left"
                  type="monotone"
                  dataKey="accuracy"
                  stroke="#1890ff"
                  strokeWidth={3}
                  name="Accuracy (%)"
                />
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="predictions"
                  stroke="#52c41a"
                  strokeWidth={2}
                  name="Daily Predictions"
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Prediction Distribution">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={predictionDistribution} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="type" type="category" width={80} />
                <Tooltip />
                <Bar dataKey="count" fill="#1890ff" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Models Table */}
      <Card
        title="ML Models"
        extra={
          <Space>
            <Button
              type="primary"
              icon={<UploadOutlined />}
              onClick={() => setUploadModalVisible(true)}
            >
              Upload Model
            </Button>
            <Button
              icon={<ExperimentOutlined />}
              onClick={() => console.log('Start training')}
            >
              Train New Model
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={models}
          rowKey="id"
          pagination={false}
        />
      </Card>

      {/* Model Details Modal */}
      <Modal
        title={`Model Details - ${selectedModel?.name}`}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={800}
      >
        {selectedModel && (
          <div>
            <Alert
              message="Model Information"
              description={`${selectedModel.name} ${selectedModel.version} - ${selectedModel.type}`}
              type="info"
              style={{ marginBottom: 16 }}
            />

            <Descriptions bordered>
              <Descriptions.Item label="Model ID">{selectedModel.id}</Descriptions.Item>
              <Descriptions.Item label="Version">{selectedModel.version}</Descriptions.Item>
              <Descriptions.Item label="Type">{selectedModel.type}</Descriptions.Item>
              <Descriptions.Item label="Status">
                <Tag color={selectedModel.status === 'active' ? 'green' : 'default'}>
                  {selectedModel.status.toUpperCase()}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Training Date">{selectedModel.trainingDate}</Descriptions.Item>
              <Descriptions.Item label="File Size">{selectedModel.size}</Descriptions.Item>
            </Descriptions>

            <Card title="Performance Metrics" style={{ marginTop: 16 }}>
              <Row gutter={16}>
                <Col span={6}>
                  <Statistic
                    title="Accuracy"
                    value={selectedModel.accuracy}
                    precision={1}
                    suffix="%"
                  />
                </Col>
                <Col span={6}>
                  <Statistic
                    title="Precision"
                    value={selectedModel.precision}
                    precision={1}
                    suffix="%"
                  />
                </Col>
                <Col span={6}>
                  <Statistic
                    title="Recall"
                    value={selectedModel.recall}
                    precision={1}
                    suffix="%"
                  />
                </Col>
                <Col span={6}>
                  <Statistic
                    title="F1-Score"
                    value={selectedModel.f1Score}
                    precision={1}
                    suffix="%"
                  />
                </Col>
              </Row>
            </Card>

            <Card title="Usage Statistics" style={{ marginTop: 16 }}>
              <Row gutter={16}>
                <Col span={12}>
                  <Statistic
                    title="Total Predictions"
                    value={selectedModel.predictions}
                  />
                </Col>
                <Col span={12}>
                  <Statistic
                    title="Last Used"
                    value={selectedModel.lastUsed}
                  />
                </Col>
              </Row>
            </Card>
          </div>
        )}
      </Modal>

      {/* Upload Model Modal */}
      <Modal
        title="Upload New Model"
        open={uploadModalVisible}
        onCancel={() => setUploadModalVisible(false)}
        footer={null}
      >
        <Form
          layout="vertical"
          onFinish={handleUploadModel}
        >
          <Form.Item
            label="Model Name"
            name="name"
            rules={[{ required: true, message: 'Please enter model name' }]}
          >
            <Input placeholder="e.g., XGBoost Classifier v2.2.0" />
          </Form.Item>

          <Form.Item
            label="Model Type"
            name="type"
            rules={[{ required: true, message: 'Please select model type' }]}
          >
            <Select placeholder="Select model type">
              <Option value="classification">Classification</Option>
              <Option value="regression">Regression</Option>
              <Option value="sequence">Sequence Analysis</Option>
              <Option value="ensemble">Ensemble</Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="Model File"
            name="file"
            rules={[{ required: true, message: 'Please upload model file' }]}
          >
            <Upload
              accept=".pkl,.joblib,.h5,.onnx"
              beforeUpload={() => false}
              maxCount={1}
            >
              <Button icon={<UploadOutlined />}>
                Select Model File
              </Button>
            </Upload>
          </Form.Item>

          <Form.Item
            label="Description"
            name="description"
          >
            <Input.TextArea
              rows={3}
              placeholder="Optional description of the model..."
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                Upload Model
              </Button>
              <Button onClick={() => setUploadModalVisible(false)}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Models;