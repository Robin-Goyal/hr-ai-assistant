import os
import uuid
from typing import List, Dict, Any, Optional
import traceback

# Conditionally import Pinecone
try:
    from pinecone import Pinecone
    pinecone_available = True
except ImportError:
    pinecone_available = False
    print("Pinecone not available")

# Conditionally import SentenceTransformer
try:
    from sentence_transformers import SentenceTransformer
    sentence_transformers_available = True
except ImportError:
    sentence_transformers_available = False
    print("SentenceTransformer not available")

# Conditionally import OpenAI
try:
    from openai import OpenAI
    openai_available = True
except ImportError:
    openai_available = False
    print("OpenAI not available")

from ..core.config import (
    OPENAI_API_KEY, 
    PINECONE_API_KEY, 
    PINECONE_ENVIRONMENT,
    INDEX_NAME,
    EMBEDDING_MODEL
)

# Print the API keys for debugging (remove in production)
print(f"OpenAI API Key: {OPENAI_API_KEY[:5]}...{OPENAI_API_KEY[-5:] if len(OPENAI_API_KEY) > 10 else 'Not Set'}")
print(f"Pinecone API Key: {PINECONE_API_KEY[:5]}...{PINECONE_API_KEY[-5:] if len(PINECONE_API_KEY) > 10 else 'Not Set'}")
print(f"Pinecone Environment: {PINECONE_ENVIRONMENT or 'Not Set'}")
print(f"Index Name: {INDEX_NAME or 'Not Set'}")
print(f"Embedding Model: {EMBEDDING_MODEL or 'Not Set'}")

# Initialize clients
openai_client = None
if openai_available and OPENAI_API_KEY:
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        print("OpenAI client initialized successfully")
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
else:
    print("OpenAI client initialization skipped: API key not set or OpenAI not available")

# Initialize the embedding model
model = None
if sentence_transformers_available:
    try:
        model = SentenceTransformer(EMBEDDING_MODEL)
        print(f"Sentence transformer model '{EMBEDDING_MODEL}' loaded successfully")
    except Exception as e:
        print(f"Error loading embedding model: {e}")

# Initialize Pinecone
index = None
pc = None
if pinecone_available and PINECONE_API_KEY and PINECONE_ENVIRONMENT:
    try:
        # Initialize Pinecone with the current API
        pc = Pinecone(api_key=PINECONE_API_KEY)
        print("Pinecone initialized successfully")
        
        try:
            # List available indexes
            available_indexes = [idx.name for idx in pc.list_indexes()]
            print(f"Available Pinecone indexes: {available_indexes}")
            
            # Check if index exists, if not create it
            if INDEX_NAME not in available_indexes:
                print(f"Creating new Pinecone index: {INDEX_NAME}")
                pc.create_index(
                    name=INDEX_NAME,
                    dimension=768,  # dimension of the all-mpnet-base-v2 embeddings
                    metric="cosine"
                )
            
            # Connect to the index
            index = pc.Index(INDEX_NAME)
            print(f"Successfully connected to Pinecone index: {INDEX_NAME}")
        except Exception as inner_e:
            print(f"Error working with Pinecone indexes: {inner_e}")
            # Fallback gracefully if index operations fail
            print("Using a fallback approach without vector storage")
    except Exception as e:
        print(f"Error initializing Pinecone: {e}")
else:
    if not pinecone_available:
        print("Pinecone not available (module not installed)")
    else:
        print("Pinecone initialization skipped: API key or environment not set")

def get_embedding(text: str) -> List[float]:
    """Get embedding for text using the sentence transformer model."""
    if model is None:
        print("Embedding model not initialized, returning empty embedding")
        return [0.0] * 768  # Return a dummy embedding
    
    try:
        return model.encode(text).tolist()
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return [0.0] * 768  # Return a dummy embedding on error

def add_document_to_vector_store(document_id: int, text: str, metadata: Dict[str, Any]) -> str:
    """Add a document to the vector store."""
    if index is None:
        print("Pinecone index not available, skipping vector store operation")
        return f"doc_{document_id}_not_stored"
    
    try:
        # Get embedding
        embedding = get_embedding(text)
        
        # Create a unique ID for the vector
        vector_id = f"doc_{document_id}_{uuid.uuid4().hex[:8]}"
        
        # Insert into Pinecone using the current API format
        index.upsert(
            vectors=[
                {
                    "id": vector_id,
                    "values": embedding,
                    "metadata": metadata
                }
            ]
        )
        
        return vector_id
    except Exception as e:
        print(f"Error adding document to vector store: {e}")
        return f"doc_{document_id}_error"

