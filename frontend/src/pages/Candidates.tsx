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
  Divider,
  Autocomplete
} from '@mui/material';
import { 
  Add as AddIcon, 
  Edit as EditIcon, 
  Delete as DeleteIcon,
  Search as SearchIcon,
  Mail as MailIcon, 
  Phone as PhoneIcon,
  Badge as BadgeIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';
import { candidateApi, skillApi, aiApi, positionApi } from '../services/api';

// Define types
interface Candidate {
  id: number;
  name: string;
  email: string;
  phone: string;
  resume_path: string | null;
  position: Position | null;
  status: string;
  created_date: string;
  updated_date: string;
  skills: Skill[];
  skill_match_score?: number;
}

interface Skill {
  id: number;
  name: string;
  category: string;
}

interface CandidateFormData {
  name: string;
  email: string;
  phone: string;
  status: string;
  position_id?: number | null;
  resume?: File | null;
  skills: string[];
}

interface Position {
  id: number;
  title?: string;
  name?: string;
}

// Resume Analysis Dialog Component
interface ResumeAnalysisDialogProps {
  open: boolean;
  onClose: () => void;
  candidateId: number | null;
}

interface ResumeAnalysisResult {
  skills: string[];
  experience_years: number;
  education: string;
  summary: string;
  match_score?: number;
}

const statusColors: Record<string, string> = {
  'new': 'info',
  'reviewing': 'warning',
  'interview': 'primary',
  'offer': 'secondary',
  'rejected': 'error',
  'hired': 'success',
};

const ResumeAnalysisDialog: React.FC<ResumeAnalysisDialogProps> = ({ open, onClose, candidateId }) => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ResumeAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const analyzeResume = async () => {
    if (!candidateId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const data = await aiApi.analyzeResume(candidateId);
      setResult(data);
    } catch (err: any) {
      console.error('Error analyzing resume:', err);
      setError(err.response?.data?.detail || 'Failed to analyze resume');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (open && candidateId) {
      analyzeResume();
    } else {
      setResult(null);
      setError(null);
    }
  }, [open, candidateId]);

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        Resume Analysis
        {loading && <CircularProgress size={24} sx={{ ml: 2 }} />}
      </DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        {result && (
          <Box>
            <Typography variant="h6" gutterBottom>Summary</Typography>
            <Typography paragraph>{result.summary}</Typography>
            
            <Divider sx={{ my: 2 }} />
            
            <Typography variant="h6" gutterBottom>Skills</Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
              {result.skills.map((skill, index) => (
                <Chip key={index} label={skill} color="primary" variant="outlined" />
              ))}
            </Box>
            
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="h6" gutterBottom>Experience</Typography>
                <Typography>{result.experience_years} years</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="h6" gutterBottom>Position Match</Typography>
                <Typography>
                  {result.match_score 
                    ? `${Math.round(result.match_score)}% match` 
                    : 'No position selected'}
                </Typography>
              </Grid>
            </Grid>
            
            <Divider sx={{ my: 2 }} />
            
            <Typography variant="h6" gutterBottom>Education</Typography>
            <Typography paragraph>{result.education}</Typography>
          </Box>
        )}
        
        {!result && !error && !loading && (
          <Typography>
            Loading resume analysis...
          </Typography>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

const Candidates: React.FC = () => {
  // State variables
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [positions, setPositions] = useState<Position[]>([]);
  const [availableSkills, setAvailableSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [currentCandidate, setCurrentCandidate] = useState<Candidate | null>(null);
  const [formData, setFormData] = useState<CandidateFormData>({
    name: '',
    email: '',
    phone: '',
    status: 'new',
    position_id: null,
    resume: null,
    skills: []
  });
  const [formMode, setFormMode] = useState<'add' | 'edit'>('add');
  const [notification, setNotification] = useState({ open: false, message: '', type: 'success' as 'success' | 'error' });
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [newSkill, setNewSkill] = useState('');
  const [analysisDialogOpen, setAnalysisDialogOpen] = useState(false);
  const [selectedCandidateForAnalysis, setSelectedCandidateForAnalysis] = useState<number | null>(null);

  // Fetch candidates
  const fetchCandidates = async () => {
    setLoading(true);
    try {
      const params = {
        skip: page * rowsPerPage,
        limit: rowsPerPage,
        search: searchQuery || undefined
      };
      const response = await candidateApi.getCandidates(params);
      
      // Handle both array and paginated response formats
      if (response.items) {
        setCandidates(response.items);
        setTotalCount(response.total || response.items.length);
      } else if (Array.isArray(response)) {
        setCandidates(response);
        setTotalCount(response.length);
      } else {
        setCandidates([]);
        setTotalCount(0);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch candidates');
      setNotification({
        open: true, 
        message: 'Failed to fetch candidates', 
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  // Fetch skills
  const fetchSkills = async () => {
    try {
      const response = await skillApi.getSkills();
      if (Array.isArray(response)) {
        setAvailableSkills(response);
      } else if (response.items) {
        setAvailableSkills(response.items);
      } else {
        setAvailableSkills([]);
      }
    } catch (err) {
      console.error('Failed to fetch skills:', err);
      setNotification({
        open: true,
        message: 'Failed to fetch skills',
        type: 'error'
      });
    }
  };

  // Fetch positions
  const fetchPositions = async () => {
    try {
      const response = await positionApi.getPositions();
      if (response.items) {
        setPositions(response.items);
      } else if (Array.isArray(response)) {
        setPositions(response);
      } else {
        setPositions([]);
      }
    } catch (err) {
      console.error('Failed to fetch positions:', err);
    }
  };

  // Fetch data on component mount and when dependencies change
  useEffect(() => {
    fetchCandidates();
  }, [page, rowsPerPage, searchQuery]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    fetchSkills();
    fetchPositions();
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
  const handleStatusChange = (event: any) => {
    setFormData(prev => ({ ...prev, status: event.target.value }));
  };

  // Handle resume file change
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setFormData(prev => ({ ...prev, resume: event.target.files![0] }));
    }
  };

  // Handle adding a new skill
  const handleAddSkill = () => {
    if (newSkill && !selectedSkills.includes(newSkill)) {
      setSelectedSkills([...selectedSkills, newSkill]);
      setNewSkill('');
    }
  };

  // Handle removing a skill
  const handleRemoveSkill = (skill: string) => {
    setSelectedSkills(selectedSkills.filter(s => s !== skill));
  };

  // Open dialog for adding a new candidate
  const handleOpenAddDialog = () => {
    setFormData({
      name: '',
      email: '',
      phone: '',
      status: 'new',
      position_id: null,
      resume: null,
      skills: []
    });
    setSelectedSkills([]);
    setFormMode('add');
    setOpenDialog(true);
  };

  // Open dialog for editing a candidate
  const handleOpenEditDialog = (candidate: Candidate) => {
    setCurrentCandidate(candidate);
    setFormData({
      name: candidate.name,
      email: candidate.email,
      phone: candidate.phone,
      status: candidate.status,
      position_id: candidate.position?.id || null,
      resume: null,
      skills: []
    });
    setSelectedSkills(candidate.skills.map(skill => skill.name));
    setFormMode('edit');
    setOpenDialog(true);
  };

  // Close dialog
  const handleCloseDialog = () => {
    setOpenDialog(false);
    setCurrentCandidate(null);
  };

  // Submit form for adding or editing a candidate
  const handleSubmit = async () => {
    setLoading(true);
    try {
      // Create FormData object for file upload
      const formDataObj = new FormData();
      formDataObj.append('name', formData.name);
      formDataObj.append('email', formData.email);
      formDataObj.append('phone', formData.phone);
      formDataObj.append('status', formData.status);
      formDataObj.append('position_id', formData.position_id?.toString() || '');
      
      if (formData.resume) {
        formDataObj.append('resume', formData.resume);
      }
      
      if (formMode === 'add') {
        // Add new candidate
        const newCandidate = await candidateApi.createCandidate(formDataObj);
        
        // Add skills if any
        if (selectedSkills.length > 0) {
          await candidateApi.addSkillsToCandidate(newCandidate.id, selectedSkills);
        }
        
        setNotification({
          open: true,
          message: 'Candidate added successfully',
          type: 'success'
        });
      } else if (currentCandidate) {
        // Update existing candidate
        await candidateApi.updateCandidate(currentCandidate.id, formDataObj);
        
        // Update skills
        // First, get the current skills to compare
        const currentSkillNames = currentCandidate.skills.map(s => s.name);
        
        // Add skills that are new
        const skillsToAdd = selectedSkills.filter(skill => !currentSkillNames.includes(skill));
        if (skillsToAdd.length > 0) {
          await candidateApi.addSkillsToCandidate(currentCandidate.id, skillsToAdd);
        }
        
        // Remove skills that are no longer selected
        const skillsToRemove = currentCandidate.skills.filter(skill => !selectedSkills.includes(skill.name));
        for (const skill of skillsToRemove) {
          await candidateApi.removeSkillFromCandidate(currentCandidate.id, skill.id);
        }
        
        setNotification({
          open: true,
          message: 'Candidate updated successfully',
          type: 'success'
        });
      }
      
      // Refresh candidate list
      fetchCandidates();
      handleCloseDialog();
    } catch (err: any) {
      setError(err.message || 'Failed to save candidate');
      setNotification({
        open: true,
        message: `Failed to ${formMode === 'add' ? 'add' : 'update'} candidate: ${err.message}`,
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  // Open delete confirmation dialog
  const handleOpenDeleteDialog = (candidate: Candidate) => {
    setCurrentCandidate(candidate);
    setDeleteDialogOpen(true);
  };

  // Close delete confirmation dialog
  const handleCloseDeleteDialog = () => {
    setDeleteDialogOpen(false);
    setCurrentCandidate(null);
  };

  // Delete a candidate
  const handleDeleteCandidate = async () => {
    if (!currentCandidate) return;
    
    setLoading(true);
    try {
      await candidateApi.deleteCandidate(currentCandidate.id);
      fetchCandidates();
      setNotification({
        open: true,
        message: 'Candidate deleted successfully',
        type: 'success'
      });
      handleCloseDeleteDialog();
    } catch (err: any) {
      setError(err.message || 'Failed to delete candidate');
      setNotification({
        open: true,
        message: `Failed to delete candidate: ${err.message}`,
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

  const handleAnalyzeResume = (candidateId: number) => {
    setSelectedCandidateForAnalysis(candidateId);
    setAnalysisDialogOpen(true);
  };
  
  const handleAnalysisDialogClose = () => {
    setAnalysisDialogOpen(false);
    setSelectedCandidateForAnalysis(null);
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Candidates
        </Typography>
        <Button 
          variant="contained" 
          startIcon={<AddIcon />}
          onClick={handleOpenAddDialog}
        >
          Add Candidate
        </Button>
      </Box>

      <Paper sx={{ mb: 3, p: 2 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Search candidates..."
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

      {loading && candidates.length === 0 ? (
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
                  <TableCell>Name</TableCell>
                  <TableCell>Contact</TableCell>
                  <TableCell>Skills</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {candidates.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} align="center">
                      No candidates found
                    </TableCell>
                  </TableRow>
                ) : (
                  candidates.map((candidate) => (
                    <TableRow key={candidate.id}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <BadgeIcon sx={{ mr: 1, color: 'primary.main' }} />
                          <Box>
                            <Typography variant="body1" fontWeight="medium">
                              {candidate.name}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Added on {new Date(candidate.created_date).toLocaleDateString()}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <MailIcon fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                            <Typography variant="body2">{candidate.email}</Typography>
                          </Box>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <PhoneIcon fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                            <Typography variant="body2">{candidate.phone}</Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {candidate.skills.length > 0 ? (
                            candidate.skills.map((skill) => (
                              <Chip 
                                key={skill.id} 
                                label={skill.name} 
                                size="small" 
                                sx={{ mr: 0.5, mb: 0.5 }}
                              />
                            ))
                          ) : (
                            <Typography variant="body2" color="text.secondary">
                              No skills listed
                            </Typography>
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={candidate.status} 
                          color={statusColors[candidate.status.toLowerCase()] as any || 'default'}
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex' }}>
                          <IconButton 
                            color="primary"
                            onClick={() => handleOpenEditDialog(candidate)}
                          >
                            <EditIcon />
                          </IconButton>
                          <IconButton 
                            color="error"
                            onClick={() => handleOpenDeleteDialog(candidate)}
                          >
                            <DeleteIcon />
                          </IconButton>
                          {candidate.resume_path && (
                            <IconButton
                              size="small"
                              onClick={() => handleAnalyzeResume(candidate.id)}
                              color="primary"
                            >
                              <AssessmentIcon fontSize="small" />
                            </IconButton>
                          )}
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

      {/* Add/Edit candidate dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {formMode === 'add' ? 'Add New Candidate' : 'Edit Candidate'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0.5 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleInputChange}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Phone"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel id="status-label">Status</InputLabel>
                <Select
                  labelId="status-label"
                  name="status"
                  value={formData.status}
                  onChange={handleStatusChange}
                  label="Status"
                >
                  <MenuItem value="new">New</MenuItem>
                  <MenuItem value="reviewing">Reviewing</MenuItem>
                  <MenuItem value="interview">Interview</MenuItem>
                  <MenuItem value="offer">Offer</MenuItem>
                  <MenuItem value="hired">Hired</MenuItem>
                  <MenuItem value="rejected">Rejected</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel id="position-label">Position</InputLabel>
                <Select
                  labelId="position-label"
                  name="position_id"
                  value={formData.position_id || ''}
                  onChange={(e) => setFormData(prev => ({ ...prev, position_id: e.target.value ? Number(e.target.value) : null }))}
                  label="Position"
                >
                  <MenuItem value="">
                    <em>None</em>
                  </MenuItem>
                  {positions.map((position) => (
                    <MenuItem key={position.id} value={position.id}>
                      {position.title}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <Button
                variant="outlined"
                component="label"
                fullWidth
                sx={{ height: '56px' }}
              >
                {formData.resume ? 'Change Resume' : 'Upload Resume'}
                <input
                  type="file"
                  accept=".pdf,.doc,.docx"
                  hidden
                  onChange={handleFileChange}
                />
              </Button>
              {formData.resume && (
                <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                  Selected file: {formData.resume.name}
                </Typography>
              )}
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle1" sx={{ mb: 1 }}>
                Skills
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Typography variant="subtitle1">Selected Skills:</Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {selectedSkills.map((skill) => (
                    <Chip
                      key={skill}
                      label={skill}
                      onDelete={() => handleRemoveSkill(skill)}
                      color="primary"
                      variant="outlined"
                    />
                  ))}
                </Box>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Autocomplete
                    freeSolo
                    options={availableSkills.map(skill => skill.name)}
                    value={newSkill}
                    onChange={(_, value) => setNewSkill(value || '')}
                    onInputChange={(_, value) => setNewSkill(value)}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label="Add a skill"
                        fullWidth
                      />
                    )}
                    sx={{ flexGrow: 1 }}
                  />
                  <Button
                    variant="contained"
                    onClick={handleAddSkill}
                    disabled={!newSkill}
                  >
                    Add
                  </Button>
                </Box>
              </Box>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={loading || !formData.name || !formData.email || !formData.phone}
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
            Are you sure you want to delete the candidate "{currentCandidate?.name}"? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog}>Cancel</Button>
          <Button onClick={handleDeleteCandidate} color="error" variant="contained">
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

      {/* Add the Analysis Dialog */}
      <ResumeAnalysisDialog
        open={analysisDialogOpen}
        onClose={handleAnalysisDialogClose}
        candidateId={selectedCandidateForAnalysis}
      />
    </Box>
  );
};

export default Candidates; 