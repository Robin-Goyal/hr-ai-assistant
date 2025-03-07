import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

// Create a custom event for API errors
export const ApiErrorEvent = 'api-error';

// Function to emit API error events
export const emitApiError = (message: string) => {
  const event = new CustomEvent(ApiErrorEvent, { 
    detail: { message } 
  });
  window.dispatchEvent(event);
};

// Create Axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle common errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login if unauthorized
      localStorage.removeItem('token');
      window.location.href = '/login';
    } 
    else if (error.response?.status >= 400 && error.response?.status < 500) {
      // Handle client errors (400-499)
      let errorMessage = 'An error occurred';
      
      // Get the most specific error message available
      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail;
        } else if (Array.isArray(error.response.data.detail) && error.response.data.detail.length > 0) {
          // Handle validation errors
          errorMessage = error.response.data.detail[0]?.msg || errorMessage;
        }
      } else if (error.response?.data?.msg) {
        errorMessage = error.response.data.msg;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      // Emit the error event
      emitApiError(errorMessage);
    }
    
    return Promise.reject(error);
  }
);

// Authentication API
export const authApi = {
  login: async (username: string, password: string) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },
  
  register: async (userData: any) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// User API
export const userApi = {
  getUsers: async () => {
    const response = await api.get('/users');
    return response.data;
  },
  
  getUser: async (id: number) => {
    const response = await api.get(`/users/${id}`);
    return response.data;
  },
  
  createUser: async (userData: any) => {
    const response = await api.post('/users', userData);
    return response.data;
  },
  
  updateUser: async (id: number, userData: any) => {
    const response = await api.put(`/users/${id}`, userData);
    return response.data;
  },
  
  deleteUser: async (id: number) => {
    const response = await api.delete(`/users/${id}`);
    return response.data;
  },
};