def search_similar_documents(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Search for similar documents using the query."""
    # Skip if Pinecone is not available
    if index is None:
        print("Pinecone index not available, returning empty results")
        return []
    
    try:
        # Get embedding for query
        query_embedding = get_embedding(query)
        
        # Search Pinecone with the current API
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )

        print(f"Pinecone query results type: {type(results)}")
        
        # Handle the response format for the current API
        matches = []
        
        if hasattr(results, 'matches'):
            matches = results.matches
            print(f"Found {len(matches)} matches from results.matches")
            
            # Log metadata details for debugging
            for i, match in enumerate(matches):
                match_id = match.id if hasattr(match, 'id') else "unknown"
                match_score = match.score if hasattr(match, 'score') else 0
                metadata_keys = list(match.metadata.keys()) if hasattr(match, 'metadata') and match.metadata else []
                print(f"Match {i}: ID={match_id}, Score={match_score}, Metadata keys: {metadata_keys}")
                
                # Check if text is present in metadata
                if hasattr(match, 'metadata') and match.metadata and 'text' in match.metadata:
                    text_len = len(match.metadata['text'])
                    text_preview = match.metadata['text'][:50] + "..." if text_len > 50 else match.metadata['text']
                    print(f"  Text present, length: {text_len}, preview: {text_preview}")
                else:
                    print(f"  No text in metadata")
                    
        elif isinstance(results, dict) and 'matches' in results:
            matches = results['matches']
            print(f"Found {len(matches)} matches from results['matches']")
            
            # Log metadata details for debugging
            for i, match in enumerate(matches):
                match_id = match.get('id', "unknown")
                match_score = match.get('score', 0)
                metadata_keys = list(match.get('metadata', {}).keys())
                print(f"Match {i}: ID={match_id}, Score={match_score}, Metadata keys: {metadata_keys}")
                
                # Check if text is present in metadata
                if 'metadata' in match and 'text' in match['metadata']:
                    text_len = len(match['metadata']['text'])
                    text_preview = match['metadata']['text'][:50] + "..." if text_len > 50 else match['metadata']['text']
                    print(f"  Text present, length: {text_len}, preview: {text_preview}")
                else:
                    print(f"  No text in metadata")
            
        else:
            print(f"Unexpected Pinecone response format: {type(results)}, returning empty results")
            return []
        
        # Ensure each match has metadata with text
        for i, match in enumerate(matches):
            # Get match ID and score
            if hasattr(match, 'id'):
                match_id = match.id
                match_score = match.score
                if hasattr(match, 'metadata'):
                    metadata = match.metadata
                    if metadata and 'text' not in metadata:
                        # Add empty text if missing
                        metadata['text'] = ""
                        print(f"Added missing text field to match {i} metadata")
            elif isinstance(match, dict):
                match_id = match.get('id', f'unknown_{i}')
                match_score = match.get('score', 0)
                if 'metadata' in match:
                    metadata = match['metadata']
                    if metadata and 'text' not in metadata:
                        # Add empty text if missing
                        metadata['text'] = ""
                        print(f"Added missing text field to match {i} metadata")
            
        return matches
    except Exception as e:
        print(f"Error searching documents: {e}")
        traceback.print_exc()
        return []

def generate_ai_response(prompt: str, context: Optional[str] = None) -> str:
    """Generate a response using OpenAI with optional context."""
    if not openai_available or openai_client is None:
        return "AI service is not available at the moment. Please try again later."
    
    if not OPENAI_API_KEY:
        return "OpenAI API key not configured. Please contact the administrator."
    
    # Prepare the full prompt with context if provided
    full_prompt = prompt
    if context:
        # Create a more efficient prompt that focuses on the query
        full_prompt = f"""
I need information to answer a question. Here is relevant information from our database:

{context}

Based on the information above, please answer this question:
{prompt}

If the answer isn't contained in the provided information, please say so and provide general knowledge about the topic.
"""
    
    try:
        # Generate response
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an HR assistant with expertise in HR processes, recruitment, and employee management."},
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        error_message = str(e)
        print(f"Error generating AI response: {error_message}")
        
        # Handle token limit errors
        if "maximum context length" in error_message:
            try:
                # Try again with a more concise prompt and fewer tokens from the context
                truncated_context = context[:len(context)//2] + "...[additional information omitted]..." if context else ""
                
                concise_prompt = f"""
I need to answer this question: {prompt}

Here is some partial information (truncated due to length):
{truncated_context}

Please answer the question based on the available information. If the information seems incomplete, please mention that.
"""
                
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an HR assistant. Provide concise answers based on the given information."},
                        {"role": "user", "content": concise_prompt}
                    ],
                    max_tokens=300,
                    temperature=0.5
                )
                
                return response.choices[0].message.content + "\n\n[Note: The response was generated with truncated context due to length limitations.]"
            except Exception as retry_error:
                print(f"Error in retry with truncated context: {retry_error}")
                return "I'm sorry, but I couldn't process your request due to the large amount of context information. Could you please ask a more specific question or break it down into smaller parts?"
        
        return f"Sorry, I encountered an error: {error_message}"

def generate_interview_questions(position_description: str, difficulty: str, count: int, categories: List[str]) -> List[str]:
    """Generate interview questions based on position description."""
    if not openai_available or openai_client is None:
        return ["AI service is not available at the moment. Please try again later."]
    
    if not OPENAI_API_KEY:
        return ["OpenAI API key not configured. Please contact the administrator."]
    
    # Prepare the prompt for question generation
    categories_str = ", ".join(categories) if categories else "general"
    prompt = f"""
    Generate {count} {difficulty} difficulty interview questions for the following position:
    
    Position Description: {position_description}
    
    Categories: {categories_str}
    
    Output only the questions without numbering or additional text.
    """
    
    try:
        # Generate questions
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert HR professional who specializes in creating interview questions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        # Parse questions from the response
        questions_text = response.choices[0].message.content.strip()
        questions = [q.strip() for q in questions_text.split("\n") if q.strip()]
        
        return questions[:count]  # Ensure we return the requested number of questions
    except Exception as e:
        print(f"Error generating interview questions: {e}")
        return [f"Sorry, I encountered an error: {str(e)}"]

def analyze_resume(resume_text: str, position_description: Optional[str] = None) -> Dict[str, Any]:
    """Analyze a resume and extract key information."""
    if not openai_available or openai_client is None:
        return {
            "skills": ["AI service unavailable"],
            "experience_years": 0,
            "education": "AI service unavailable",
            "summary": "AI service is not available at the moment. Please try again later."
        }
    
    if not OPENAI_API_KEY:
        return {
            "skills": ["API key missing"],
            "experience_years": 0,
            "education": "API key missing",
            "summary": "OpenAI API key not configured. Please contact the administrator."
        }
    
    # Handle large resumes by chunking
    # Estimate token count (rough approximation: 1 token ≈ 4 characters for English text)
    estimated_tokens = len(resume_text) // 4
    
    # If resume is too large, chunk it and extract key information from each chunk
    if estimated_tokens > 12000:  # Leave room for system message and instructions
        print(f"Resume is large (est. {estimated_tokens} tokens), chunking...")
        return analyze_large_resume(resume_text, position_description)
    
    # For smaller resumes, proceed with normal analysis
    # Prepare the prompt for resume analysis
    prompt = f"""
    Analyze the following resume and extract:
    1. Key skills
    2. Years of experience
    3. Education
    4. A brief summary of qualifications
    
    Resume:
    {resume_text}
    
    Format your response as JSON with the following keys:
    "skills" (array), "experience_years" (number), "education" (string), "summary" (string)
    """
    
    # If position description is provided, add skill matching
    if position_description:
        prompt += f"""
        
        Also compare the candidate's skills with the following position requirements and provide a match score from 0 to 100:
        
        Position Requirements:
        {position_description}
        
        Add a "match_score" key to your JSON response.
        """
    
    try:
        # Generate analysis
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert HR professional who specializes in resume analysis."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.3
        )
        
        # Extract JSON-formatted response
        analysis_text = response.choices[0].message.content.strip()
        
        # Parse JSON (in a real application, you'd use proper error handling)
        try:
            import json
            analysis = json.loads(analysis_text)
            
            # Ensure all required fields are present
            required_fields = ["skills", "experience_years", "education", "summary"]
            for field in required_fields:
                if field not in analysis:
                    analysis[field] = [] if field == "skills" else "" if field in ["education", "summary"] else 0
                    
            # Ensure skills is a list
            if not isinstance(analysis["skills"], list):
                analysis["skills"] = [analysis["skills"]] if analysis["skills"] else []
                
            # Ensure experience_years is a number
            if not isinstance(analysis["experience_years"], (int, float)):
                try:
                    analysis["experience_years"] = float(analysis["experience_years"])
                except:
                    analysis["experience_years"] = 0
                    
            # If position was provided, ensure match_score is present
            if position_description and "match_score" not in analysis:
                analysis["match_score"] = 0
                
            return analysis
                
        except:
            # Fallback to providing a structured response if JSON parsing fails
            analysis = {
                "skills": ["parsing error"],
                "experience_years": 0,
                "education": "Could not parse education",
                "summary": "Error parsing resume analysis result"
            }
            if position_description:
                analysis["match_score"] = 0
        
        return analysis
    except Exception as e:
        print(f"Error analyzing resume: {e}")
        return {
            "skills": ["error"],
            "experience_years": 0,
            "education": "Error occurred",
            "summary": f"Error analyzing resume: {str(e)}"
        }

def analyze_large_resume(resume_text: str, position_description: Optional[str] = None) -> Dict[str, Any]:
    """Handle large resumes by chunking and analyzing in parts."""
    print("Using analyze_large_resume function")
    
    # Split resume into sections or meaningful chunks
    sections = split_resume_into_sections(resume_text)
    
    # Debug the sections found
    print(f"Resume split into {len(sections)} sections:")
    for section_name, content in sections.items():
        print(f"- Section '{section_name}': {len(content)} characters")
    
    # Initialize combined results
    all_skills = []
    max_experience = 0
    education_parts = []
    summary_parts = []
    match_score = 0
    
    # First, try to analyze the whole resume as a condensed version
    condensed_resume = ""
    
    # Create a condensed version focusing on important sections
    for section_name, section_text in sections.items():
        # Include full content of important sections
        if any(key in section_name.lower() for key in ['skill', 'experience', 'education', 'summary', 'profile']):
            condensed_resume += f"\n\n{section_name}:\n{section_text}"
        # For other sections, include just the title and first couple of lines
        else:
            lines = section_text.split('\n')
            preview = '\n'.join(lines[:3]) + ("..." if len(lines) > 3 else "")
            condensed_resume += f"\n\n{section_name}:\n{preview}"
    
    # Try to analyze the condensed resume first
    try:
        print("Attempting to analyze condensed resume")
        prompt = f"""
        Analyze the following condensed resume and extract:
        1. Key skills (as a list)
        2. Years of experience (as a number)
        3. Education details
        4. A brief professional summary
        
        Resume:
        {condensed_resume}
        
        Format your response as clean JSON without comments with these keys:
        "skills" (array of strings), 
        "experience_years" (number), 
        "education" (string), 
        "summary" (string)
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert HR professional who specializes in resume analysis. Output valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.3
        )
        
        analysis_text = response.choices[0].message.content.strip()
        
        # Try to parse the JSON response
        try:
            import json
            analysis = json.loads(analysis_text)
            print("Successfully parsed condensed resume analysis")
            
            # Basic validation of the response
            if "skills" in analysis and isinstance(analysis["skills"], list) and \
               "experience_years" in analysis and \
               "education" in analysis and \
               "summary" in analysis:
                
                # If position description is provided, add match score
                if position_description:
                    analysis["match_score"] = calculate_match_score(analysis["skills"], position_description)
                
                # Return the successful analysis
                return analysis
                
        except json.JSONDecodeError as e:
            print(f"Error parsing condensed resume analysis JSON: {e}")
            # Continue with section-by-section analysis
    except Exception as e:
        print(f"Error analyzing condensed resume: {e}")
        # Continue with section-by-section analysis
    
    # If condensed analysis failed, try section by section
    print("Proceeding with section-by-section analysis")
    
    # Process each section separately
    for section_name, section_text in sections.items():
        # Skip empty sections
        if not section_text.strip():
            continue
            
        print(f"Analyzing section: {section_name}")
            
        # Prepare prompt for this section
        prompt = ""
        
        # Customize prompt based on section type
        if 'skill' in section_name.lower():
            prompt = f"""
            Extract skills from this resume section:
            {section_text}
            
            Format your response as clean JSON with one key:
            "skills": [list of skills]
            """
        elif 'experience' in section_name.lower() or 'work' in section_name.lower() or 'employment' in section_name.lower():
            prompt = f"""
            Analyze this work experience section:
            {section_text}
            
            Format your response as clean JSON with these keys:
            "experience_years": (estimated total years of experience as a number)
            "summary": (brief summary of the experience)
            """
        elif 'education' in section_name.lower():
            prompt = f"""
            Extract education details from this section:
            {section_text}
            
            Format your response as clean JSON with one key:
            "education": (education details as text)
            """
        elif 'summary' in section_name.lower() or 'profile' in section_name.lower() or 'objective' in section_name.lower() or section_name == 'Header':
            prompt = f"""
            Create a professional summary from this section:
            {section_text}
            
            Format your response as clean JSON with one key:
            "summary": (professional summary as text)
            """
        else:
            # Generic analysis for other sections
            prompt = f"""
            Analyze this resume section and extract any relevant information:
            {section_text}
            
            Format your response as clean JSON with these keys:
            "skills": [any skills mentioned],
            "experience_years": (any years mentioned or 0),
            "education": (any education details or empty string),
            "summary": (brief summary of this section)
            """
        
        try:
            # Generate analysis for this section
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert HR professional who extracts resume information. Output valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.3
            )
            
            # Extract JSON-formatted response
            section_analysis_text = response.choices[0].message.content.strip()
            
            # Parse JSON
            import json
            try:
                # Remove markdown code formatting if present
                if section_analysis_text.startswith('```json'):
                    section_analysis_text = section_analysis_text.replace('```json', '', 1)
                if section_analysis_text.endswith('```'):
                    section_analysis_text = section_analysis_text[:-3]
                
                section_analysis_text = section_analysis_text.strip()
                
                section_analysis = json.loads(section_analysis_text)
                print(f"Successfully parsed analysis for section {section_name}")
                
                # Combine results
                if "skills" in section_analysis and isinstance(section_analysis["skills"], list):
                    all_skills.extend(section_analysis["skills"])
                
                if "experience_years" in section_analysis:
                    try:
                        exp_years = float(section_analysis["experience_years"])
                        max_experience = max(max_experience, exp_years)
                    except (ValueError, TypeError):
                        pass
                
                if "education" in section_analysis and section_analysis["education"]:
                    education_parts.append(section_analysis["education"])
                
                if "summary" in section_analysis and section_analysis["summary"]:
                    summary_parts.append(section_analysis["summary"])
                    
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON from section {section_name}: {e} - Text: {section_analysis_text[:100]}")
                
        except Exception as e:
            print(f"Error analyzing section {section_name}: {e}")
    
    # If position description is provided, do a separate analysis for skill matching
    if position_description:
        match_score = calculate_match_score(all_skills, position_description)
    
    # Combine all results
    # Remove duplicates from skills
    unique_skills = []
    for skill in all_skills:
        if skill and skill.lower() not in [s.lower() for s in unique_skills]:
            unique_skills.append(skill)
    
    # Combine education parts
    education = "\n".join(education_parts) if education_parts else "No education information found"
    
    # Create a summary from the parts
    if summary_parts:
        combined_summary = " ".join(summary_parts)
        # If combined summary is too long, summarize it further
        if len(combined_summary) > 500:
            try:
                summary_prompt = f"""
                Summarize this resume information in a concise paragraph:
                {combined_summary[:2000]}
                """
                
                summary_response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You create concise professional summaries."},
                        {"role": "user", "content": summary_prompt}
                    ],
                    max_tokens=150,
                    temperature=0.3
                )
                
                final_summary = summary_response.choices[0].message.content.strip()
            except Exception as e:
                print(f"Error creating final summary: {e}")
                final_summary = combined_summary[:500] + "..."
        else:
            final_summary = combined_summary
    else:
        final_summary = "No summary information available"
    
    # Prepare final result
    result = {
        "skills": unique_skills,
        "experience_years": max_experience,
        "education": education,
        "summary": final_summary
    }
    
    if position_description:
        result["match_score"] = match_score
    
    return result

