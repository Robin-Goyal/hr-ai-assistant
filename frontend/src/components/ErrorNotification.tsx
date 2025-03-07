import React, { useState, useEffect } from 'react';
import { Snackbar, Alert } from '@mui/material';
import { ApiErrorEvent } from '../services/api';

const ErrorNotification: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const handleApiError = (event: CustomEvent<{ message: string }>) => {
      setMessage(event.detail.message);
      setOpen(true);
    };

    // Add event listener for API errors
    window.addEventListener(
      ApiErrorEvent, 
      handleApiError as EventListener
    );

    // Cleanup
    return () => {
      window.removeEventListener(
        ApiErrorEvent, 
        handleApiError as EventListener
      );
    };
  }, []);

  const handleClose = (event?: React.SyntheticEvent | Event, reason?: string) => {
    if (reason === 'clickaway') {
      return;
    }
    setOpen(false);
  };

  return (
    <Snackbar
      open={open}
      autoHideDuration={6000}
      onClose={handleClose}
      anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
    >
      <Alert
        onClose={handleClose}
        severity="error"
        variant="filled"
        sx={{ width: '100%' }}
      >
        {message}
      </Alert>
    </Snackbar>
  );
};

export default ErrorNotification; 