import React, { useState, useEffect, useRef } from 'react';
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
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  IconButton,
  CircularProgress,
  Chip,
  Alert,
  Snackbar,
  Grid
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DeleteIcon from '@mui/icons-material/Delete';
import GetAppIcon from '@mui/icons-material/GetApp';
import VisibilityIcon from '@mui/icons-material/Visibility';
import { documentApi } from '../services/api';

interface Document {
  id: number;
  title: string;
  category: string;
  created_at: string;
  offline_available: boolean;
  file_path: string;
}

const Documents: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('General');
  const [offlineAvailable, setOfflineAvailable] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [notification, setNotification] = useState({ open: false, message: '', type: 'success' as 'success' | 'error' });
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Fetch documents on component mount
  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const data = await documentApi.getDocuments();
      setDocuments(data || []);
    } catch (error) {
      console.error('Error fetching documents:', error);
      setNotification({
        open: true,
        message: 'Failed to fetch documents',
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleClickOpen = () => {
    setOpen(true);
    setTitle('');
    setCategory('General');
    setOfflineAvailable(false);
    setSelectedFile(null);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      setSelectedFile(file);
      
      // Auto-fill title with filename (without extension) if title is empty
      if (!title) {
        const filename = file.name.split('.').slice(0, -1).join('.');
        setTitle(filename);
      }
    }
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!selectedFile) {
      setNotification({
        open: true,
        message: 'Please select a file to upload',
        type: 'error'
      });
      return;
    }
    
    setUploadLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('title', title);
      formData.append('category', category);
      formData.append('offline_available', String(offlineAvailable));
      
      await documentApi.uploadDocument(formData);
      
      setNotification({
        open: true,
        message: 'Document uploaded successfully',
        type: 'success'
      });
      
      handleClose();
      fetchDocuments();
    } catch (error) {
      console.error('Error uploading document:', error);
      setNotification({
        open: true,
        message: 'Failed to upload document',
        type: 'error'
      });
    } finally {
      setUploadLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await documentApi.deleteDocument(id);
      setNotification({
        open: true,
        message: 'Document deleted successfully',
        type: 'success'
      });
      
      // Update documents list
      setDocuments(documents.filter(doc => doc.id !== id));
    } catch (error) {
      console.error('Error deleting document:', error);
      setNotification({
        open: true,
        message: 'Failed to delete document',
        type: 'error'
      });
    }
  };

  const handleCloseNotification = () => {
    setNotification({ ...notification, open: false });
  };

  // Calculate file size for display
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Documents</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleClickOpen}
        >
          Upload Document
        </Button>
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : documents.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No documents found
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Upload your first document to get started
          </Typography>
          <Button 
            variant="outlined" 
            startIcon={<CloudUploadIcon />}
            onClick={handleClickOpen}
          >
            Upload Document
          </Button>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Title</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Uploaded</TableCell>
                <TableCell>Offline Available</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {documents.map((doc) => (
                <TableRow key={doc.id}>
                  <TableCell>{doc.title}</TableCell>
                  <TableCell>
                    <Chip label={doc.category} size="small" />
                  </TableCell>
                  <TableCell>{new Date(doc.created_at).toLocaleDateString()}</TableCell>
                  <TableCell>
                    {doc.offline_available ? (
                      <Chip label="Available Offline" color="success" size="small" />
                    ) : (
                      <Chip label="Online Only" variant="outlined" size="small" />
                    )}
                  </TableCell>
                  <TableCell>
                    <IconButton 
                      size="small" 
                      color="primary" 
                      onClick={() => {
                        // Get the auth token
                        const token = localStorage.getItem('token');
                        // Create a hidden anchor and trigger download
                        const link = document.createElement('a');
                        link.href = `http://localhost:8000/api/v1/documents/${doc.id}/download`;
                        link.setAttribute('download', doc.title);
                        link.setAttribute('target', '_blank');
                        // Add auth header via fetch
                        fetch(link.href, {
                          headers: {
                            'Authorization': `Bearer ${token}`
                          }
                        })
                        .then(response => response.blob())
                        .then(blob => {
                          const url = window.URL.createObjectURL(blob);
                          link.href = url;
                          document.body.appendChild(link);
                          link.click();
                          document.body.removeChild(link);
                          window.URL.revokeObjectURL(url);
                        })
                        .catch(error => {
                          console.error('Error downloading document:', error);
                          setNotification({
                            open: true,
                            message: 'Failed to download document',
                            type: 'error'
                          });
                        });
                      }}
                    >
                      <GetAppIcon />
                    </IconButton>
                    <IconButton 
                      size="small" 
                      color="info"
                      onClick={() => {
                        // Get the auth token
                        const token = localStorage.getItem('token');
                        // Open the document in a new window with authentication
                        const viewWindow = window.open('about:blank', '_blank');
                        
                        if (viewWindow) {
                          // Create a form to send the token
                          viewWindow.document.write(`
                            <html>
                              <head>
                                <title>Loading Document...</title>
                                <script>
                                  // Create a fetch request with authorization header
                                  fetch('http://localhost:8000/api/v1/documents/${doc.id}/view', {
                                    headers: {
                                      'Authorization': 'Bearer ${token}'
                                    }
                                  })
                                  .then(response => {
                                    if (!response.ok) throw new Error('Network response was not ok');
                                    return response.blob();
                                  })
                                  .then(blob => {
                                    // Create object URL and redirect
                                    const url = URL.createObjectURL(blob);
                                    window.location.href = url;
                                  })
                                  .catch(error => {
                                    document.body.innerHTML = '<h3>Error loading document: ' + error.message + '</h3>';
                                  });
                                </script>
                                <style>
                                  body {
                                    font-family: Arial, sans-serif;
                                    display: flex;
                                    justify-content: center;
                                    align-items: center;
                                    height: 100vh;
                                    margin: 0;
                                  }
                                  .loader {
                                    border: 5px solid #f3f3f3;
                                    border-top: 5px solid #3498db;
                                    border-radius: 50%;
                                    width: 50px;
                                    height: 50px;
                                    animation: spin 1s linear infinite;
                                    margin-right: 20px;
                                  }
                                  @keyframes spin {
                                    0% { transform: rotate(0deg); }
                                    100% { transform: rotate(360deg); }
                                  }
                                  .container {
                                    display: flex;
                                    align-items: center;
                                  }
                                </style>
                              </head>
                              <body>
                                <div class="container">
                                  <div class="loader"></div>
                                  <h2>Loading document, please wait...</h2>
                                </div>
                              </body>
                            </html>
                          `);
                        } else {
                          setNotification({
                            open: true,
                            message: 'Failed to open document. Please check popup blocker settings.',
                            type: 'error'
                          });
                        }
                      }}
                    >
                      <VisibilityIcon />
                    </IconButton>
                    <IconButton 
                      size="small" 
                      color="error"
                      onClick={() => handleDelete(doc.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Upload Dialog */}
      <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogTitle>Upload Document</DialogTitle>
        <form onSubmit={handleSubmit}>
          <DialogContent>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  autoFocus
                  margin="dense"
                  id="title"
                  label="Document Title"
                  type="text"
                  fullWidth
                  variant="outlined"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth margin="dense" required>
                  <InputLabel id="category-label">Category</InputLabel>
                  <Select
                    labelId="category-label"
                    id="category"
                    label="Category"
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                  >
                    <MenuItem value="General">General</MenuItem>
                    <MenuItem value="Policy">Policy</MenuItem>
                    <MenuItem value="Procedure">Procedure</MenuItem>
                    <MenuItem value="Form">Form</MenuItem>
                    <MenuItem value="Guide">Guide</MenuItem>
                    <MenuItem value="Template">Template</MenuItem>
                    <MenuItem value="Resume">Resume</MenuItem>
                    <MenuItem value="Other">Other</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <Box 
                  sx={{ 
                    border: '1px dashed #ccc', 
                    borderRadius: 1, 
                    p: 3, 
                    textAlign: 'center',
                    bgcolor: 'background.paper',
                    cursor: 'pointer',
                    '&:hover': { borderColor: 'primary.main' },
                    mb: 2
                  }}
                  onClick={handleBrowseClick}
                >
                  <input
                    type="file"
                    ref={fileInputRef}
                    style={{ display: 'none' }}
                    onChange={handleFileSelect}
                  />
                  
                  {selectedFile ? (
                    <Box>
                      <Typography variant="subtitle1" color="primary" gutterBottom>
                        {selectedFile.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {formatFileSize(selectedFile.size)}
                      </Typography>
                      <Button 
                        variant="outlined" 
                        size="small" 
                        sx={{ mt: 1 }}
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedFile(null);
                        }}
                      >
                        Change File
                      </Button>
                    </Box>
                  ) : (
                    <Box>
                      <CloudUploadIcon color="primary" sx={{ fontSize: 40, mb: 1 }} />
                      <Typography variant="subtitle1" gutterBottom>
                        Click to select a file
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        or drag and drop file here
                      </Typography>
                    </Box>
                  )}
                </Box>
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch 
                      checked={offlineAvailable}
                      onChange={(e) => setOfflineAvailable(e.target.checked)}
                    />
                  }
                  label="Available Offline"
                  sx={{ mt: 2 }}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>Cancel</Button>
            <Button 
              type="submit" 
              variant="contained"
              disabled={!selectedFile || uploadLoading}
              startIcon={uploadLoading ? <CircularProgress size={20} color="inherit" /> : null}
            >
              {uploadLoading ? 'Uploading...' : 'Upload'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Notification Snackbar */}
      <Snackbar
        open={notification.open}
        autoHideDuration={4000}
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

export default Documents; 