def calculate_match_score(skills: List[str], position_description: str) -> int:
    """Calculate a match score between candidate skills and position description."""
    try:
        # Simplified matching logic - we're measuring how many skills appear in the description
        skill_count = len(skills)
        if skill_count == 0:
            return 0
            
        match_count = 0
        position_desc_lower = position_description.lower()
        
        for skill in skills:
            if skill.lower() in position_desc_lower:
                match_count += 1
        
        # Calculate percentage match
        match_percentage = int((match_count / skill_count) * 100)
        
        # Ensure the score is between 0 and 100
        return max(0, min(100, match_percentage))
        
    except Exception as e:
        print(f"Error calculating match score: {e}")
        return 50  # Default middle score

def split_resume_into_sections(resume_text: str) -> Dict[str, str]:
    """Split a resume into common sections."""
    # Common resume section headers
    section_headers = [
        "Summary", "Profile", "Objective", "Experience", "Work Experience", 
        "Employment History", "Skills", "Technical Skills", "Education",
        "Certifications", "Projects", "Publications", "Languages",
        "Interests", "References", "Personal Information"
    ]
    
    # Add variations of headers
    variations = []
    for header in section_headers:
        variations.append(header.upper())
        variations.append(header.lower())
        variations.append(header + ":")
        variations.append(header.upper() + ":")
        variations.append(header.lower() + ":")
    
    section_headers.extend(variations)
    
    # Try to identify sections based on common headers
    sections = {}
    current_section = "Header"  # Default section for the beginning
    current_content = []
    
    # Safety check
    if not resume_text or not isinstance(resume_text, str):
        print("Warning: Invalid resume text provided")
        return {"Content": str(resume_text) if resume_text else ""}
    
    # Clean the text
    resume_text = resume_text.replace('\r', '\n')
    
    # Split by lines to process
    lines = resume_text.split('\n')
    
    for line in lines:
        # Skip empty lines
        if not line.strip():
            current_content.append(line)
            continue
            
        # Check if this line could be a section header
        is_header = False
        line_clean = line.strip()
        
        # If line is short, all caps, or ends with colon, it might be a header
        is_possible_header = (len(line_clean) < 30 and 
                             (line_clean.isupper() or 
                              line_clean.endswith(':') or
                              any(line_clean.lower() == header.lower() for header in section_headers)))
        
        if is_possible_header:
            for header in section_headers:
                header_clean = header.lower().replace(':', '')
                if header_clean in line_clean.lower():
                    # Save previous section
                    if current_content:
                        sections[current_section] = '\n'.join(current_content)
                    
                    # Start new section
                    normalized_header = header.split(':')[0].strip()  # Remove colon if present
                    current_section = normalized_header
                    current_content = []
                    is_header = True
                    break
        
        if not is_header:
            current_content.append(line)
    
    # Save the last section
    if current_content:
        sections[current_section] = '\n'.join(current_content)
    
    # If no sections were identified or just one section, try alternative approaches
    if len(sections) <= 1:
        print("Few or no sections identified, trying alternative parsing approach")
        
        # Try a different approach - split by double newlines
        parts = resume_text.split('\n\n')
        if len(parts) > 1:
            # Reset sections
            sections = {}
            
            # Try to identify headers in these parts
            for i, part in enumerate(parts):
                if not part.strip():
                    continue
                    
                lines = part.split('\n')
                first_line = lines[0].strip()
                
                # Check if the first line looks like a header
                if len(first_line) < 30 and (first_line.isupper() or first_line.endswith(':')):
                    section_name = first_line.replace(':', '').strip()
                    section_content = '\n'.join(lines[1:])
                    sections[section_name] = section_content
                else:
                    sections[f"Section_{i+1}"] = part
        else:
            # If still no good sections, just use the whole text
            sections = {"Content": resume_text}
    
    # Final check - if Header section is empty or just has name, merge it with the next section
    if "Header" in sections and len(sections["Header"].strip().split('\n')) <= 2:
        header_content = sections["Header"]
        del sections["Header"]
        
        # Find the next section to merge with
        if "Summary" in sections:
            sections["Summary"] = header_content + "\n\n" + sections["Summary"]
        elif "Profile" in sections:
            sections["Profile"] = header_content + "\n\n" + sections["Profile"]
        elif "Objective" in sections:
            sections["Objective"] = header_content + "\n\n" + sections["Objective"]
        else:
            # Just add it back if no suitable section to merge with
            sections["Header"] = header_content
    
    return sections 