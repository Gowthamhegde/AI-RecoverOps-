import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Layout, ConfigProvider, theme, notification } from 'antd';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import io from 'socket.io-client';

// Components
import Sidebar from './components/Layout/Sidebar';
import Header from './components/Layout/Header';
import Dashboard from './pages/Dashboard';
import Incidents from './pages/Incidents';
import Pipelines from './pages/Pipelines';
import Recovery from './pages/Recovery';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';
import RealTimeMonitor from './pages/RealTimeMonitor';

// Services
import { apiService } from './services/apiService';

// Styles
import './App.css';

const { Content } = Layout;

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 2,
      staleTime: 30000,
      cacheTime: 300000,
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
    pipelines: 0,
    uptime: '99.9%',
    lastUpdate: new Date().toISOString()
  });
  const [realTimeData, setRealTimeData] = useState({
    activeIncidents: [],
    recentEvents: [],
    systemMetrics: {}
  });

  // Initialize WebSocket connection
  useEffect(() => {
    const initializeSocket = () => {
      const newSocket = io('http://localhost:8000', {
        transports: ['websocket', 'polling'],
        timeout: 20000,
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionAttempts: 5
      });

      newSocket.on('connect', () => {
        console.log('🔗 Connected to AI-RecoverOps backend');
        notification.success({
          message: 'Connected',
          description: 'Real-time monitoring active',
          duration: 2
        });
      });

      newSocket.on('disconnect', () => {
        console.log('❌ Disconnected from backend');
        notification.warning({
          message: 'Disconnected',
          description: 'Attempting to reconnect...',
          duration: 3
        });
      });

      // Real-time event handlers
      newSocket.on('incident_detected', (data) => {
        console.log('🚨 New incident detected:', data);
        setRealTimeData(prev => ({
          ...prev,
          activeIncidents: [data, ...prev.activeIncidents.slice(0, 9)],
          recentEvents: [{
            type: 'incident',
            data: data,
            timestamp: new Date().toISOString()
          }, ...prev.recentEvents.slice(0, 49)]
        }));

        notification.error({
          message: 'New Incident Detected',
          description: `${data.title} - ${data.severity}`,
          duration: 5
        });
      });

      newSocket.on('incident_resolved', (data) => {
        console.log('✅ Incident resolved:', data);
        setRealTimeData(prev => ({
          ...prev,
          activeIncidents: prev.activeIncidents.filter(inc => inc.id !== data.id),
          recentEvents: [{
            type: 'resolution',
            data: data,
            timestamp: new Date().toISOString()
          }, ...prev.recentEvents.slice(0, 49)]
        }));

        notification.success({
          message: 'Incident Resolved',
          description: `${data.title} has been automatically fixed`,
          duration: 4
        });
      });

      newSocket.on('remediation_started', (data) => {
        console.log('🔧 Remediation started:', data);
        setRealTimeData(prev => ({
          ...prev,
          recentEvents: [{
            type: 'remediation',
            data: data,
            timestamp: new Date().toISOString()
          }, ...prev.recentEvents.slice(0, 49)]
        }));

        notification.info({
          message: 'Auto-Remediation Started',
          description: `Fixing: ${data.description}`,
          duration: 3
        });
      });

      newSocket.on('system_metrics', (data) => {
        setRealTimeData(prev => ({
          ...prev,
          systemMetrics: data
        }));
      });

      newSocket.on('pipeline_status', (data) => {
        console.log('📊 Pipeline status update:', data);
        setRealTimeData(prev => ({
          ...prev,
          recentEvents: [{
            type: 'pipeline',
            data: data,
            timestamp: new Date().toISOString()
          }, ...prev.recentEvents.slice(0, 49)]
        }));
      });

      setSocket(newSocket);

      return newSocket;
    };

    const socketInstance = initializeSocket();

    return () => {
      if (socketInstance) {
        socketInstance.close();
      }
    };
  }, []);

  // Fetch system status periodically
  useEffect(() => {
    const fetchSystemStatus = async () => {
      try {
        const status = await apiService.getSystemStatus();
        setSystemStatus(status);
      } catch (error) {
        console.error('Failed to fetch system status:', error);
      }
    };

    fetchSystemStatus();
    const interval = setInterval(fetchSystemStatus, 30000); // Every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const toggleTheme = () => {
    setDarkMode(!darkMode);
    localStorage.setItem('ai-recoverops-theme', !darkMode ? 'dark' : 'light');
  };

  // Load theme preference
  useEffect(() => {
    const savedTheme = localStorage.getItem('ai-recoverops-theme');
    if (savedTheme === 'dark') {
      setDarkMode(true);
    }
  }, []);

  return (
    <ConfigProvider
      theme={{
        algorithm: darkMode ? theme.darkAlgorithm : theme.defaultAlgorithm,
        token: {
          colorPrimary: '#1890ff',
          borderRadius: 6,
          colorBgContainer: darkMode ? '#141414' : '#ffffff',
        },
      }}
    >
      <QueryClientProvider client={queryClient}>
        <Router>
          <Layout style={{ minHeight: '100vh' }}>
            <Sidebar 
              collapsed={collapsed} 
              darkMode={darkMode}
              systemStatus={systemStatus}
            />
            
            <Layout className="site-layout">
              <Header
                collapsed={collapsed}
                setCollapsed={setCollapsed}
                darkMode={darkMode}
                toggleTheme={toggleTheme}
                systemStatus={systemStatus}
                realTimeData={realTimeData}
              />
              
              <Content
                style={{
                  margin: '24px 16px',
                  padding: 24,
                  minHeight: 280,
                  background: darkMode ? '#141414' : '#fff',
                  borderRadius: 6,
                  overflow: 'auto'
                }}
              >
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route 
                    path="/dashboard" 
                    element={
                      <Dashboard 
                        socket={socket} 
                        realTimeData={realTimeData}
                        systemStatus={systemStatus}
                      />
                    } 
                  />
                  <Route 
                    path="/incidents" 
                    element={
                      <Incidents 
                        socket={socket}
                        realTimeData={realTimeData}
                      />
                    } 
                  />
                  <Route 
                    path="/pipelines" 
                    element={
                      <Pipelines 
                        socket={socket}
                        realTimeData={realTimeData}
                      />
                    } 
                  />
                  <Route 
                    path="/recovery" 
                    element={
                      <Recovery 
                        socket={socket}
                        realTimeData={realTimeData}
                      />
                    } 
                  />
                  <Route 
                    path="/monitor" 
                    element={
                      <RealTimeMonitor 
                        socket={socket}
                        realTimeData={realTimeData}
                        systemStatus={systemStatus}
                      />
                    } 
                  />
                  <Route path="/analytics" element={<Analytics />} />
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
              border: darkMode ? '1px solid #555' : '1px solid #ddd',
            },
            success: {
              iconTheme: {
                primary: '#52c41a',
                secondary: '#fff',
              },
            },
            error: {
              iconTheme: {
                primary: '#ff4d4f',
                secondary: '#fff',
              },
            },
          }}
        />
      </QueryClientProvider>
    </ConfigProvider>
  );
}

export default App;