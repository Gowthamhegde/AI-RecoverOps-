import React from 'react';
import { Layout, Menu } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  AlertOutlined,
  BarChartOutlined,
  BranchesOutlined,
  FileTextOutlined,
  SettingOutlined,
  RobotOutlined,
} from '@ant-design/icons';

const { Sider } = Layout;

const Sidebar = ({ collapsed, darkMode }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: '/incidents',
      icon: <AlertOutlined />,
      label: 'Incidents',
    },
    {
      key: '/analytics',
      icon: <BarChartOutlined />,
      label: 'Analytics',
    },
    {
      key: '/models',
      icon: <BranchesOutlined />,
      label: 'ML Models',
    },
    {
      key: '/logs',
      icon: <FileTextOutlined />,
      label: 'Logs',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: 'Settings',
    },
  ];

  const handleMenuClick = ({ key }) => {
    navigate(key);
  };

  return (
    <Sider
      trigger={null}
      collapsible
      collapsed={collapsed}
      theme={darkMode ? 'dark' : 'light'}
      style={{
        overflow: 'auto',
        height: '100vh',
        position: 'fixed',
        left: 0,
        top: 0,
        bottom: 0,
      }}
    >
      <div
        style={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderBottom: `1px solid ${darkMode ? '#303030' : '#f0f0f0'}`,
        }}
      >
        <RobotOutlined
          style={{
            fontSize: collapsed ? 24 : 32,
            color: '#1890ff',
            marginRight: collapsed ? 0 : 8,
          }}
        />
        {!collapsed && (
          <span
            style={{
              fontSize: 18,
              fontWeight: 'bold',
              color: darkMode ? '#fff' : '#000',
            }}
          >
            AI-RecoverOps
          </span>
        )}
      </div>
      
      <Menu
        theme={darkMode ? 'dark' : 'light'}
        mode="inline"
        selectedKeys={[location.pathname]}
        items={menuItems}
        onClick={handleMenuClick}
        style={{ borderRight: 0, marginTop: 16 }}
      />
    </Sider>
  );
};

export default Sidebar;