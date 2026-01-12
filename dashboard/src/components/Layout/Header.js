import React from 'react';
import { Layout, Button, Space, Badge, Dropdown, Avatar, Switch } from 'antd';
import {
  MenuUnfoldOutlined,
  MenuFoldOutlined,
  BellOutlined,
  UserOutlined,
  LogoutOutlined,
  SettingOutlined,
  BulbOutlined,
} from '@ant-design/icons';

const { Header: AntHeader } = Layout;

const Header = ({ collapsed, setCollapsed, darkMode, toggleTheme, systemStatus }) => {
  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Profile',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Settings',
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      danger: true,
    },
  ];

  const notificationMenuItems = [
    {
      key: '1',
      label: (
        <div>
          <div style={{ fontWeight: 'bold' }}>High CPU Alert</div>
          <div style={{ fontSize: '12px', color: '#666' }}>
            web-server-prod - 2 minutes ago
          </div>
        </div>
      ),
    },
    {
      key: '2',
      label: (
        <div>
          <div style={{ fontWeight: 'bold' }}>Memory Leak Detected</div>
          <div style={{ fontSize: '12px', color: '#666' }}>
            api-gateway - 5 minutes ago
          </div>
        </div>
      ),
    },
    {
      key: '3',
      label: (
        <div>
          <div style={{ fontWeight: 'bold' }}>Auto-Remediation Success</div>
          <div style={{ fontSize: '12px', color: '#666' }}>
            database-primary - 10 minutes ago
          </div>
        </div>
      ),
    },
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
        return '#52c41a';
      case 'warning':
        return '#faad14';
      case 'critical':
        return '#ff4d4f';
      default:
        return '#d9d9d9';
    }
  };

  return (
    <AntHeader
      style={{
        padding: '0 24px',
        background: darkMode ? '#141414' : '#fff',
        borderBottom: `1px solid ${darkMode ? '#303030' : '#f0f0f0'}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'sticky',
        top: 0,
        zIndex: 1,
        marginLeft: collapsed ? 80 : 200,
        width: `calc(100% - ${collapsed ? 80 : 200}px)`,
      }}
    >
      <Space align="center">
        <Button
          type="text"
          icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          onClick={() => setCollapsed(!collapsed)}
          style={{
            fontSize: '16px',
            width: 64,
            height: 64,
          }}
        />
        
        <div style={{ marginLeft: 16 }}>
          <Space>
            <Badge
              color={getStatusColor(systemStatus.status)}
              text={
                <span style={{ color: darkMode ? '#fff' : '#000' }}>
                  System {systemStatus.status}
                </span>
              }
            />
            <span style={{ color: darkMode ? '#888' : '#666', fontSize: '14px' }}>
              {systemStatus.incidents} active incidents • {systemStatus.services} services • {systemStatus.uptime} uptime
            </span>
          </Space>
        </div>
      </Space>

      <Space align="center">
        <Space align="center">
          <BulbOutlined style={{ color: darkMode ? '#fff' : '#000' }} />
          <Switch
            checked={darkMode}
            onChange={toggleTheme}
            size="small"
          />
        </Space>

        <Dropdown
          menu={{ items: notificationMenuItems }}
          placement="bottomRight"
          trigger={['click']}
        >
          <Badge count={3} size="small">
            <Button
              type="text"
              icon={<BellOutlined />}
              style={{ fontSize: '16px' }}
            />
          </Badge>
        </Dropdown>

        <Dropdown
          menu={{ items: userMenuItems }}
          placement="bottomRight"
          trigger={['click']}
        >
          <Space style={{ cursor: 'pointer' }}>
            <Avatar icon={<UserOutlined />} />
            <span style={{ color: darkMode ? '#fff' : '#000' }}>
              Admin User
            </span>
          </Space>
        </Dropdown>
      </Space>
    </AntHeader>
  );
};

export default Header;