import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  IconButton,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  TextField,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Snackbar,
  InputAdornment,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  Business as BusinessIcon,
  LocationOn as LocationIcon,
  AttachMoney as SalaryIcon,
  Work as WorkIcon
} from '@mui/icons-material';
import { positionApi, departmentApi } from '../services/api';

// Define types
interface Position {
  id: number;
  title: string;
  department_id: number;
  department_name: string;
  location: string;
  salary_range: string;
  description: string;
  requirements: string;
  responsibilities: string;
  is_active: boolean;
  created_date: string;
  updated_date: string;
}

interface Department {
  id: number;
  name: string;
  description: string;
}

interface PositionFormData {
  title: string;
  department_id: number;
  location: string;
  salary_range: string;
  description: string;
  requirements: string;
  responsibilities: string;
  is_active: boolean;
}

const Positions: React.FC = () => {
  // State variables
  const [positions, setPositions] = useState<Position[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [currentPosition, setCurrentPosition] = useState<Position | null>(null);
  const [formData, setFormData] = useState<PositionFormData>({
    title: '',
    department_id: 0,
    location: '',
    salary_range: '',
    description: '',
    requirements: '',
    responsibilities: '',
    is_active: true
  });
  const [formMode, setFormMode] = useState<'add' | 'edit'>('add');
  const [notification, setNotification] = useState({ open: false, message: '', type: 'success' as 'success' | 'error' });

  // Fetch positions
  const fetchPositions = async () => {
    setLoading(true);
    try {
      const params = {
        skip: page * rowsPerPage,
        limit: rowsPerPage,
        search: searchQuery || undefined
      };
      const response = await positionApi.getPositions(params);
      
      // Handle both array and paginated response formats
      if (response.items) {
        setPositions(response.items);
        setTotalCount(response.total || response.items.length);
      } else if (Array.isArray(response)) {
        setPositions(response);
        setTotalCount(response.length);
      } else {
        setPositions([]);
        setTotalCount(0);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch positions');
      setNotification({
        open: true,
        message: 'Failed to fetch positions',
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  // Fetch departments
  const fetchDepartments = async () => {
    try {
      const response = await departmentApi.getDepartments();
      
      // Handle both array and object response formats
      if (Array.isArray(response)) {
        setDepartments(response);
      } else if (response && typeof response === 'object') {
        // If it's an object with items property
        if (Array.isArray(response.items)) {
          setDepartments(response.items);
        } else {
          // If it's some other object structure, try to convert to array
          const deptArray = Object.values(response).filter(item => 
            item && typeof item === 'object' && 'id' in item && 'name' in item
          );
          setDepartments(deptArray as Department[]);
        }
      } else {
        setDepartments([]);
      }
    } catch (err) {
      console.error('Failed to fetch departments:', err);
      setNotification({
        open: true,
        message: 'Failed to fetch departments',
        type: 'error'
      });
    }
  };

  // Fetch data on component mount and when dependencies change
  useEffect(() => {
    fetchPositions();
  }, [page, rowsPerPage, searchQuery]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    fetchDepartments();
  }, []);

  // Handle page change
  const handleChangePage = (_: unknown, newPage: number) => {
    setPage(newPage);
  };

  // Handle rows per page change
  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Handle search
  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(event.target.value);
    setPage(0);
  };

  // Handle form input changes
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  // Handle status change
  const handleStatusChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, is_active: event.target.checked }));
  };

  // Handle department change
  const handleDepartmentChange = (event: any) => {
    setFormData(prev => ({ ...prev, department_id: event.target.value }));
  };

  // Open dialog for adding a new position
  const handleOpenAddDialog = () => {
    setFormData({
      title: '',
      department_id: departments.length > 0 ? departments[0].id : 0,
      location: '',
      salary_range: '',
      description: '',
      requirements: '',
      responsibilities: '',
      is_active: true
    });
    setFormMode('add');
    setOpenDialog(true);
  };

  // Open dialog for editing a position
  const handleOpenEditDialog = (position: Position) => {
    setCurrentPosition(position);
    setFormData({
      title: position.title,
      department_id: position.department_id,
      location: position.location,
      salary_range: position.salary_range,
      description: position.description,
      requirements: position.requirements,
      responsibilities: position.responsibilities,
      is_active: position.is_active
    });
    setFormMode('edit');
    setOpenDialog(true);
  };

  // Close dialog
  const handleCloseDialog = () => {
    setOpenDialog(false);
    setCurrentPosition(null);
  };

  // Submit form for adding or editing a position
  const handleSubmit = async () => {
    setLoading(true);
    try {
      if (formMode === 'add') {
        // Add new position
        await positionApi.createPosition(formData);
        setNotification({
          open: true,
          message: 'Position added successfully',
          type: 'success'
        });
      } else if (currentPosition) {
        // Update existing position
        await positionApi.updatePosition(currentPosition.id, formData);
        setNotification({
          open: true,
          message: 'Position updated successfully',
          type: 'success'
        });
      }
      
      // Refresh position list
      fetchPositions();
      handleCloseDialog();
    } catch (err: any) {
      setError(err.message || 'Failed to save position');
      setNotification({
        open: true,
        message: `Failed to ${formMode === 'add' ? 'add' : 'update'} position: ${err.message}`,
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  // Toggle position status
  const handleToggleStatus = async (position: Position) => {
    setLoading(true);
    try {
      await positionApi.togglePositionStatus(position.id);
      fetchPositions();
      setNotification({
        open: true,
        message: `Position ${position.is_active ? 'deactivated' : 'activated'} successfully`,
        type: 'success'
      });
    } catch (err: any) {
      setError(err.message || 'Failed to toggle position status');
      setNotification({
        open: true,
        message: `Failed to toggle position status: ${err.message}`,
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  // Open delete confirmation dialog
  const handleOpenDeleteDialog = (position: Position) => {
    setCurrentPosition(position);
    setDeleteDialogOpen(true);
  };

  // Close delete confirmation dialog
  const handleCloseDeleteDialog = () => {
    setDeleteDialogOpen(false);
    setCurrentPosition(null);
  };

  // Delete a position
  const handleDeletePosition = async () => {
    if (!currentPosition) return;
    
    setLoading(true);
    try {
      await positionApi.deletePosition(currentPosition.id);
      fetchPositions();
      setNotification({
        open: true,
        message: 'Position deleted successfully',
        type: 'success'
      });
      handleCloseDeleteDialog();
    } catch (err: any) {
      setError(err.message || 'Failed to delete position');
      setNotification({
        open: true,
        message: `Failed to delete position: ${err.message}`,
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  // Close notification
  const handleCloseNotification = () => {
    setNotification({ ...notification, open: false });
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Positions
        </Typography>
        <Button 
          variant="contained" 
          startIcon={<AddIcon />}
          onClick={handleOpenAddDialog}
        >
          Add Position
        </Button>
      </Box>

      <Paper sx={{ mb: 3, p: 2 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Search positions by title, department, or location..."
          value={searchQuery}
          onChange={handleSearchChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
      </Paper>

      {loading && positions.length === 0 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      ) : (
        <Paper>
          <TableContainer>
            <Table sx={{ minWidth: 650 }}>
              <TableHead>
                <TableRow>
                  <TableCell>Title</TableCell>
                  <TableCell>Department</TableCell>
                  <TableCell>Location</TableCell>
                  <TableCell>Salary Range</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {positions.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      No positions found
                    </TableCell>
                  </TableRow>
                ) : (
                  positions.map((position) => (
                    <TableRow key={position.id}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <WorkIcon sx={{ mr: 1, color: 'primary.main' }} />
                          <Box>
                            <Typography variant="body1" fontWeight="medium">
                              {position.title}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Added on {new Date(position.created_date).toLocaleDateString()}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <BusinessIcon fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                          <Typography variant="body2">{position.department_name}</Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <LocationIcon fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                          <Typography variant="body2">{position.location}</Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <SalaryIcon fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                          <Typography variant="body2">{position.salary_range}</Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={position.is_active ? 'Active' : 'Inactive'} 
                          color={position.is_active ? 'success' : 'default'}
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex' }}>
                          <IconButton 
                            color="primary"
                            onClick={() => handleOpenEditDialog(position)}
                          >
                            <EditIcon />
                          </IconButton>
                          <IconButton 
                            color="error"
                            onClick={() => handleOpenDeleteDialog(position)}
                          >
                            <DeleteIcon />
                          </IconButton>
                          <Switch
                            checked={position.is_active}
                            onChange={() => handleToggleStatus(position)}
                            color="success"
                            size="small"
                          />
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            rowsPerPageOptions={[5, 10, 25]}
            component="div"
            count={totalCount}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </Paper>
      )}

      {/* Add/Edit position dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {formMode === 'add' ? 'Add New Position' : 'Edit Position'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0.5 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Position Title"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth required>
                <InputLabel>Department</InputLabel>
                <Select
                  value={formData.department_id}
                  label="Department"
                  onChange={handleDepartmentChange}
                >
                  {departments.map((department) => (
                    <MenuItem key={department.id} value={department.id}>
                      {department.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Location"
                name="location"
                value={formData.location}
                onChange={handleInputChange}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Salary Range"
                name="salary_range"
                value={formData.salary_range}
                onChange={handleInputChange}
                placeholder="e.g. $50,000 - $70,000"
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.is_active}
                    onChange={handleStatusChange}
                    name="status"
                    color="success"
                  />
                }
                label="Active Position"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                multiline
                rows={3}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Requirements"
                name="requirements"
                value={formData.requirements}
                onChange={handleInputChange}
                multiline
                rows={3}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Responsibilities"
                name="responsibilities"
                value={formData.responsibilities}
                onChange={handleInputChange}
                multiline
                rows={3}
                required
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={loading || !formData.title || !formData.department_id || !formData.location}
          >
            {loading ? <CircularProgress size={24} /> : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete confirmation dialog */}
      <Dialog open={deleteDialogOpen} onClose={handleCloseDeleteDialog}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the position "{currentPosition?.title}"? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog}>Cancel</Button>
          <Button onClick={handleDeletePosition} color="error" variant="contained">
            {loading ? <CircularProgress size={24} color="inherit" /> : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Notification snackbar */}
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={handleCloseNotification}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <Alert
          onClose={handleCloseNotification}
          severity={notification.type}
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Positions; 