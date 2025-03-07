import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Alert, Snackbar } from '@mui/material';

// Components
import Layout from './components/Layout';
import ErrorNotification from './components/ErrorNotification';

// Pages
import Dashboard from './pages/Dashboard';
import Documents from './pages/Documents';
import Candidates from './pages/Candidates';
import Positions from './pages/Positions';
import InterviewQuestions from './pages/InterviewQuestions';
import ChatAssistant from './pages/ChatAssistant';
import Login from './pages/Login';
import Register from './pages/Register';

// Create theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 500,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
    },
    h3: {
      fontSize: '1.8rem',
      fontWeight: 500,
    },
  },
});

// Protected route component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = localStorage.getItem('token') !== null;
  const location = useLocation();

  if (!isAuthenticated) {
    // Redirect to login if not authenticated
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

function App() {
  const location = useLocation();
  const [notification, setNotification] = useState<{message: string, type: 'success' | 'error'} | null>(null);

  // Check for notification messages in location state (e.g., from register success)
  useEffect(() => {
    if (location.state && location.state.message) {
      setNotification({
        message: location.state.message,
        type: location.state.type || 'success'
      });
      
      // Clean up the location state
      window.history.replaceState({}, document.title);
    }
  }, [location]);

  // Close notification
  const handleCloseNotification = () => {
    setNotification(null);
  };

  // Determine if the current route is a public route (login/register)
  const isAuthRoute = location.pathname === '/login' || location.pathname === '/register';

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      
      {/* Global API Error Notification */}
      <ErrorNotification />
      
      {/* Notification snackbar */}
      <Snackbar 
        open={notification !== null} 
        autoHideDuration={6000} 
        onClose={handleCloseNotification}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleCloseNotification} 
          severity={notification?.type || 'success'}
          sx={{ width: '100%' }}
        >
          {notification?.message || ''}
        </Alert>
      </Snackbar>

      {isAuthRoute ? (
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      ) : (
        <Layout>
          <Routes>
            <Route path="/" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            <Route path="/documents" element={
              <ProtectedRoute>
                <Documents />
              </ProtectedRoute>
            } />
            <Route path="/candidates" element={
              <ProtectedRoute>
                <Candidates />
              </ProtectedRoute>
            } />
            <Route path="/positions" element={
              <ProtectedRoute>
                <Positions />
              </ProtectedRoute>
            } />
            <Route path="/interview-questions" element={
              <ProtectedRoute>
                <InterviewQuestions />
              </ProtectedRoute>
            } />
            <Route path="/chat" element={
              <ProtectedRoute>
                <ChatAssistant />
              </ProtectedRoute>
            } />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Layout>
      )}
    </ThemeProvider>
  );
}

export default App; 