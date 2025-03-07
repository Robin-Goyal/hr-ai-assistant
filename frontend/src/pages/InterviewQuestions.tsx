import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  CircularProgress,
  Grid,
  Chip,
  IconButton,
  Divider,
  Alert,
  Snackbar,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Checkbox,
  FormGroup,
  FormControlLabel,
  Tooltip
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  FileCopy as FileCopyIcon,
  Print as PrintIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { positionApi, aiApi } from '../services/api';

interface Position {
  id: number;
  title: string;
  department_name: string;
}

interface QuestionCategory {
  id: string;
  name: string;
  checked: boolean;
}

interface Question {
  id: number;
  content: string;
  difficulty: string;
  category: string;
}

const InterviewQuestions: React.FC = () => {
  // State variables
  const [positions, setPositions] = useState<Position[]>([]);
  const [selectedPosition, setSelectedPosition] = useState<number>(0);
  const [difficulty, setDifficulty] = useState<string>('Medium');
  const [questionCount, setQuestionCount] = useState<number>(5);
  const [generatedQuestions, setGeneratedQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [fetchingPositions, setFetchingPositions] = useState<boolean>(true);
  const [notification, setNotification] = useState({ open: false, message: '', type: 'success' as 'success' | 'error' | 'info' });
  const [categories, setCategories] = useState<QuestionCategory[]>([
    { id: 'technical', name: 'Technical', checked: true },
    { id: 'behavioral', name: 'Behavioral', checked: true },
    { id: 'experience', name: 'Experience', checked: true },
    { id: 'situational', name: 'Situational', checked: false },
    { id: 'cultural', name: 'Cultural Fit', checked: false },
  ]);

  // Fetch positions on component mount
  useEffect(() => {
    const fetchPositions = async () => {
      try {
        const response = await positionApi.getPositions();
        setPositions(response.items || []);
        if (response.items && response.items.length > 0) {
          setSelectedPosition(response.items[0].id);
        }
      } catch (error) {
        console.error('Error fetching positions:', error);
        setNotification({
          open: true,
          message: 'Failed to fetch positions',
          type: 'error'
        });
      } finally {
        setFetchingPositions(false);
      }
    };

    fetchPositions();
  }, []);

  // Handle category selection
  const handleCategoryChange = (id: string) => {
    setCategories(
      categories.map(category =>
        category.id === id ? { ...category, checked: !category.checked } : category
      )
    );
  };

  // Generate interview questions
  const handleGenerateQuestions = async () => {
    if (selectedPosition === 0) {
      setNotification({
        open: true,
        message: 'Please select a position',
        type: 'error'
      });
      return;
    }

    // Check if at least one category is selected
    const selectedCategories = categories.filter(cat => cat.checked).map(cat => cat.id);
    if (selectedCategories.length === 0) {
      setNotification({
        open: true,
        message: 'Please select at least one question category',
        type: 'error'
      });
      return;
    }

    setLoading(true);
    try {
      const response = await aiApi.generateQuestions(
        selectedPosition,
        difficulty,
        questionCount,
        selectedCategories
      );
      
      setGeneratedQuestions(response.questions || []);
      setNotification({
        open: true,
        message: 'Questions generated successfully',
        type: 'success'
      });
    } catch (error) {
      console.error('Error generating questions:', error);
      setNotification({
        open: true,
        message: 'Failed to generate questions',
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  // Copy questions to clipboard
  const handleCopyQuestions = () => {
    const questionText = generatedQuestions
      .map((q, index) => `${index + 1}. ${q.content}`)
      .join('\n\n');
    
    navigator.clipboard.writeText(questionText);
    setNotification({
      open: true,
      message: 'Questions copied to clipboard',
      type: 'success'
    });
  };

  // Handle print questions
  const handlePrintQuestions = () => {
    const positionInfo = positions.find(p => p.id === selectedPosition);
    const printWindow = window.open('', '_blank');
    
    if (printWindow) {
      printWindow.document.write(`
        <html>
          <head>
            <title>Interview Questions for ${positionInfo?.title || 'Position'}</title>
            <style>
              body { font-family: Arial, sans-serif; margin: 20px; }
              h1 { color: #1976d2; }
              h2 { color: #555; font-size: 18px; margin-top: 20px; }
              ol { margin-top: 10px; }
              li { margin-bottom: 10px; line-height: 1.5; }
              .footer { margin-top: 40px; font-size: 12px; color: #777; }
            </style>
          </head>
          <body>
            <h1>Interview Questions</h1>
            <h2>Position: ${positionInfo?.title || 'Not specified'}</h2>
            <h2>Department: ${positionInfo?.department_name || 'Not specified'}</h2>
            <h2>Difficulty: ${difficulty}</h2>
            <hr />
            <ol>
              ${generatedQuestions.map(q => `<li>${q.content}</li>`).join('')}
            </ol>
            <div class="footer">
              Generated by HR Assistant on ${new Date().toLocaleDateString()}
            </div>
          </body>
        </html>
      `);
      printWindow.document.close();
      printWindow.print();
    }
  };

  // Close notification
  const handleCloseNotification = () => {
    setNotification({ ...notification, open: false });
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Interview Questions Generator
      </Typography>
      
      <Grid container spacing={3}>
        {/* Question Generation Panel */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Generation Settings
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <FormControl fullWidth margin="normal">
              <InputLabel id="position-label">Position</InputLabel>
              <Select
                labelId="position-label"
                value={selectedPosition}
                label="Position"
                onChange={(e) => setSelectedPosition(e.target.value as number)}
                disabled={fetchingPositions}
              >
                {fetchingPositions ? (
                  <MenuItem value={0}>Loading positions...</MenuItem>
                ) : positions.length === 0 ? (
                  <MenuItem value={0}>No positions available</MenuItem>
                ) : (
                  positions.map((position) => (
                    <MenuItem key={position.id} value={position.id}>
                      {position.title}
                    </MenuItem>
                  ))
                )}
              </Select>
            </FormControl>
            
            <FormControl fullWidth margin="normal">
              <InputLabel id="difficulty-label">Difficulty</InputLabel>
              <Select
                labelId="difficulty-label"
                value={difficulty}
                label="Difficulty"
                onChange={(e) => setDifficulty(e.target.value)}
              >
                <MenuItem value="Easy">Easy</MenuItem>
                <MenuItem value="Medium">Medium</MenuItem>
                <MenuItem value="Hard">Hard</MenuItem>
              </Select>
            </FormControl>
            
            <FormControl fullWidth margin="normal">
              <TextField
                label="Number of Questions"
                type="number"
                value={questionCount}
                onChange={(e) => setQuestionCount(Math.max(1, Math.min(20, parseInt(e.target.value) || 5)))}
                inputProps={{ min: 1, max: 20 }}
              />
            </FormControl>
            
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Question Categories
              </Typography>
              <FormGroup>
                {categories.map((category) => (
                  <FormControlLabel
                    key={category.id}
                    control={
                      <Checkbox 
                        checked={category.checked}
                        onChange={() => handleCategoryChange(category.id)}
                      />
                    }
                    label={category.name}
                  />
                ))}
              </FormGroup>
            </Box>
            
            <Button
              variant="contained"
              fullWidth
              sx={{ mt: 3 }}
              onClick={handleGenerateQuestions}
              disabled={loading || fetchingPositions || selectedPosition === 0}
              startIcon={loading ? <CircularProgress size={24} color="inherit" /> : <RefreshIcon />}
            >
              {loading ? 'Generating...' : 'Generate Questions'}
            </Button>
          </Paper>
        </Grid>
        
        {/* Question Display */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Generated Questions
              </Typography>
              <Box>
                {generatedQuestions.length > 0 && (
                  <>
                    <Tooltip title="Copy to clipboard">
                      <IconButton onClick={handleCopyQuestions}>
                        <FileCopyIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Print questions">
                      <IconButton onClick={handlePrintQuestions}>
                        <PrintIcon />
                      </IconButton>
                    </Tooltip>
                  </>
                )}
              </Box>
            </Box>
            <Divider sx={{ mb: 2 }} />
            
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
                <CircularProgress />
              </Box>
            ) : generatedQuestions.length === 0 ? (
              <Alert severity="info" sx={{ my: 2 }}>
                No questions generated yet. Select a position and click 'Generate Questions' to create interview questions.
              </Alert>
            ) : (
              <Box>
                {generatedQuestions.map((question, index) => (
                  <Accordion key={index} sx={{ mb: 1 }}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography sx={{ fontWeight: 'medium' }}>
                        {index + 1}. {question.content.length > 100 
                          ? `${question.content.substring(0, 100)}...` 
                          : question.content}
                      </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography paragraph>
                        {question.content}
                      </Typography>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2 }}>
                        <Chip 
                          label={question.difficulty || difficulty} 
                          color={
                            question.difficulty === 'Easy' ? 'success' :
                            question.difficulty === 'Hard' ? 'error' : 'primary'
                          }
                          size="small"
                        />
                        <Chip 
                          label={question.category} 
                          variant="outlined"
                          size="small"
                        />
                      </Box>
                    </AccordionDetails>
                  </Accordion>
                ))}
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
      
      {/* Notification */}
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

export default InterviewQuestions; 