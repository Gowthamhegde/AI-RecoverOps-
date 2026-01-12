import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Layout, ConfigProvider, theme } from 'antd';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import io from 'socket.io-client';

// Components
import Sidebar from './components/Layout/Sidebar';
import Header from './components/Layout/Header';
import Dashboard from './pages/Dashboard';
import Incidents from './pages/Incidents';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';
import Models from './pages/Models';
import Logs from './pages/Logs';

// Styles
import './App.css';

const { Content } = Layout;

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000,
    },
  },
});

function App() {
  const [collapsed, setCollapsed] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [socket, setSocket] = useState(null);
  const [systemStatus, setSystemStatus] = useState({
    status: 'healthy',
    incidents: 0,
    services: 47,
    uptime: '99.9%'
  });

  // Initialize WebSocket connection for real-time updates
  useEffect(() => {
    const newSocket = io('http://localhost:8000', {
      transports: ['websocket', 'polling']
    });

    newSocket.on('connect', () => {
      console.log('Connected to AI-RecoverOps backend');
    });

    newSocket.on('incident_detected', (data) => {
      console.log('New incident detected:', data);
      // Handle real-time incident updates
    });

    newSocket.on('system_status', (data) => {
      setSystemStatus(data);
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, []);

  const toggleTheme = () => {
    setDarkMode(!darkMode);
  };

  return (
    <ConfigProvider
      theme={{
        algorithm: darkMode ? theme.darkAlgorithm : theme.defaultAlgorithm,
        token: {
          colorPrimary: '#1890ff',
          borderRadius: 6,
        },
      }}
    >
      <QueryClientProvider client={queryClient}>
        <Router>
          <Layout style={{ minHeight: '100vh' }}>
            <Sidebar collapsed={collapsed} darkMode={darkMode} />
            
            <Layout className="site-layout">
              <Header
                collapsed={collapsed}
                setCollapsed={setCollapsed}
                darkMode={darkMode}
                toggleTheme={toggleTheme}
                systemStatus={systemStatus}
              />
              
              <Content
                style={{
                  margin: '24px 16px',
                  padding: 24,
                  minHeight: 280,
                  background: darkMode ? '#141414' : '#fff',
                  borderRadius: 6,
                }}
              >
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/dashboard" element={<Dashboard socket={socket} />} />
                  <Route path="/incidents" element={<Incidents socket={socket} />} />
                  <Route path="/analytics" element={<Analytics />} />
                  <Route path="/models" element={<Models />} />
                  <Route path="/logs" element={<Logs />} />
                  <Route path="/settings" element={<Settings />} />
                </Routes>
              </Content>
            </Layout>
          </Layout>
        </Router>
        
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: darkMode ? '#363636' : '#fff',
              color: darkMode ? '#fff' : '#363636',
            },
          }}
        />
      </QueryClientProvider>
    </ConfigProvider>
  );
}

export default App;