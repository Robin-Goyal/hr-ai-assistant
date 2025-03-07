import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  Avatar,
  CircularProgress,
  IconButton,
  Tooltip,
  Divider,
  InputAdornment,
  Menu,
  MenuItem,
  Alert,
  Snackbar,
  Chip,
  Collapse
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import ImageIcon from '@mui/icons-material/Image';
import MicIcon from '@mui/icons-material/Mic';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import DescriptionIcon from '@mui/icons-material/Description';
import FolderIcon from '@mui/icons-material/Folder';
import SaveIcon from '@mui/icons-material/Save';
import DeleteIcon from '@mui/icons-material/Delete';
import InfoIcon from '@mui/icons-material/Info';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import { aiApi } from '../services/api';

interface Message {
  id: number;
  content: string;
  isUser: boolean;
  timestamp: Date;
  attachment?: {
    type: 'image' | 'document' | 'voice';
    url: string;
    name: string;
  };
  usedRAG?: boolean;
}

const ChatAssistant: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      content: "Hello! I'm your HR AI Assistant. How can I help you today?",
      isUser: false,
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);
  const [attachmentMenuAnchor, setAttachmentMenuAnchor] = useState<null | HTMLElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [notification, setNotification] = useState({ open: false, message: '', type: 'info' as 'info' | 'error' | 'success' });
  const [isRecording, setIsRecording] = useState(false);
  const [expandedSources, setExpandedSources] = useState<number[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);
  const [audioRecorder, setAudioRecorder] = useState<MediaRecorder | null>(null);
  const [audioChunks, setAudioChunks] = useState<Blob[]>([]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const toggleSourcesExpanded = (messageId: number) => {
    setExpandedSources(prev => 
      prev.includes(messageId) 
        ? prev.filter(id => id !== messageId)
        : [...prev, messageId]
    );
  };

  // Check if a message contains references to documents (RAG)
  const detectRAGUsage = (content: string): boolean => {
    const ragIndicators = [
      "Relevant information from our knowledge base",
      "Based on our documents",
      "According to our records",
      "From our HR documentation",
      "--- Document",
      "--- "
    ];
    
    return ragIndicators.some(indicator => content.includes(indicator));
  };

  // Extract and format sources from RAG response
  const extractSources = (content: string): string[] => {
    const sources: string[] = [];
    const lines = content.split('\n');
    
    let inSourceSection = false;
    let currentSource = '';
    
    for (const line of lines) {
      if (line.startsWith('--- ') && line.endsWith(' ---')) {
        if (inSourceSection && currentSource) {
          sources.push(currentSource.trim());
          currentSource = '';
        }
        inSourceSection = true;
        const title = line.replace(/^--- /, '').replace(/ ---$/, '');
        currentSource = `**${title}**\n`;
      } else if (inSourceSection) {
        if (line.trim() === '') {
          if (currentSource) {
            sources.push(currentSource.trim());
            currentSource = '';
            inSourceSection = false;
          }
        } else {
          currentSource += line + '\n';
        }
      }
    }
    
    if (inSourceSection && currentSource) {
      sources.push(currentSource.trim());
    }
    
    return sources;
  };

  const handleSend = async () => {
    if (input.trim() === '' && !selectedFile) return;

    // Add user message
    const userMessage: Message = {
      id: messages.length + 1,
      content: input,
      isUser: true,
      timestamp: new Date(),
    };

    // Add attachment if there's a selected file
    if (selectedFile) {
      const fileType = selectedFile.type.startsWith('image/')
        ? 'image'
        : 'document';
      
      userMessage.attachment = {
        type: fileType,
        url: URL.createObjectURL(selectedFile),
        name: selectedFile.name,
      };
    }

    setMessages([...messages, userMessage]);
    setInput('');
    setSelectedFile(null);
    setLoading(true);

    try {
      // Call the AI service
      const response = await aiApi.chat(
        selectedFile 
          ? `[Attachment: ${selectedFile.name}] ${input}` 
          : input, 
        conversationId
      );
      
      // Check if RAG was used in the response
      const usedRAG = detectRAGUsage(response.message);
      
      const aiMessage: Message = {
        id: messages.length + 2,
        content: response.message,
        isUser: false,
        timestamp: new Date(),
        usedRAG
      };
      
      setMessages(prev => [...prev, aiMessage]);
      setConversationId(response.conversation_id);
      
      // If RAG was used, automatically expand sources for this message
      if (usedRAG) {
        setExpandedSources(prev => [...prev, aiMessage.id]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setNotification({
        open: true,
        message: 'Failed to get response from assistant',
        type: 'error'
      });
      
      // Add error message from AI
      const errorMessage: Message = {
        id: messages.length + 2,
        content: "I'm sorry, I encountered an error processing your request. Please try again.",
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleAttachmentClick = (event: React.MouseEvent<HTMLElement>) => {
    setAttachmentMenuAnchor(event.currentTarget);
  };

  const handleAttachmentMenuClose = () => {
    setAttachmentMenuAnchor(null);
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      setSelectedFile(file);
      setNotification({
        open: true,
        message: `File attached: ${file.name}`,
        type: 'info'
      });
    }
    handleAttachmentMenuClose();
  };

  const handleImageSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      if (file.type.startsWith('image/')) {
        setSelectedFile(file);
        setNotification({
          open: true,
          message: `Image attached: ${file.name}`,
          type: 'info'
        });
      } else {
        setNotification({
          open: true,
          message: 'Please select an image file',
          type: 'error'
        });
      }
    }
    handleAttachmentMenuClose();
  };

  const handleVoiceRecording = async () => {
    if (isRecording) {
      // Stop recording
      if (audioRecorder) {
        audioRecorder.stop();
        setIsRecording(false);
        setNotification({
          open: true,
          message: 'Voice recording stopped',
          type: 'info'
        });
      }
    } else {
      try {
        // Request microphone access
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const recorder = new MediaRecorder(stream);
        
        // Set up event handlers
        recorder.ondataavailable = (e) => {
          if (e.data.size > 0) {
            setAudioChunks(prev => [...prev, e.data]);
          }
        };
        
        recorder.onstop = () => {
          // Create audio blob
          const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
          
          // Create a file from the blob
          const audioFile = new File([audioBlob], "voice_message.wav", { 
            type: 'audio/wav',
            lastModified: Date.now()
          });
          
          // Set as selected file
          setSelectedFile(audioFile);
          
          // Reset audio chunks
          setAudioChunks([]);
          
          // Close all tracks
          stream.getTracks().forEach(track => track.stop());
          
          setNotification({
            open: true,
            message: 'Voice recording ready to send',
            type: 'success'
          });
        };
        
        // Start recording
        recorder.start();
        setAudioRecorder(recorder);
        setIsRecording(true);
        setNotification({
          open: true,
          message: 'Voice recording started...',
          type: 'info'
        });
      } catch (err) {
        console.error('Error accessing microphone:', err);
        setNotification({
          open: true,
          message: 'Could not access microphone. Please check permissions.',
          type: 'error'
        });
      }
    }
    
    handleAttachmentMenuClose();
  };

  const handleCloseNotification = () => {
    setNotification(prev => ({ ...prev, open: false }));
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Chat Assistant
      </Typography>
      <Paper
        sx={{
          height: 'calc(100vh - 200px)',
          display: 'flex',
          flexDirection: 'column',
          p: 2,
        }}
      >
        <Box
          sx={{
            flexGrow: 1,
            overflow: 'auto',
            mb: 2,
          }}
        >
          <List>
            {messages.map((message) => (
              <ListItem
                key={message.id}
                sx={{
                  display: 'flex',
                  justifyContent: message.isUser ? 'flex-end' : 'flex-start',
                  mb: 1,
                }}
              >
                <Box
                  sx={{
                    display: 'flex',
                    maxWidth: '70%',
                    flexDirection: message.isUser ? 'row-reverse' : 'row',
                  }}
                >
                  <Avatar
                    sx={{
                      bgcolor: message.isUser ? 'primary.main' : 'secondary.main',
                      mr: message.isUser ? 0 : 1,
                      ml: message.isUser ? 1 : 0,
                    }}
                  >
                    {message.isUser ? <PersonIcon /> : <SmartToyIcon />}
                  </Avatar>
                  <Paper
                    sx={{
                      p: 2,
                      bgcolor: message.isUser ? 'primary.light' : 'grey.100',
                      borderRadius: 2,
                      maxWidth: '100%',
                    }}
                  >
                    <ListItemText
                      primary={message.content}
                      secondary={message.timestamp.toLocaleTimeString()}
                      primaryTypographyProps={{
                        style: { wordBreak: 'break-word' }
                      }}
                    />
                    
                    {/* Display RAG indicator if present */}
                    {message.usedRAG && !message.isUser && (
                      <Box sx={{ mt: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                          <Chip 
                            icon={<InfoIcon fontSize="small" />} 
                            label="AI used knowledge base" 
                            size="small" 
                            color="info" 
                            variant="outlined"
                            onClick={() => toggleSourcesExpanded(message.id)}
                            sx={{ mr: 1 }}
                          />
                          <IconButton 
                            size="small" 
                            onClick={() => toggleSourcesExpanded(message.id)}
                          >
                            {expandedSources.includes(message.id) ? 
                              <ExpandLessIcon fontSize="small" /> : 
                              <ExpandMoreIcon fontSize="small" />
                            }
                          </IconButton>
                        </Box>
                        
                        <Collapse in={expandedSources.includes(message.id)}>
                          <Box sx={{ 
                            mt: 1, 
                            p: 1, 
                            bgcolor: 'background.paper', 
                            borderRadius: 1,
                            border: '1px solid',
                            borderColor: 'divider'
                          }}>
                            <Typography variant="subtitle2" gutterBottom>
                              Sources used:
                            </Typography>
                            {extractSources(message.content).map((source, index) => (
                              <Box key={index} sx={{ mb: 1 }}>
                                <Typography 
                                  variant="body2" 
                                  component="div"
                                  sx={{ 
                                    whiteSpace: 'pre-wrap',
                                    '& b, & strong': { fontWeight: 'bold' }
                                  }}
                                  dangerouslySetInnerHTML={{ 
                                    __html: source
                                      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                      .replace(/\n/g, '<br/>') 
                                  }}
                                />
                              </Box>
                            ))}
                          </Box>
                        </Collapse>
                      </Box>
                    )}
                    
                    {/* Display attachment if present */}
                    {message.attachment && (
                      <Box sx={{ mt: 1 }}>
                        <Divider sx={{ my: 1 }} />
                        {message.attachment.type === 'image' ? (
                          <Box sx={{ mt: 1 }}>
                            <img 
                              src={message.attachment.url} 
                              alt="Attached image" 
                              style={{ maxWidth: '100%', maxHeight: '200px', borderRadius: '4px' }} 
                            />
                            <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
                              {message.attachment.name}
                            </Typography>
                          </Box>
                        ) : (
                          <Box sx={{ 
                            display: 'flex', 
                            alignItems: 'center', 
                            p: 1, 
                            bgcolor: 'background.paper',
                            borderRadius: 1,
                            border: '1px solid',
                            borderColor: 'divider'
                          }}>
                            <DescriptionIcon color="primary" sx={{ mr: 1 }} />
                            <Typography variant="body2" component="div" sx={{ flexGrow: 1, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                              {message.attachment.name}
                            </Typography>
                            <IconButton size="small" onClick={() => window.open(message.attachment?.url, '_blank')}>
                              <FolderIcon fontSize="small" />
                            </IconButton>
                          </Box>
                        )}
                      </Box>
                    )}
                  </Paper>
                </Box>
              </ListItem>
            ))}
            {loading && (
              <ListItem
                sx={{
                  display: 'flex',
                  justifyContent: 'flex-start',
                  mb: 1,
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Avatar sx={{ bgcolor: 'secondary.main', mr: 1 }}>
                    <SmartToyIcon />
                  </Avatar>
                  <CircularProgress size={24} />
                </Box>
              </ListItem>
            )}
            <div ref={messagesEndRef} />
          </List>
        </Box>
        <Box sx={{ display: 'flex', mt: 'auto' }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder={selectedFile ? `Message with attachment: ${selectedFile.name}` : "Type your message..."}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            multiline
            maxRows={4}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Tooltip title="Attach file, image, or voice">
                    <IconButton 
                      edge="start" 
                      onClick={handleAttachmentClick}
                      color={selectedFile || isRecording ? "primary" : "default"}
                    >
                      <AttachFileIcon />
                    </IconButton>
                  </Tooltip>
                  <Menu
                    id="attachment-menu"
                    anchorEl={attachmentMenuAnchor}
                    open={Boolean(attachmentMenuAnchor)}
                    onClose={handleAttachmentMenuClose}
                  >
                    <MenuItem onClick={() => fileInputRef.current?.click()}>
                      <DescriptionIcon sx={{ mr: 1 }} />
                      Attach Document
                    </MenuItem>
                    <MenuItem onClick={() => imageInputRef.current?.click()}>
                      <ImageIcon sx={{ mr: 1 }} />
                      Attach Image
                    </MenuItem>
                    <MenuItem onClick={handleVoiceRecording}>
                      <MicIcon sx={{ mr: 1 }} color={isRecording ? "error" : "inherit"} />
                      {isRecording ? "Stop Recording" : "Voice Message"}
                    </MenuItem>
                  </Menu>
                  <input
                    type="file"
                    ref={fileInputRef}
                    style={{ display: 'none' }}
                    onChange={handleFileSelect}
                    accept=".pdf,.doc,.docx,.txt"
                  />
                  <input
                    type="file"
                    ref={imageInputRef}
                    style={{ display: 'none' }}
                    onChange={handleImageSelect}
                    accept="image/*"
                  />
                </InputAdornment>
              ),
              endAdornment: selectedFile && (
                <InputAdornment position="end">
                  <Tooltip title="Remove attachment">
                    <IconButton edge="end" onClick={() => setSelectedFile(null)}>
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </InputAdornment>
              )
            }}
          />
          <Button
            variant="contained"
            color="primary"
            endIcon={<SendIcon />}
            onClick={handleSend}
            disabled={input.trim() === '' && !selectedFile || loading}
            sx={{ ml: 1 }}
          >
            Send
          </Button>
        </Box>
      </Paper>
      
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

export default ChatAssistant; 