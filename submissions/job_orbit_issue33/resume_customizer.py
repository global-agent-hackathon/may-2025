import os
import json
import fitz  # PyMuPDF
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.models.aws import AwsBedrock
import time

import boto3
from botocore.config import Config

config = Config(connect_timeout=5,
                read_timeout=5 * 60,
                retries={'max_attempts': 2})
bedrock_client = boto3.client(
    'bedrock-runtime',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name='us-east-1',
    config=config)

import re
import subprocess
import os
import tempfile
from typing import Dict, List, Tuple

import re
import subprocess
import os
import tempfile
import shutil
from pathlib import Path


def create_agent_safe_latex_resume(text: str, output_path: str) -> bool:
    """Create LaTeX resume that works reliably in agent environments."""

    def find_pdflatex():
        """Find pdflatex executable in various locations."""
        possible_paths = [
            'pdflatex',  # In PATH
            '/usr/bin/pdflatex',  # Linux
            '/usr/local/bin/pdflatex',  # Linux/macOS
            '/Library/TeX/texbin/pdflatex',  # macOS MacTeX
            '/usr/local/texlive/2023/bin/x86_64-linux/pdflatex',  # TeXLive
            '/usr/local/texlive/2024/bin/x86_64-linux/pdflatex',  # TeXLive
        ]

        for path in possible_paths:
            if shutil.which(path):
                return path

        return None

    def clean_text_robust(text):
        """Ultra-robust text cleaning for LaTeX."""
        if not text:
            return ""

        # Handle special characters very carefully
        text = str(text)  # Ensure it's a string

        # Order matters - backslash first!
        replacements = [
            ('\\', '\\textbackslash{}'),
            ('{', '\\{'),
            ('}', '\\}'),
            ('$', '\\$'),
            ('&', '\\&'),
            ('%', '\\%'),
            ('#', '\\#'),
            ('^', '\\textasciicircum{}'),
            ('_', '\\_'),
            ('~', '\\textasciitilde{}'),
        ]

        for old, new in replacements:
            text = text.replace(old, new)

        # Convert markdown formatting
        text = re.sub(r'\*\*([^*]+?)\*\*', r'\\textbf{\1}', text)
        text = re.sub(r'\*([^*]+?)\*', r'\\textit{\1}', text)

        # Fix URLs
        text = re.sub(r'//([^\s]+)', r'https://\1', text)

        # Remove any remaining problematic characters
        text = re.sub(r'[^\w\s\.,;:()\[\]/@\-+\\{}]', '', text)

        return text.strip()

    # Minimal LaTeX template to avoid package conflicts
    latex_template = r"""
\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[margin=0.75in]{geometry}

% Basic formatting only
\renewcommand{\familydefault}{\sfdefault}
\pagestyle{empty}

% Simple section formatting
\makeatletter
\renewcommand{\section}[1]{%
  \vspace{12pt}%
  {\large\bfseries #1}%
  \vspace{6pt}%
  \hrule%
  \vspace{6pt}%
}
\makeatother

\begin{document}

%CONTENT%

\end{document}
"""

    try:
        # Check if pdflatex is available
        pdflatex_path = find_pdflatex()
        if not pdflatex_path:
            print("Error: pdflatex not found in system PATH")
            print("Available paths checked:")
            print("- Standard PATH locations")
            print("- /usr/bin/pdflatex")
            print("- /usr/local/bin/pdflatex")
            print("- /Library/TeX/texbin/pdflatex")
            return False

        print(f"Using pdflatex at: {pdflatex_path}")

        # Parse content very simply
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        latex_content = ""

        for line in lines:
            # Name (main title)
            if line.startswith('# '):
                name = clean_text_robust(line[2:])
                latex_content += f"\\begin{{center}}\\Huge\\textbf{{{name}}}\\\\[0.5cm]\\end{{center}}\n\n"

            # Section headers
            elif line.startswith('## '):
                section = clean_text_robust(line[3:])
                latex_content += f"\\section{{{section}}}\n\n"

            # Contact info (center these)
            elif any(
                    line.startswith(x)
                    for x in ['Email:', 'Linkedin:', 'Mobile:']):
                contact = clean_text_robust(line)
                latex_content += f"\\begin{{center}}{contact}\\end{{center}}\n"

            # Bullet points - convert to simple paragraphs to avoid itemize issues
            elif line.startswith(('• ', '- ', '* ')):
                bullet_text = clean_text_robust(line[2:])
                if bullet_text:
                    latex_content += f"\\noindent $\\bullet$ {bullet_text}\\\\[0.2cm]\n"

            # Sub-bullets
            elif line.startswith('◦ '):
                sub_bullet = clean_text_robust(line[2:])
                if sub_bullet:
                    latex_content += f"\\hspace{{0.5cm}}$\\circ$ {sub_bullet}\\\\[0.1cm]\n"

            # Regular paragraphs
            else:
                clean_line = clean_text_robust(line)
                if clean_line:
                    latex_content += f"{clean_line}\\\\[0.2cm]\n"

        # Create full document
        full_latex = latex_template.replace('%CONTENT%', latex_content)

        # Use absolute paths and proper error handling
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)

            # Write LaTeX file
            tex_file = temp_dir / 'resume.tex'
            tex_file.write_text(full_latex, encoding='utf-8')

            # Save debug copy
            debug_path = Path(output_path).with_suffix('.tex')
            debug_path.write_text(full_latex, encoding='utf-8')
            print(f"Debug LaTeX saved to: {debug_path}")

            # Set environment variables for LaTeX
            env = os.environ.copy()
            env['TEXMFOUTPUT'] = str(temp_dir)

            # Compile with full path and environment
            cmd = [
                str(pdflatex_path), '-output-directory',
                str(temp_dir), '-interaction=nonstopmode', '-halt-on-error',
                str(tex_file)
            ]

            print(f"Running command: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                cwd=str(temp_dir),
                env=env,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )

            if result.returncode != 0:
                print(
                    f"LaTeX compilation failed with return code: {result.returncode}"
                )
                print("STDOUT:", result.stdout[-1000:])  # Last 1000 chars
                print("STDERR:", result.stderr[-1000:])

                # Check log file
                log_file = temp_dir / 'resume.log'
                if log_file.exists():
                    log_content = log_file.read_text()
                    print("\nRelevant log lines:")
                    for line in log_content.split('\n'):
                        if any(keyword in line.lower() for keyword in
                               ['error', '!', 'undefined', 'missing']):
                            print(f"  {line}")

                return False

            # Copy PDF to final location
            pdf_file = temp_dir / 'resume.pdf'
            if pdf_file.exists():
                # Use shutil.copy2 for better compatibility
                shutil.copy2(str(pdf_file), output_path)
                print(f"Successfully created PDF: {output_path}")
                return True
            else:
                print("PDF file was not created")
                return False

    except subprocess.TimeoutExpired:
        print("LaTeX compilation timed out (>30 seconds)")
        return False
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


