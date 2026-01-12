import React, { useState } from 'react';
import {
  Card,
  Form,
  Input,
  Switch,
  Button,
  Slider,
  Select,
  Divider,
  Space,
  Alert,
  Tabs,
  InputNumber,
  Upload,
  message,
} from 'antd';
import {
  SaveOutlined,
  ReloadOutlined,
  UploadOutlined,
  TestOutlined,
  SecurityScanOutlined,
} from '@ant-design/icons';

const { Option } = Select;
const { TextArea } = Input;

const Settings = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [testingConnection, setTestingConnection] = useState(false);

  const handleSave = async (values) => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      message.success('Settings saved successfully');
    } catch (error) {
      message.error('Failed to save settings');
    } finally {
      setLoading(false);
    }
  };

  const testConnection = async (type) => {
    setTestingConnection(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      message.success(`${type} connection test successful`);
    } catch (error) {
      message.error(`${type} connection test failed`);
    } finally {
      setTestingConnection(false);
    }
  };

  const tabItems = [
    {
      key: 'general',
      label: 'General',
      children: (
        <Card>
          <Form
            form={form}
            layout="vertical"
            onFinish={handleSave}
            initialValues={{
              confidenceThreshold: 0.8,
              autoRemediation: true,
              maxConcurrentFixes: 3,
              rollbackTimeout: 300,
              logLevel: 'INFO',
            }}
          >
            <Form.Item
              label="Confidence Threshold"
              name="confidenceThreshold"
              help="Minimum confidence level required for auto-remediation"
            >
              <Slider
                min={0.5}
                max={1.0}
                step={0.05}
                marks={{
                  0.5: '50%',
                  0.7: '70%',
                  0.8: '80%',
                  0.9: '90%',
                  1.0: '100%',
                }}
              />
            </Form.Item>

            <Form.Item
              label="Enable Auto-Remediation"
              name="autoRemediation"
              valuePropName="checked"
            >
              <Switch />
            </Form.Item>

            <Form.Item
              label="Max Concurrent Fixes"
              name="maxConcurrentFixes"
              help="Maximum number of simultaneous remediation actions"
            >
              <InputNumber min={1} max={10} />
            </Form.Item>

            <Form.Item
              label="Rollback Timeout (seconds)"
              name="rollbackTimeout"
              help="Time to wait before automatic rollback"
            >
              <InputNumber min={60} max={3600} />
            </Form.Item>

            <Form.Item
              label="Log Level"
              name="logLevel"
            >
              <Select>
                <Option value="DEBUG">DEBUG</Option>
                <Option value="INFO">INFO</Option>
                <Option value="WARN">WARN</Option>
                <Option value="ERROR">ERROR</Option>
              </Select>
            </Form.Item>

            <Form.Item>
              <Space>
                <Button
                  type="primary"
                  htmlType="submit"
                  icon={<SaveOutlined />}
                  loading={loading}
                >
                  Save Settings
                </Button>
                <Button icon={<ReloadOutlined />}>
                  Reset to Defaults
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Card>
      ),
    },
    {
      key: 'notifications',
      label: 'Notifications',
      children: (
        <Card>
          <Form layout="vertical">
            <Alert
              message="Notification Settings"
              description="Configure how and when you receive alerts about incidents and system status."
              type="info"
              style={{ marginBottom: 24 }}
            />

            <Divider>Slack Integration</Divider>
            
            <Form.Item
              label="Slack Webhook URL"
              name="slackWebhook"
              help="Get this from your Slack app configuration"
            >
              <Input.Password placeholder="https://hooks.slack.com/services/..." />
            </Form.Item>

            <Form.Item
              label="Slack Channel"
              name="slackChannel"
            >
              <Input placeholder="#ai-recoverops" />
            </Form.Item>

            <Form.Item>
              <Button
                icon={<TestOutlined />}
                onClick={() => testConnection('Slack')}
                loading={testingConnection}
              >
                Test Slack Connection
              </Button>
            </Form.Item>

            <Divider>Email Notifications</Divider>

            <Form.Item
              label="SMTP Server"
              name="smtpServer"
            >
              <Input placeholder="smtp.gmail.com" />
            </Form.Item>

            <Form.Item
              label="SMTP Port"
              name="smtpPort"
            >
              <InputNumber placeholder={587} />
            </Form.Item>

            <Form.Item
              label="Email Username"
              name="emailUsername"
            >
              <Input placeholder="alerts@yourcompany.com" />
            </Form.Item>

            <Form.Item
              label="Email Password"
              name="emailPassword"
            >
              <Input.Password />
            </Form.Item>

            <Form.Item
              label="Alert Recipients"
              name="alertRecipients"
              help="Comma-separated email addresses"
            >
              <TextArea
                rows={3}
                placeholder="admin@company.com, devops@company.com"
              />
            </Form.Item>

            <Form.Item>
              <Button
                icon={<TestOutlined />}
                onClick={() => testConnection('Email')}
                loading={testingConnection}
              >
                Test Email Configuration
              </Button>
            </Form.Item>

            <Divider>Alert Rules</Divider>

            <Form.Item
              label="Critical Incidents"
              name="criticalAlerts"
              valuePropName="checked"
            >
              <Switch defaultChecked />
            </Form.Item>

            <Form.Item
              label="High Priority Incidents"
              name="highPriorityAlerts"
              valuePropName="checked"
            >
              <Switch defaultChecked />
            </Form.Item>

            <Form.Item
              label="Remediation Success"
              name="remediationSuccess"
              valuePropName="checked"
            >
              <Switch />
            </Form.Item>

            <Form.Item
              label="Remediation Failures"
              name="remediationFailures"
              valuePropName="checked"
            >
              <Switch defaultChecked />
            </Form.Item>
          </Form>
        </Card>
      ),
    },
    {
      key: 'aws',
      label: 'AWS Integration',
      children: (
        <Card>
          <Form layout="vertical">
            <Alert
              message="AWS Configuration"
              description="Configure AWS credentials and services for cloud integration."
              type="info"
              style={{ marginBottom: 24 }}
            />

            <Form.Item
              label="AWS Region"
              name="awsRegion"
            >
              <Select placeholder="Select AWS region">
                <Option value="us-east-1">US East (N. Virginia)</Option>
                <Option value="us-west-2">US West (Oregon)</Option>
                <Option value="eu-west-1">Europe (Ireland)</Option>
                <Option value="ap-southeast-1">Asia Pacific (Singapore)</Option>
              </Select>
            </Form.Item>

            <Form.Item
              label="AWS Access Key ID"
              name="awsAccessKey"
            >
              <Input.Password />
            </Form.Item>

            <Form.Item
              label="AWS Secret Access Key"
              name="awsSecretKey"
            >
              <Input.Password />
            </Form.Item>

            <Divider>Service Configuration</Divider>

            <Form.Item
              label="CloudWatch Log Groups"
              name="logGroups"
              help="Comma-separated list of log groups to monitor"
            >
              <TextArea
                rows={3}
                placeholder="/aws/lambda/my-function, /aws/ecs/my-cluster"
              />
            </Form.Item>

            <Form.Item
              label="SNS Topic ARN"
              name="snsTopicArn"
              help="SNS topic for sending alerts"
            >
              <Input placeholder="arn:aws:sns:us-east-1:123456789012:ai-recoverops-alerts" />
            </Form.Item>

            <Form.Item
              label="S3 Bucket for Logs"
              name="s3LogsBucket"
            >
              <Input placeholder="ai-recoverops-logs" />
            </Form.Item>

            <Form.Item>
              <Button
                icon={<TestOutlined />}
                onClick={() => testConnection('AWS')}
                loading={testingConnection}
              >
                Test AWS Connection
              </Button>
            </Form.Item>
          </Form>
        </Card>
      ),
    },
    {
      key: 'security',
      label: 'Security',
      children: (
        <Card>
          <Form layout="vertical">
            <Alert
              message="Security Settings"
              description="Configure authentication, authorization, and security policies."
              type="warning"
              style={{ marginBottom: 24 }}
            />

            <Divider>Authentication</Divider>

            <Form.Item
              label="Enable API Authentication"
              name="apiAuth"
              valuePropName="checked"
            >
              <Switch defaultChecked />
            </Form.Item>

            <Form.Item
              label="JWT Secret Key"
              name="jwtSecret"
            >
              <Input.Password placeholder="Enter a strong secret key" />
            </Form.Item>

            <Form.Item
              label="Session Timeout (minutes)"
              name="sessionTimeout"
            >
              <InputNumber min={15} max={1440} defaultValue={480} />
            </Form.Item>

            <Divider>Access Control</Divider>

            <Form.Item
              label="Allowed IP Addresses"
              name="allowedIPs"
              help="Comma-separated list of allowed IP addresses (leave empty for all)"
            >
              <TextArea
                rows={3}
                placeholder="192.168.1.0/24, 10.0.0.0/8"
              />
            </Form.Item>

            <Form.Item
              label="Enable Audit Logging"
              name="auditLogging"
              valuePropName="checked"
            >
              <Switch defaultChecked />
            </Form.Item>

            <Divider>Remediation Safety</Divider>

            <Form.Item
              label="Require Manual Approval for Critical Actions"
              name="requireApproval"
              valuePropName="checked"
            >
              <Switch defaultChecked />
            </Form.Item>

            <Form.Item
              label="Enable Rollback for Failed Remediations"
              name="enableRollback"
              valuePropName="checked"
            >
              <Switch defaultChecked />
            </Form.Item>

            <Form.Item
              label="Backup Before Remediation"
              name="backupBeforeRemediation"
              valuePropName="checked"
            >
              <Switch defaultChecked />
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                icon={<SecurityScanOutlined />}
                onClick={() => message.info('Security scan initiated')}
              >
                Run Security Scan
              </Button>
            </Form.Item>
          </Form>
        </Card>
      ),
    },
    {
      key: 'models',
      label: 'ML Models',
      children: (
        <Card>
          <Form layout="vertical">
            <Alert
              message="Machine Learning Configuration"
              description="Manage ML models, training data, and model performance settings."
              type="info"
              style={{ marginBottom: 24 }}
            />

            <Divider>Model Management</Divider>

            <Form.Item
              label="Active Model Version"
              name="activeModel"
            >
              <Select defaultValue="v2.1.0">
                <Option value="v2.1.0">v2.1.0 (Current)</Option>
                <Option value="v2.0.5">v2.0.5</Option>
                <Option value="v1.9.8">v1.9.8</Option>
              </Select>
            </Form.Item>

            <Form.Item
              label="Model Update Interval (hours)"
              name="modelUpdateInterval"
            >
              <InputNumber min={1} max={168} defaultValue={24} />
            </Form.Item>

            <Form.Item
              label="Training Data Retention (days)"
              name="dataRetention"
            >
              <InputNumber min={7} max={365} defaultValue={90} />
            </Form.Item>

            <Divider>Model Upload</Divider>

            <Form.Item
              label="Upload New Model"
              name="modelUpload"
            >
              <Upload
                accept=".pkl,.joblib,.h5"
                beforeUpload={() => false}
                onChange={(info) => {
                  message.info(`${info.file.name} selected for upload`);
                }}
              >
                <Button icon={<UploadOutlined />}>
                  Select Model File
                </Button>
              </Upload>
            </Form.Item>

            <Divider>Performance Thresholds</Divider>

            <Form.Item
              label="Minimum Model Accuracy (%)"
              name="minAccuracy"
            >
              <Slider
                min={70}
                max={100}
                defaultValue={85}
                marks={{
                  70: '70%',
                  80: '80%',
                  85: '85%',
                  90: '90%',
                  100: '100%',
                }}
              />
            </Form.Item>

            <Form.Item
              label="Auto-Retrain on Performance Drop"
              name="autoRetrain"
              valuePropName="checked"
            >
              <Switch defaultChecked />
            </Form.Item>

            <Form.Item>
              <Space>
                <Button
                  type="primary"
                  onClick={() => message.info('Model training initiated')}
                >
                  Start Training
                </Button>
                <Button
                  onClick={() => message.info('Model validation started')}
                >
                  Validate Model
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Card>
      ),
    },
  ];

  return (
    <div>
      <Card title="AI-RecoverOps Settings" style={{ marginBottom: 24 }}>
        <p>
          Configure AI-RecoverOps settings, integrations, and security policies.
          Changes will be applied immediately unless otherwise noted.
        </p>
      </Card>

      <Tabs
        defaultActiveKey="general"
        items={tabItems}
        size="large"
      />
    </div>
  );
};

export default Settings;