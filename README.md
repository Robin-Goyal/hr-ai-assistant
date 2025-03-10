# HR AI Assistant

## Project Overview
The HR AI Assistant is a comprehensive web application designed to streamline and enhance various HR processes using artificial intelligence. The application integrates document management, candidate evaluation, interview question generation, resume analysis, and an AI-powered chat interface to assist HR professionals in their daily tasks.

## Key Features

### 1. Document Management System with RAG Architecture
- **Intelligent Document Processing**: Upload, categorize, and analyze HR-related documents using advanced NLP techniques
- **Vector Search Capabilities**: Semantic search across all documents using Pinecone vector database
- **Automatic Text Chunking**: Sophisticated text chunking with configurable overlap for optimal context retrieval
- **Document Sectioning**: AI-driven document sectioning that preserves semantic meaning for better retrieval
- **Relevance Scoring**: Advanced relevance calculation algorithms to present the most pertinent information
- **Source Attribution**: All AI responses include source attribution to maintain accountability and transparency

### 2. AI-Powered Chat Assistant
- **Retrieval-Augmented Generation (RAG)**: Combines the power of LLMs with document retrieval for accurate, context-aware responses
- **Conversation Memory**: Maintains context throughout multi-turn conversations
- **Context Management**: Intelligently handles context length limitations by prioritizing the most relevant information
- **Fallback Mechanisms**: Gracefully handles situations where context exceeds token limits
- **Source Indicators**: Visual indicators for when responses are derived from knowledge base vs. model knowledge

### 3. Advanced Resume Analysis
- **Comprehensive Parsing**: Extract education, experience, skills, and other key information from resumes
- **Section Detection**: Automatically identifies resume sections regardless of formatting style
- **Large Resume Handling**: Special processing for large resumes that exceed token limits
- **Position Matching**: Calculates match scores between candidate skills and position requirements
- **Experience Quantification**: Automatically estimates years of experience based on resume content
- **Skill Categorization**: Organizes extracted skills into relevant categories

### 4. AI-Driven Interview Question Generation
- **Position-Specific Questions**: Generates tailored questions based on job descriptions and requirements
- **Difficulty Control**: Adjustable question difficulty levels (Easy, Medium, Hard)
- **Category Selection**: Generate questions by category (Technical, Behavioral, Problem-solving, etc.)
- **Quantity Control**: Specify the exact number of questions needed
- **Contextual Awareness**: Questions can be generated with awareness of candidate qualifications

### 5. Candidate Management
- **Comprehensive Profiles**: Store and manage candidate information including contact details, experience, and skills
- **Resume Integration**: Automatically populate profiles with information extracted from resumes
- **Skill Tracking**: Track and update candidate skills throughout the hiring process
- **Status Management**: Monitor candidate progress through customizable workflow stages
- **Position Association**: Link candidates with open positions for streamlined management

### 6. Position Management
- **Structured Job Definitions**: Create detailed position descriptions with requirements and responsibilities
- **Department Organization**: Organize positions by department with clear hierarchies
- **Skill Requirements**: Define and prioritize required skills for better candidate matching
- **Salary Range Management**: Track and manage salary expectations for budget planning
- **Location Flexibility**: Support for various work arrangements including remote and hybrid options

### 7. Integrated HR Dashboard
- **Hiring Pipeline Visualization**: See the current status of all hiring processes at a glance
- **Candidate Statistics**: Track key metrics related to recruitment efforts
- **Department Analytics**: Monitor hiring needs and progress by department
- **Position Insights**: Gain insights into position-specific recruitment challenges
- **Activity Timeline**: Chronological view of recent HR activities

## Technical Architecture

### Backend Framework
- **FastAPI**: High-performance Python API framework with automatic OpenAPI documentation
- **SQLAlchemy ORM**: Object-Relational Mapping for efficient database interactions
- **Pydantic Models**: Robust data validation and serialization
- **Async Processing**: Asynchronous handling for file uploads and AI processing

### AI Implementation
- **OpenAI Integration**: Leverages OpenAI's GPT models for natural language understanding and generation
- **Sentence Transformers**: Uses all-mpnet-base-v2 for high-quality text embeddings
- **Pinecone Vector Database**: Stores and retrieves document embeddings for semantic search
- **Custom NLP Processing**: Specialized text processing pipelines for different document types
- **Context Management**: Sophisticated algorithms for handling context limitations and relevance

### Frontend Technology
- **React**: Component-based UI development with React hooks
- **TypeScript**: Type-safe code for reduced errors and better developer experience
- **Material UI**: Modern, responsive component library for consistent design
- **Context API**: State management for application-wide data access
- **Axios**: Promise-based HTTP client for API communication

### Security Features
- **JWT Authentication**: Secure token-based authentication system
- **Role-Based Access Control**: Different permission levels for various user types
- **Password Hashing**: Secure password storage with bcrypt
- **Protected Routes**: Front-end route protection based on authentication status
- **Error Handling**: Comprehensive error handling and reporting

## Deployment Architecture
- **Docker Support**: Containerized deployment for consistency across environments
- **Environment Configuration**: Centralized environment variable management
- **Development Mode**: Hot-reloading and debugging features for development
- **Production Optimization**: Build optimizations for production deployment

## RAG System Architecture

### Document Processing Pipeline

1. **Document Ingestion**
   - File upload handling with support for multiple formats (PDF, DOCX, TXT, DOC)
   - Text extraction with fallback mechanisms for different document types
   - Semantic chunking with configurable size and overlap
   - Embedding generation using Sentence Transformers
   - Vector storage in Pinecone with metadata preservation

2. **Query Processing**
   - User query embedding with the same model used for documents
   - Semantic similarity search with configurable top-k retrieval
   - Smart section extraction from relevant documents
   - Context prioritization based on relevance scoring
   - Token management to handle context length limitations

3. **Response Generation**
   - Context integration with the user query
   - LLM-based response generation with OpenAI's models
   - Source tracking for attribution
   - Fallback mechanisms for token limit exceptions
   - Response quality checks

### Vector Store Configuration

```python
RAG Engine Settings:
- Embedding Model: 'all-mpnet-base-v2'
- Vector Dimension: 768
- Similarity Metric: cosine
- Index Name: "hr-assistant"
- Chunking Strategy: Semantic sections with 1000 token size and 200 token overlap
```

## Installation and Setup

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn
- SQLite (included)
- OpenAI API Key
- Pinecone API Key

### Backend Setup
1. Clone the repository
2. Navigate to the backend directory
3. Create a virtual environment: `python -m venv venv`
4. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Copy `.env.example` to `.env` and fill in your API keys
7. Run migrations: `alembic upgrade head`
8. Start the server: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

### Frontend Setup
1. Navigate to the frontend directory
2. Install dependencies: `npm install` or `yarn`
3. Copy `.env.example` to `.env` and configure the backend URL
4. Start the development server: `npm start` or `yarn start`

### Running with the Script
For convenience, you can use the provided script to start both servers:
```bash
chmod +x run.sh
./run.sh
```

## Acknowledgments

- OpenAI for GPT models
- Pinecone for vector database technology
- FastAPI team for the excellent API framework
- HuggingFace for transformer models and sentence-transformers
- All other open-source libraries used in this project 
