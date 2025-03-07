import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Paper, 
  List, 
  ListItem, 
  ListItemText, 
  ListItemIcon, 
  Divider, 
  CircularProgress, 
  Alert,
  Button,
  Card,
  CardContent,
  CardActions,
  Chip
} from '@mui/material';
import { 
  Description as DocumentIcon, 
  Person as PersonIcon, 
  Work as WorkIcon, 
  ArrowForward as ArrowForwardIcon
} from '@mui/icons-material';
import { Link as RouterLink } from 'react-router-dom';
import { candidateApi, positionApi, documentApi } from '../services/api';
import { useAuth } from '../context/AuthContext';

// Define types
interface DashboardStats {
  totalCandidates: number;
  totalPositions: number;
  totalDocuments: number;
  candidatesByStatus: Record<string, number>;
  recentCandidates: any[];
  recentPositions: any[];
  recentDocuments: any[];
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalCandidates: 0,
    totalPositions: 0,
    totalDocuments: 0,
    candidatesByStatus: {},
    recentCandidates: [],
    recentPositions: [],
    recentDocuments: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user } = useAuth();

  // Fetch dashboard data
  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        // Fetch candidates
        const candidatesResponse = await candidateApi.getCandidates({ limit: 5 });
        const candidates = candidatesResponse.items || [];
        const totalCandidates = candidatesResponse.total || 0;

        // Calculate candidates by status
        const statusCounts: Record<string, number> = {};
        candidates.forEach((candidate: any) => {
          const status = candidate.status;
          statusCounts[status] = (statusCounts[status] || 0) + 1;
        });

        // Fetch positions
        const positionsResponse = await positionApi.getPositions({ limit: 5 });
        const positions = positionsResponse.items || [];
        const totalPositions = positionsResponse.total || 0;

        // Fetch documents
        const documentsResponse = await documentApi.getDocuments();
        const documents = documentsResponse || [];
        const totalDocuments = documents.length;

        // Update stats
        setStats({
          totalCandidates,
          totalPositions,
          totalDocuments,
          candidatesByStatus: statusCounts,
          recentCandidates: candidates,
          recentPositions: positions,
          recentDocuments: documents.slice(0, 5)
        });
      } catch (err: any) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // Status color mapping
  const getStatusColor = (status: string): string => {
    const statusMap: Record<string, string> = {
      'new': 'primary',
      'screening': 'info',
      'interview': 'warning',
      'offer': 'success',
      'rejected': 'error',
      'hired': 'success'
    };
    return statusMap[status.toLowerCase()] || 'default';
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ mt: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Dashboard
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Welcome back, {user?.full_name || user?.username || 'User'}
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <PersonIcon color="primary" sx={{ fontSize: 40, mr: 2 }} />
                <Box>
                  <Typography variant="h4">{stats.totalCandidates}</Typography>
                  <Typography variant="body2" color="text.secondary">Total Candidates</Typography>
                </Box>
              </Box>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {Object.entries(stats.candidatesByStatus).map(([status, count]) => (
                  <Chip 
                    key={status}
                    label={`${status}: ${count}`}
                    color={getStatusColor(status) as any}
                    size="small"
                  />
                ))}
              </Box>
            </CardContent>
            <CardActions>
              <Button 
                size="small" 
                component={RouterLink} 
                to="/candidates"
                endIcon={<ArrowForwardIcon />}
              >
                View All Candidates
              </Button>
            </CardActions>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <WorkIcon color="primary" sx={{ fontSize: 40, mr: 2 }} />
                <Box>
                  <Typography variant="h4">{stats.totalPositions}</Typography>
                  <Typography variant="body2" color="text.secondary">Open Positions</Typography>
                </Box>
              </Box>
            </CardContent>
            <CardActions>
              <Button 
                size="small" 
                component={RouterLink} 
                to="/positions"
                endIcon={<ArrowForwardIcon />}
              >
                View All Positions
              </Button>
            </CardActions>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <DocumentIcon color="primary" sx={{ fontSize: 40, mr: 2 }} />
                <Box>
                  <Typography variant="h4">{stats.totalDocuments}</Typography>
                  <Typography variant="body2" color="text.secondary">Total Documents</Typography>
                </Box>
              </Box>
            </CardContent>
            <CardActions>
              <Button 
                size="small" 
                component={RouterLink} 
                to="/documents"
                endIcon={<ArrowForwardIcon />}
              >
                View All Documents
              </Button>
            </CardActions>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Items */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Recent Candidates
            </Typography>
            {stats.recentCandidates.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No candidates added yet. Go to the Candidates section to add your first candidate.
              </Typography>
            ) : (
              <List>
                {stats.recentCandidates.map((candidate) => (
                  <React.Fragment key={candidate.id}>
                    <ListItem>
                      <ListItemIcon>
                        <PersonIcon />
                      </ListItemIcon>
                      <ListItemText 
                        primary={candidate.name} 
                        secondary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body2">{candidate.email}</Typography>
                            <Chip 
                              label={candidate.status} 
                              size="small" 
                              color={getStatusColor(candidate.status) as any}
                            />
                          </Box>
                        } 
                      />
                    </ListItem>
                    <Divider variant="inset" component="li" />
                  </React.Fragment>
                ))}
              </List>
            )}
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Recent Positions
            </Typography>
            {stats.recentPositions.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No positions added yet. Go to the Positions section to add your first position.
              </Typography>
            ) : (
              <List>
                {stats.recentPositions.map((position) => (
                  <React.Fragment key={position.id}>
                    <ListItem>
                      <ListItemIcon>
                        <WorkIcon />
                      </ListItemIcon>
                      <ListItemText 
                        primary={position.title} 
                        secondary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body2">{position.department_name}</Typography>
                            <Typography variant="body2">•</Typography>
                            <Typography variant="body2">{position.location}</Typography>
                            <Chip 
                              label={position.is_active ? 'Active' : 'Inactive'} 
                              size="small" 
                              color={position.is_active ? 'success' : 'default'}
                            />
                          </Box>
                        } 
                      />
                    </ListItem>
                    <Divider variant="inset" component="li" />
                  </React.Fragment>
                ))}
              </List>
            )}
          </Paper>
        </Grid>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Documents
            </Typography>
            {stats.recentDocuments.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No documents uploaded yet. Go to the Documents section to upload your first document.
              </Typography>
            ) : (
              <List>
                {stats.recentDocuments.map((document) => (
                  <React.Fragment key={document.id}>
                    <ListItem>
                      <ListItemIcon>
                        <DocumentIcon />
                      </ListItemIcon>
                      <ListItemText 
                        primary={document.title || document.filename} 
                        secondary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body2">{document.category || 'Uncategorized'}</Typography>
                            <Typography variant="body2">•</Typography>
                            <Typography variant="body2">
                              {new Date(document.upload_date).toLocaleDateString()}
                            </Typography>
                          </Box>
                        } 
                      />
                    </ListItem>
                    <Divider variant="inset" component="li" />
                  </React.Fragment>
                ))}
              </List>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard; 