// Candidate API
export const candidateApi = {
  getCandidates: async (params?: any) => {
    try {
      const response = await api.get('/candidates', { params });
      // Transform the response to match expected format if needed
      if (Array.isArray(response.data)) {
        // If the response is just an array, transform it to the expected format
        return {
          items: response.data,
          total: response.data.length
        };
      }
      return response.data;
    } catch (error) {
      console.error('Error fetching candidates:', error);
      throw error;
    }
  },
  
  getCandidate: async (id: number) => {
    const response = await api.get(`/candidates/${id}`);
    return response.data;
  },
  
  createCandidate: async (formData: FormData) => {
    const response = await api.post('/candidates', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  updateCandidate: async (id: number, candidateData: any) => {
    const response = await api.put(`/candidates/${id}`, candidateData);
    return response.data;
  },
  
  deleteCandidate: async (id: number) => {
    const response = await api.delete(`/candidates/${id}`);
    return response.data;
  },
  
  updateCandidateStatus: async (id: number, status: string) => {
    const response = await api.put(`/candidates/${id}/status`, { status });
    return response.data;
  },
  
  addSkillsToCandidate: async (id: number, skillNames: string[]) => {
    const response = await api.post(`/candidates/${id}/skills`, { skill_names: skillNames });
    return response.data;
  },
  
  removeSkillFromCandidate: async (candidateId: number, skillId: number) => {
    const response = await api.delete(`/candidates/${candidateId}/skills/${skillId}`);
    return response.data;
  },
  
  getCandidateNotes: async (candidateId: number) => {
    const response = await api.get(`/candidates/${candidateId}/notes`);
    return response.data;
  },
  
  addNoteToCandidate: async (candidateId: number, noteData: any) => {
    const response = await api.post(`/candidates/${candidateId}/notes`, noteData);
    return response.data;
  },
};

// Position API
export const positionApi = {
  getPositions: async (params?: any) => {
    try {
      const response = await api.get('/positions', { params });
      // Transform the response to match expected format if needed
      if (Array.isArray(response.data)) {
        // If the response is just an array, transform it to the expected format
        return {
          items: response.data,
          total: response.data.length
        };
      }
      return response.data;
    } catch (error) {
      console.error('Error fetching positions:', error);
      throw error;
    }
  },
  
  getPosition: async (id: number) => {
    const response = await api.get(`/positions/${id}`);
    return response.data;
  },
  
  createPosition: async (positionData: any) => {
    const response = await api.post('/positions', positionData);
    return response.data;
  },
  
  updatePosition: async (id: number, positionData: any) => {
    const response = await api.put(`/positions/${id}`, positionData);
    return response.data;
  },
  
  deletePosition: async (id: number) => {
    const response = await api.delete(`/positions/${id}`);
    return response.data;
  },
  
  togglePositionStatus: async (id: number) => {
    const response = await api.put(`/positions/${id}/toggle-status`, {});
    return response.data;
  },
};

// Department API
export const departmentApi = {
  getDepartments: async () => {
    const response = await api.get('/departments');
    return response.data;
  },
  
  getDepartment: async (id: number) => {
    const response = await api.get(`/departments/${id}`);
    return response.data;
  },
  
  createDepartment: async (departmentData: any) => {
    const response = await api.post('/departments', departmentData);
    return response.data;
  },
  
  updateDepartment: async (id: number, departmentData: any) => {
    const response = await api.put(`/departments/${id}`, departmentData);
    return response.data;
  },
  
  deleteDepartment: async (id: number) => {
    const response = await api.delete(`/departments/${id}`);
    return response.data;
  },
  
  getDepartmentPositions: async (id: number) => {
    const response = await api.get(`/departments/${id}/positions`);
    return response.data;
  },
};

// Skill API
export const skillApi = {
  getSkills: async (params?: any) => {
    const response = await api.get('/skills', { params });
    return response.data;
  },
  
  getSkill: async (id: number) => {
    const response = await api.get(`/skills/${id}`);
    return response.data;
  },
  
  createSkill: async (skillData: any) => {
    const response = await api.post('/skills', skillData);
    return response.data;
  },
  
  updateSkill: async (id: number, skillData: any) => {
    const response = await api.put(`/skills/${id}`, skillData);
    return response.data;
  },
  
  deleteSkill: async (id: number) => {
    const response = await api.delete(`/skills/${id}`);
    return response.data;
  },
  
  searchSkillsByNames: async (skillNames: string[]) => {
    const response = await api.post('/skills/search', { skill_names: skillNames });
    return response.data;
  },
};

// Application API
export const applicationApi = {
  getApplications: async (params?: any) => {
    const response = await api.get('/applications', { params });
    return response.data;
  },
  
  getApplication: async (id: number) => {
    const response = await api.get(`/applications/${id}`);
    return response.data;
  },
  
  createApplication: async (applicationData: any) => {
    const response = await api.post('/applications', applicationData);
    return response.data;
  },
  
  updateApplication: async (id: number, applicationData: any) => {
    const response = await api.put(`/applications/${id}`, applicationData);
    return response.data;
  },
  
  deleteApplication: async (id: number) => {
    const response = await api.delete(`/applications/${id}`);
    return response.data;
  },
  
  updateApplicationStatus: async (id: number, status: string) => {
    const response = await api.put(`/applications/${id}/status`, { status });
    return response.data;
  },
  
  addInterviewDate: async (id: number, interviewDate: string) => {
    const response = await api.put(`/applications/${id}/interview-date`, { interview_date: interviewDate });
    return response.data;
  },
};

// Note API
export const noteApi = {
  getNotes: async (params?: any) => {
    const response = await api.get('/notes', { params });
    return response.data;
  },
  
  getNote: async (id: number) => {
    const response = await api.get(`/notes/${id}`);
    return response.data;
  },
  
  createNote: async (noteData: any) => {
    const response = await api.post('/notes', noteData);
    return response.data;
  },
  
  updateNote: async (id: number, noteData: any) => {
    const response = await api.put(`/notes/${id}`, noteData);
    return response.data;
  },
  
  deleteNote: async (id: number) => {
    const response = await api.delete(`/notes/${id}`);
    return response.data;
  },
};

// Document API
export const documentApi = {
  getDocuments: async (category?: string) => {
    const params = category ? { category } : {};
    const response = await api.get('/documents', { params });
    return response.data;
  },
  
  getDocument: async (id: number) => {
    const response = await api.get(`/documents/${id}`);
    return response.data;
  },
  
  uploadDocument: async (formData: FormData) => {
    const response = await api.post('/documents', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  deleteDocument: async (id: number) => {
    const response = await api.delete(`/documents/${id}`);
    return response.data;
  },
};

// AI API
export const aiApi = {
  chat: async (message: string, conversationId?: string) => {
    const response = await api.post('/ai/chat', {
      message,
      conversation_id: conversationId,
    });
    return response.data;
  },
  
  generateQuestions: async (positionId: number, difficulty: string, count: number, categories: string[]) => {
    const response = await api.post('/ai/questions', {
      position_id: positionId,
      difficulty,
      count,
      categories,
    });
    return response.data;
  },
  
  analyzeResume: async (candidateId: number) => {
    const response = await api.post('/ai/resume-analysis', {
      candidate_id: candidateId,
    });
    return response.data;
  },
};

export default api; 