# Test function to verify environment
def test_latex_environment():
    """Test if LaTeX is properly set up."""
    print("Testing LaTeX environment...")

    # Check pdflatex
    if shutil.which('pdflatex'):
        print("✓ pdflatex found in PATH")

        # Test basic compilation
        test_latex = r"""
\documentclass{article}
\begin{document}
Hello World!
\end{document}
"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                tex_file = Path(temp_dir) / 'test.tex'
                tex_file.write_text(test_latex)

                result = subprocess.run([
                    'pdflatex', '-output-directory', temp_dir,
                    '-interaction=nonstopmode',
                    str(tex_file)
                ],
                                        capture_output=True,
                                        timeout=10)

                if result.returncode == 0:
                    print("✓ LaTeX compilation test successful")
                    return True
                else:
                    print("✗ LaTeX compilation test failed")
                    print("Error:", result.stderr[:200])
        except Exception as e:
            print(f"✗ LaTeX test error: {e}")
    else:
        print("✗ pdflatex not found in PATH")

    return False


# Usage for agents:
def safe_create_resume(text: str, output_path: str) -> bool:
    """Entry point that tests environment first."""
    if not test_latex_environment():
        print("LaTeX environment not properly configured")
        return False

    return create_agent_safe_latex_resume(text, output_path)


class ResumeCustomizer:
    """Enhanced Resume Customizer with better error handling, tracking, and flexibility."""

    def __init__(self, model_provider='aws', model_id=None):
        """
        Initialize ResumeCustomizer with configurable model provider.
        
        Args:
            model_provider: 'ollama' or 'aws'
            model_id: Optional specific model ID to use
        """
        self.model_provider = model_provider
        self.model = self._get_model(model_provider, model_id)
        self.agent = Agent(tools=[],
                           show_tool_calls=True,
                           model=self.model,
                           markdown=True)

        # Setup logging
        self._setup_logging()

        # Ensure output directory exists
        self.output_dir = Path("./data/customized_resumes")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Memory for tracking customizations
        self.memory_path = Path("./data/memory.json")

    def _get_model(self, provider: str, model_id: Optional[str] = None):
        """Get LLM model based on provider."""
        return AwsBedrock(id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
                          aws_region='us-east-1',
                          client=bedrock_client)
        if provider == 'ollama':
            return Ollama(id=model_id or 'llama3.1')
        elif provider == 'aws':
            return AwsBedrock(id=model_id
                              or "anthropic.claude-3-sonnet-20240229-v1:0",
                              aws_region='us-east-1')
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _setup_logging(self):
        """Setup logging for resume customization operations."""
        log_dir = Path("./data/logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'resume_customizer.log'),
                logging.StreamHandler()
            ])
        self.logger = logging.getLogger(__name__)

    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract text from PDF while maintaining structure and metadata.
        
        Returns:
            Dict containing text, page_count, and structure info
        """
        try:
            doc = fitz.open(pdf_path)

            result = {
                'text': '',
                'pages': [],
                'page_count': len(doc),
                'structure': {
                    'sections': [],
                    'fonts': set(),
                    'text_blocks': []
                }
            }

            for page_num, page in enumerate(doc):
                page_text = page.get_text()
                result['text'] += page_text + '\n'
                result['pages'].append({
                    'page_num': page_num + 1,
                    'text': page_text,
                    'rect': page.rect
                })

                # Extract text blocks with formatting
                blocks = page.get_text("dict")
                for block in blocks.get("blocks", []):
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line.get("spans", []):
                                result['structure']['fonts'].add(
                                    span.get('font', ''))
                                result['structure']['text_blocks'].append({
                                    'text':
                                    span.get('text', ''),
                                    'font':
                                    span.get('font', ''),
                                    'size':
                                    span.get('size', 0),
                                    'bbox':
                                    span.get('bbox', [])
                                })

            result['structure']['fonts'] = list(result['structure']['fonts'])
            doc.close()

            self.logger.info(
                f"Successfully extracted text from PDF: {pdf_path}")
            return result

        except Exception as e:
            self.logger.error(
                f"Error extracting text from PDF {pdf_path}: {e}")
            return {'text': '', 'pages': [], 'page_count': 0, 'structure': {}}

    def analyze_job_description(self, job_description: str) -> Dict[str, Any]:
        """
        Analyze job description to extract comprehensive requirements.
        
        Args:
            job_description: Full job description text
            
        Returns:
            Dict with structured analysis of job requirements
        """
        try:
            prompt = f"""
            Analyze this job description thoroughly and extract the following information in JSON format:

            {{
                "required_technical_skills": ["skill1", "skill2", ...],
                "preferred_technical_skills": ["skill1", "skill2", ...],
                "required_soft_skills": ["skill1", "skill2", ...],
                "key_responsibilities": ["responsibility1", "responsibility2", ...],
                "industry_keywords": ["keyword1", "keyword2", ...],
                "experience_level": "entry/mid/senior/executive",
                "required_experience_years": "X-Y years or specific number",
                "education_requirements": ["requirement1", "requirement2", ...],
                "company_culture_indicators": ["indicator1", "indicator2", ...],
                "job_type": "full-time/part-time/contract/remote/hybrid",
                "priority_skills": ["top 5 most important skills"],
                "tools_and_technologies": ["tool1", "tool2", ...],
                "certifications": ["cert1", "cert2", ...],
                "salary_range": "if mentioned",
                "benefits": ["benefit1", "benefit2", ...],
                "growth_opportunities": ["opportunity1", "opportunity2", ...]
            }}

            Job Description:
            {job_description}

            Provide only the JSON response with accurate analysis.
            """

            response = self.agent.run(prompt)

            try:
                # Try to extract JSON from response
                content = response.content
                if isinstance(content, str):
                    # Look for JSON in the response
                    start_idx = content.find('{')
                    end_idx = content.rfind('}') + 1
                    if start_idx != -1 and end_idx != 0:
                        json_str = content[start_idx:end_idx]
                        analysis = json.loads(json_str)
                    else:
                        analysis = {
                            'error': 'No JSON found in response',
                            'raw_response': content
                        }
                else:
                    analysis = content

                self.logger.info("Successfully analyzed job description")
                return analysis

            except json.JSONDecodeError as e:
                self.logger.warning(
                    f"Failed to parse JSON from job analysis: {e}")
                return {
                    'error':
                    'JSON parsing failed',
                    'raw_response':
                    response.content,
                    'fallback_analysis':
                    self._extract_basic_job_info(job_description)
                }

        except Exception as e:
            self.logger.error(f"Error analyzing job description: {e}")
            return {
                'error': str(e),
                'fallback_analysis':
                self._extract_basic_job_info(job_description)
            }

    def _extract_basic_job_info(self,
                                job_description: str) -> Dict[str, List[str]]:
        """Fallback method to extract basic job information using simple text processing."""
        # Basic keyword extraction as fallback
        technical_keywords = [
            'python', 'java', 'javascript', 'sql', 'aws', 'docker',
            'kubernetes', 'machine learning', 'data science', 'react',
            'angular', 'node.js'
        ]

        found_skills = []
        for skill in technical_keywords:
            if skill.lower() in job_description.lower():
                found_skills.append(skill)

        return {
            'required_technical_skills': found_skills,
            'priority_skills': found_skills[:5],
            'experience_level': 'mid',  # default assumption
            'key_responsibilities': ['See job description for details']
        }

    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Analyze current resume to understand structure and content comprehensively.
        
        Args:
            resume_text: Extracted resume text
            
        Returns:
            Dict with structured resume analysis
        """
        try:
            prompt = f"""
            Analyze this resume comprehensively and provide analysis in JSON format:

            {{
                "personal_info": {{
                    "name": "extracted name",
                    "email": "extracted email",
                    "phone": "extracted phone",
                    "location": "extracted location",
                    "linkedin": "extracted linkedin",
                    "github": "extracted github"
                }},
                "sections": ["section1", "section2", ...],
                "section_order": ["exact order of sections"],
                "current_skills": {{
                    "technical": ["skill1", "skill2", ...],
                    "soft": ["skill1", "skill2", ...],
                    "tools": ["tool1", "tool2", ...],
                    "programming_languages": ["lang1", "lang2", ...],
                    "frameworks": ["framework1", "framework2", ...]
                }},
                "experience": [
                    {{
                        "company": "company name",
                        "position": "job title",
                        "duration": "time period",
                        "responsibilities": ["resp1", "resp2", ...],
                        "technologies": ["tech1", "tech2", ...]
                    }}
                ],
                "education": [
                    {{
                        "institution": "school name",
                        "degree": "degree type",
                        "field": "field of study",
                        "year": "graduation year"
                    }}
                ],
                "projects": [
                    {{
                        "name": "project name",
                        "description": "project description",
                        "technologies": ["tech1", "tech2", ..."]
                    }}
                ],
                "certifications": ["cert1", "cert2", ...],
                "achievements": ["achievement1", "achievement2", ...],
                "writing_style": "professional/casual/technical",
                "formatting_elements": ["bullets", "sections", "headers", ...],
                "strengths": ["strength1", "strength2", ...],
                "experience_level": "entry/mid/senior",
                "total_experience_years": "number"
            }}

            Resume Text:
            {resume_text}

            Provide only the JSON response with accurate analysis.
            """

            response = self.agent.run(prompt)

            try:
                content = response.content
                if isinstance(content, str):
                    start_idx = content.find('{')
                    end_idx = content.rfind('}') + 1
                    if start_idx != -1 and end_idx != 0:
                        json_str = content[start_idx:end_idx]
                        analysis = json.loads(json_str)
                    else:
                        analysis = {
                            'error': 'No JSON found in response',
                            'raw_response': content
                        }
                else:
                    analysis = content

                self.logger.info("Successfully analyzed resume")
                return analysis

            except json.JSONDecodeError as e:
                self.logger.warning(
                    f"Failed to parse JSON from resume analysis: {e}")
                return {
                    'error': 'JSON parsing failed',
                    'raw_response': response.content
                }

        except Exception as e:
            self.logger.error(f"Error analyzing resume: {e}")
            return {'error': str(e)}

    def generate_customized_content(self,
                                    resume_analysis: Dict,
                                    job_analysis: Dict,
                                    resume_text: str,
                                    customization_level: str = "low") -> str:
        """
        Generate customized resume content with flexible customization levels.
        
        Args:
            resume_analysis: Analysis of current resume
            job_analysis: Analysis of job requirements
            resume_text: Original resume text
            customization_level: "light", "moderate", or "heavy"
            
        Returns:
            Customized resume text
        """
        try:
            customization_instructions = {
                "light":
                "Make minimal changes, only highlight most relevant skills and adjust keywords slightly.",
                "moderate":
                "Modify skills emphasis, adjust experience descriptions, and integrate job-specific keywords naturally.",
                "heavy":
                "Significantly restructure content to match job requirements while maintaining truthfulness."
            }

            prompt = f"""
            You are an expert resume customizer. Customize this resume for the specific job while maintaining authenticity and the original structure.

            CUSTOMIZATION LEVEL: {customization_level.upper()}
            Instructions: {customization_instructions.get(customization_level, customization_instructions["moderate"])}

            ORIGINAL RESUME:
            {resume_text}

            RESUME ANALYSIS:
            {json.dumps(resume_analysis, indent=2)}

            JOB REQUIREMENTS:
            {json.dumps(job_analysis, indent=2)}

            CUSTOMIZATION RULES:
            1. NEVER fabricate experience, skills, or achievements
            2. Maintain the exact same sections and their order
            3. Keep all personal information unchanged
            4. Enhance existing experience descriptions to highlight relevant aspects
            5. Adjust skills section to prioritize job-relevant skills
            6. Integrate job-specific keywords naturally throughout
            7. Maintain the same professional tone and writing style
            8. Keep the same format structure and layout markers
            9. Ensure all claims are truthful and verifiable
            10. Focus on relevance and impact rather than length

            ENHANCEMENT STRATEGIES:
            - Quantify achievements where possible
            - Use action verbs that match job requirements
            - Highlight transferable skills
            - Emphasize relevant projects and experiences
            - Align technical skills with job priorities

            Return ONLY the customized resume text maintaining all original formatting and structure.
            """

            response = self.agent.run(prompt)
            customized_text = response.content

            self.logger.info(
                f"Generated customized content with {customization_level} level customization"
            )
            return customized_text

        except Exception as e:
            self.logger.error(f"Error generating customized content: {e}")
            return resume_text  # Return original if customization fails

    def create_customized_pdf(self,
                              original_pdf_path: str,
                              customized_text: str,
                              output_path: str,
                              preserve_formatting: bool = True) -> bool:
        """
        Create a new PDF with customized content while preserving original layout.
        
        Args:
            original_pdf_path: Path to original PDF
            customized_text: New text content
            output_path: Output path for customized PDF
            preserve_formatting: Whether to attempt to preserve original formatting
            
        Returns:
            bool: Success status
        """
        try:
            # if preserve_formatting:
            #     return self._create_formatted_pdf(original_pdf_path,
            #                                       customized_text, output_path)
            # else:
            self.logger.info(customized_text)
            return self._create_simple_pdf(customized_text, output_path)

        except Exception as e:
            self.logger.error(f"Error creating customized PDF: {e}")
            return False

    def _create_simple_pdf(self, text: str, output_path: str) -> bool:
        """Create simple DOCX with text content."""
        try:
            safe_create_resume(text, output_path)
            self.logger.info(
                f"Successfully created simple DOCX at {output_path}")
            return True

        except ImportError as e:
            self.logger.error(f"python-docx library not installed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error creating simple DOCX: {e}")
            return False

    def customize_resume(self,
                         base_resume_path: str,
                         job_description: str,
                         output_path: str,
                         customization_level: str = "moderate",
                         job_title: str = "",
                         company_name: str = "") -> bool:
        """
        Main function to customize resume with enhanced capabilities.
        
        Args:
            base_resume_path: Path to base resume PDF
            job_description: Full job description text
            output_path: Output path for customized resume
            customization_level: "light", "moderate", or "heavy"
            job_title: Job title for tracking
            company_name: Company name for tracking
            
        Returns:
            bool: Success status
        """
        start_time = datetime.now()

        try:
            self.logger.info(
                f"Starting resume customization for {company_name} - {job_title}"
            )

            # Validate inputs
            if not os.path.exists(base_resume_path):
                self.logger.error(f"Base resume not found: {base_resume_path}")
                return False

            if not job_description.strip():
                self.logger.error("Empty job description provided")
                return False

            # Extract text from base resume
            self.logger.info("Extracting text from base resume...")
            resume_data = self.extract_text_from_pdf(base_resume_path)
            self.logger.info(resume_data['text'])

            if not resume_data['text'].strip():
                self.logger.error("Failed to extract text from resume")
                return False

            # Analyze job description
            self.logger.info("Analyzing job description...")
            job_analysis = self.analyze_job_description(job_description)
            self.logger.info(job_analysis)

            if 'error' in job_analysis:
                self.logger.warning(
                    f"Job analysis had issues: {job_analysis.get('error')}")

            # Analyze current resume
            self.logger.info("Analyzing resume content...")
            time.sleep(60)
            resume_analysis = self.analyze_resume(resume_data['text'])
            self.logger.info(resume_analysis)

            if 'error' in resume_analysis:
                self.logger.warning(
                    f"Resume analysis had issues: {resume_analysis.get('error')}"
                )

            # Generate customized content
            self.logger.info(
                f"Generating customized content (level: {customization_level})..."
            )
            time.sleep(60)
            customized_text = self.generate_customized_content(
                resume_analysis, job_analysis, resume_data['text'],
                customization_level)
            self.logger.info(customized_text)
            time.sleep(60)

            # Create customized PDF
            self.logger.info("Creating customized PDF...")
            success = self.create_customized_pdf(base_resume_path,
                                                 customized_text, output_path)

            if success:
                # Track the customization
                self._track_customization(base_resume_path, output_path,
                                          job_description, job_title,
                                          company_name, customization_level,
                                          start_time)

                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                self.logger.info(
                    f"Resume customization completed successfully in {duration:.2f} seconds"
                )
                self.logger.info(f"Output saved to: {output_path}")
                return True
            else:
                self.logger.error("Failed to create customized PDF")
                return False

        except Exception as e:
            self.logger.error(f"Error in resume customization: {e}")
            return False

    def _track_customization(self, base_path: str, output_path: str,
                             job_description: str, job_title: str,
                             company_name: str, customization_level: str,
                             start_time: datetime):
        """Track customization details in memory system."""
        try:
            memory_data = {}

            if self.memory_path.exists():
                with open(self.memory_path, 'r') as f:
                    memory_data = json.load(f)

            if 'resume_customizations' not in memory_data:
                memory_data['resume_customizations'] = []

            customization_record = {
                'base_resume_path':
                base_path,
                'output_path':
                output_path,
                'filename':
                os.path.basename(output_path),
                'job_title':
                job_title,
                'company':
                company_name,
                'customization_level':
                customization_level,
                'job_description_preview':
                job_description[:200] +
                "..." if len(job_description) > 200 else job_description,
                'timestamp':
                start_time.isoformat(),
                'file_size':
                os.path.getsize(output_path)
                if os.path.exists(output_path) else 0,
                'model_provider':
                self.model_provider
            }

            memory_data['resume_customizations'].append(customization_record)

            with open(self.memory_path, 'w') as f:
                json.dump(memory_data, f, indent=2)

            self.logger.info("Customization tracked successfully")

        except Exception as e:
            self.logger.error(f"Error tracking customization: {e}")

    def batch_customize(
            self,
            jobs_data: List[Dict],
            base_resume_path: str,
            customization_level: str = "moderate") -> Dict[str, Any]:
        """
        Customize resumes for multiple jobs in batch.
        
        Args:
            jobs_data: List of job dictionaries with job details
            base_resume_path: Path to base resume
            customization_level: Customization level for all jobs
            
        Returns:
            Dict with batch processing results
        """
        results = {
            'successful': 0,
            'failed': 0,
            'total': len(jobs_data),
            'details': [],
            'start_time': datetime.now().isoformat()
        }

        self.logger.info(
            f"Starting batch customization for {len(jobs_data)} jobs")

        for i, job in enumerate(jobs_data, 1):
            job_id = job.get('job_id', f'job_{i}')
            job_title = job.get('title', 'Unknown Position')
            company_name = job.get('company', 'Unknown Company')
            job_description = job.get('description', '')

            # Create output filename
            safe_company = "".join(
                c for c in company_name
                if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = "".join(
                c for c in job_title
                if c.isalnum() or c in (' ', '-', '_')).strip()

            filename = f"resume_{job_id}_{safe_company}_{safe_title}.pdf"
            if len(filename) > 100:
                filename = f"resume_{job_id}_{safe_company[:20]}.pdf"

            output_path = self.output_dir / filename

            self.logger.info(
                f"[{i}/{len(jobs_data)}] Processing: {company_name} - {job_title}"
            )

            # Customize resume
            success = self.customize_resume(
                base_resume_path=base_resume_path,
                job_description=job_description,
                output_path=str(output_path),
                customization_level=customization_level,
                job_title=job_title,
                company_name=company_name)

            result_detail = {
                'job_id': job_id,
                'company': company_name,
                'title': job_title,
                'success': success,
                'output_path': str(output_path) if success else None,
                'error': None if success else "Customization failed"
            }

            results['details'].append(result_detail)

            if success:
                results['successful'] += 1
            else:
                results['failed'] += 1

        results['end_time'] = datetime.now().isoformat()

        self.logger.info(
            f"Batch customization completed: {results['successful']}/{results['total']} successful"
        )

        return results

    def get_customization_history(self) -> List[Dict]:
        """Get history of all resume customizations."""
        try:
            if self.memory_path.exists():
                with open(self.memory_path, 'r') as f:
                    memory_data = json.load(f)
                return memory_data.get('resume_customizations', [])
            return []
        except Exception as e:
            self.logger.error(f"Error retrieving customization history: {e}")
            return []

    def cleanup_old_resumes(self, days_old: int = 30) -> int:
        """
        Clean up customized resumes older than specified days.
        
        Args:
            days_old: Remove resumes older than this many days
            
        Returns:
            int: Number of files removed
        """
        try:
            removed_count = 0
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 *
                                                        60)

            for file_path in self.output_dir.glob("*.pdf"):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    removed_count += 1
                    self.logger.info(f"Removed old resume: {file_path.name}")

            self.logger.info(
                f"Cleanup completed: {removed_count} files removed")
            return removed_count

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            return 0


if __name__ == "__main__":
    text = """
# Rishiraj Kalita
Email: rishirajkalita19@gmail.com  
Linkedin: //Rishirak Kalita  
Mobile: 7386260082

## Education
• **National Institute of Technology, Silchar**  
India  
Bachelor of Technology - Computer Science and Engineering; GPA: 8.8  
2019 - 2023

## Skills
• **Programming:**  
Advanced - Python, Spark, SQL, PL/SQL
• **Software Development:**  
Architecture Design, Debugging, Application Development, Code Optimization
• **Relation Databases:**  
RDS, Redshift, Postgres
• **Cloud Solutions:**  
AWS Services, Data Architecture, Solution Design
• **Data Tools:**  
Amazon Glue, EMR, Airflow, S3
• **Development Frameworks:**  
PySpark, HDFS, Hive

## Experience
• **ORGANIZATION: Amazon Web Services**  
**ROLE: Consultant Data Analytics**  
August 2023 - Present
◦ Architecting Software Solutions: Designed scalable and performant software platforms tailored to customer's technical requirements, ensuring high availability and robust architecture.  
◦ Technical Consulting: Providing expert guidance on software development and architecture, including troubleshooting complex issues and recommending optimal implementation approaches.  
◦ Debugging and Optimization: Identifying and resolving software challenges related to platform and application performance, implementing solutions that enhance system efficiency and stability.

• **Organization: Mastercard**  
**Role: Software Developer Intern**  
May 2022 - July 2022  
◦ Developed software applications at scale, focusing on architecture design and performance optimization.  
◦ Debugged complex issues in production systems and implemented improvements to enhance reliability.  
◦ Landed PPO for my work during the internship based on technical problem-solving abilities.

• **ORGANISATION: GEEKSFORGEEKS AND SCALER**  
**Role: Content Writer**  
Freelancing  
◦ Created technically accurate programming tutorials and problem-solving guides focusing on software development concepts and algorithms.  
◦ Developed educational content on Graphs, Trie, Dynamic Programming, SegmentTrees, and other advanced programming topics.  
◦ List of published articles: //Rishiraj-Kalita-Articles-Link

## Projects
◦ **CLOUDERA TO EMR MIGRATION**  
∗**Task:** Executed a comprehensive software architecture migration from Cloudera to Amazon EMR, designing and developing data processing applications using Spark jobs, performing extensive debugging and validation to ensure code integrity, successfully migrating approximately 5000 jobs to the Amazon EMR platform.  
∗**Technologies:** Hive, PySpark, EMR, S3, IAM

◦ **MIGRATING FROM INFORMATICA TO PYSPARK - Amazon GLUE**  
∗**Task:** Architected and implemented robust software solutions to replace Informatica workflows, developing custom PySpark applications for processing and transforming data. Enhanced overall system architecture while troubleshooting complex integration issues between Amazon S3 and Redshift.  
∗**Technologies:** Amazon S3, Glue, MWAA(Airflow), Redshift.

◦ **MIGRATING FROM SISENSE To Business Intelligent Service - Amazon QUICKSIGHT**  
∗**Task:** Designed and developed software components to improve efficiency and consistency of dashboards, transitioning from Sisense to Amazon Quicksight. Architected data models based on different business logic, creating ETL applications that provided reliable data processing.  
∗**Technologies:** Amazon Quicksight, Amazon S3, Glue, Pyspark.

## Certifications
• AWS Certified Data Engineer  
• AWS Certified Machine Learning Specialist  
• AWS Certified Solutions Architect  
• AWS Certified AI Practitioner  
• Solved more than 1500 algorithmic questions on various competitive coding platforms
"""
    result = create_latex_resume(
        text,
        '/Users/rishirajkalita/Desktop/job_orbit_v2/data/customized_resumes/rishi_resume.pdf'
    )
    print(result)
