
import requests
import json
import os
import re
import fitz  # PyMuPDF
from pyspark.sql.functions import pandas_udf
from pyspark.sql.types import StringType
import pandas as pd
from pyspark.sql import SparkSession
import logging
import time

# class SDLC_WIDGET

class SDLC_DATABRICKS():
    def __init__(self, GOOGLE_API_KEY, GITHUB_USERNAME, GITHUB_API, GITHUB_OWNER, GITHUB_REPO, GITHUB_TOKEN, FILE_PATH, GITHUB_BRANCH):
        self.GOOGLE_API_KEY= GOOGLE_API_KEY
        self.GITHUB_USERNAME= GITHUB_USERNAME
        self.GITHUB_TOKEN= GITHUB_TOKEN
        self.FILE_PATH = FILE_PATH
        self.GITHUB_API = GITHUB_API
        self.GITHUB_OWNER = GITHUB_OWNER
        self.GITHUB_REPO = GITHUB_REPO
        self.GITHUB_TOKEN = GITHUB_TOKEN
        self.FILE_PATH = FILE_PATH
        self.GITHUB_BRANCH = GITHUB_BRANCH
        self.spark = SparkSession.builder.appName("SDLC_DATABRICKS").getOrCreate()
        self.logger = logging.getLogger(__name__)
        self.active_model = ""
        logging.basicConfig(level=logging.INFO)

    def generate_response(self, prompt):
        self.logger.info("Generating response from LLM")
        
        # Try Gemini Flash first, then fallback to Gemma
        models = [
            "gemini-2.0-flash",  # primary model
            "gemma-3n-e4b-it"    # fallback model
        ]
        
        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.GOOGLE_API_KEY}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }

            for attempt in range(3):
                try:
                    response = requests.post(url, headers=headers, json=payload)
                    self.logger.info(f"{model} - Attempt {attempt+1} - Status Code: {response.status_code}")

                    if response.status_code == 200:
                        response_text = json.loads(response.text)['candidates'][0]['content']['parts'][0]['text']
                        self.llm_response = response_text
                        self.active_model = model  # Remember the working model
                        self.logger.info(f"Successfully received response from {model}")
                        return self.llm_response
                    else:
                        self.logger.warning(f"{model} - Attempt {attempt+1} failed. Retrying in 5 seconds...")
                        time.sleep(5)

                except Exception as e:
                    self.logger.error(f"Exception with {model} - Attempt {attempt+1}: {str(e)}")
                    time.sleep(5)

            self.logger.warning(f"{model} failed after 3 attempts. Trying next model...")

        self.logger.error("All LLM models failed. No response generated.")
        return None


    def pdf_extractor(self):
        self.logger.info("##---STEP-1: Extracting PDF content.---##")
        try:
            df_pdf = self.spark.read.format("binaryFile").load(self.FILE_PATH)

            @pandas_udf(StringType())
            def extract_text_udf(content_series: pd.Series) -> pd.Series:
                texts = []
                for content in content_series:
                    try:
                        with fitz.open(stream=content, filetype="pdf") as doc:
                            text = "\n".join([page.get_text() for page in doc])
                        texts.append(text)
                    except Exception as e:
                        texts.append(f"ERROR: {e}")
                return pd.Series(texts)

            df_with_text = df_pdf.withColumn("text", extract_text_udf("content"))

            # Fix: use collect instead of rdd
            all_text_list = [row.text for row in df_with_text.select("text").collect()]
            self.all_pdf_text = "\n".join(all_text_list)

            self.logger.info("Successfully extracted PDF content.")
            return self.all_pdf_text
        except Exception as e:
            self.logger.error(f"Error while extracting content from PDF: {str(e)}")


    def func_prompt(self, general_text):
        func_prompt = f"""
                        You are a business analyst. Convert the following general software requirement into a detailed Functional Requirement Document (FRD).

                        Use this Business Requirement Document(BRD) to construct a detailed human like functional requirement document. Write the requirements in bullet point.
                        Adhere to the text present only in the BRD.

                        \"\"\"
                        {general_text}
                        \"\"\"

                        Follow the following functional requirement template:

                        1. Requirement ID
                        FR-<ModuleAbbreviation>-<SequentialNumber>
                        E.g., FR-INV-001

                        2. Title
                        A brief and descriptive title of the functionality.
                        E.g., "Generate Monthly Invoice Reports"

                        3. Description
                        A concise explanation of the business functionality or feature required.
                        E.g., "The system must generate monthly invoice reports for each active customer based on billing data from the previous month."

                        4. Actor(s)
                        Identify all actors (users or systems) involved.
                        E.g., "Customer, Billing System, Admin Portal"

                        5. Preconditions
                        List all conditions that must be true before this function can be executed.
                        E.g., "Customer must have an active subscription; billing data must be available for the month."

                        6. Trigger
                        What event or action initiates the functionality?
                        E.g., "Triggered automatically on the 1st of each month at 12:00 AM."

                        7. Main Flow / Functional Steps
                        Step-by-step explanation of how the function behaves, from trigger to completion.
                        E.g.,

                        System retrieves all active customer accounts.

                        Pulls relevant billing data for each account.

                        Generates PDF reports.

                        Stores reports in secure location.

                        Sends email notification to customers with report link.

                        8. Alternate Flows / Exceptions
                        Define deviations or exceptions to the main flow.
                        E.g.,

                        If billing data is missing → Log error and notify admin.

                        If email delivery fails → Retry twice, then mark as undelivered.

                        9. Postconditions / Outputs
                        What is the state of the system after successful execution?
                        E.g., "Invoice reports are generated, stored, and emailed to customers."

                        10. Business Rules
                        List any rules or logic constraints that apply.
                        E.g., "Do not generate invoices for accounts with a balance of $0."

                        11. Data Requirements (Optional)
                        Define data inputs/outputs or fields involved.
                        E.g.,

                        Input: CustomerID, BillingPeriod, Charges

                        Output: InvoicePDF, EmailStatus

                        12. Assumptions (Optional)
                        Anything assumed to be true for this functionality to work.
                        E.g., "Email service is operational."

                        13. Dependencies (Optional)
                        Any external systems or modules this functionality depends on.
                        E.g., "Depends on CRM module for customer status data."

                        14. Priority
                        High / Medium / Low

                        15. Acceptance Criteria
                        Clear, testable conditions for accepting the requirement.
                        E.g.,

                        Reports generated correctly for all active customers.

                        Email includes correct attachments and metadata.

                        System handles errors gracefully.
                        """
        return func_prompt
                    
    def tech_prompt(self, functional_output):
        tech_prompt = f"""
                        You are a software architect. Based on the following general requirement, generate a **Technical Requirement Document (TRD)**. The TRD should include:

                        Use the Functional Requirement Document(FRD) to construct a detailed human like technical requirement document. Write the requirements in bullet point.
                        Adhere to the text present only in the FRD. Donot simply copy paste the following template, provide the details in every pointers wrt FRD. Fill <provide> section
                        dynamically wrt FRD requirements.

                        \"\"\"
                        {functional_output}
                        \"\"\"

                        Follow the following functional requirement template:

                        1. Technical Requirement ID
                        TR-<ModuleAbbreviation>-<SequentialNumber>
                        E.g., TR-INV-001

                        2. Related Functional Requirement(s)
                        Reference the corresponding FR IDs.
                        E.g., FR-INV-001

                        3. Objective
                        A technical interpretation of what needs to be built.
                        E.g., "Implement a PySpark job to aggregate monthly customer billing data and generate output in Parquet and PDF format."

                        4. Target Cluster Configuration
                        Indicate the Databricks cluster where the job will run.

                        Cluster Name: <provide>

                        Databricks Runtime Version: <provide>

                        Node Type: <provide>

                        Driver Node: <provide>

                        Worker Nodes: <provide>

                        Autoscaling: <provide>

                        Auto Termination: <provide>

                        Libraries Installed: <provide>

                        5. Source Data Details <provide>
                        Dataset Name	Location (Path/Table)	Format	Description
                        

                        6. Target Data Details <provide>
                        Output Name	Location	Format	Description
                        

                        7. Job Flow / Pipeline Stages
                        <provide>

                        8. Data Transformations / Business Logic
                        Step	Description	Transformation Logic
                        <provide>

                        9. Error Handling and Logging
                        <provide>

                        10. Scheduling & Triggering
                        <provide>

                        11. Security & Access Control
                        <provide>

                        12. Dependencies
                        <provide>

                        13. Assumptions
                        <provide>

                        14. Acceptance Criteria
                        <provide>

                        15. Notes / Implementation Suggestions
                        <provide>

                        Consider window functions for future enhancements (e.g., historical comparisons)
                        """
        return tech_prompt

    def functional_document(self):
        self.logger.info("\n##---STEP-2: Generating functional document.---##")
        try:
            # Check if PDF text is already extracted
            if not hasattr(self, 'all_pdf_text') or not self.all_pdf_text:
                self.pdf_extractor()
            else:
                self.logger.info("PDF text already extracted.")

            # Generate functional requirement
            self.functional_output = self.generate_response(self.func_prompt(self.all_pdf_text))
            self.logger.info("Successfully generated functional document.")
            return self.functional_output

        except Exception as e:
            self.logger.error(f"Error while generating functional document: {str(e)}")


    def technical_document(self):
        self.logger.info("\n##---STEP-3: Generating technical document.---##")
        try:
            # Check if PDF text is already extracted
            if not hasattr(self, 'all_pdf_text') or not self.all_pdf_text:
                self.pdf_extractor()
            else:
                self.logger.info("PDF text already extracted.")

            # Generate technical requirement
            self.pdf_extractor()
            self.technical_output = self.generate_response(self.tech_prompt(self.all_pdf_text))
            self.logger.info("Successfully generated technical document.")
            return self.technical_output
        except Exception as e:
            self.logger.error(f"Error while generating technical document: {str(e)}")

    def generate_pyspark_code(self):
        self.logger.info("\n##---STEP-4: Generating pyspark code.---##")
        try:
            """
            Generate PySpark code dynamically based on the functional and technical requirements using GenAI.
            """
            # Check if PDF text is already extracted
            if not hasattr(self, 'technical_output') or not self.technical_output:
                self.technical_document()
            else:
                self.logger.info("Technical document present.")
            
            prompt = f"""
            You are a highly experienced software engineer with deep expertise in enterprise system development, cloud computing, and data engineering. 
            Create relevant code based on techincal requirement provided below. Donot create any code which is out of the technical requirement.

            Technical Requirements:
            {self.technical_output}

            The code should:
            - Strictly adhere to technical requirement.
            - Refine the code to match requirements of the technical requirement.
            - Use PySpark APIs for data processing.
            - Handle large datasets efficiently.
            - Include transformation, cleaning, and aggregation steps.
            - Follow best practices for PySpark.
            - Provide examples of how to execute the code on a Spark cluster.
            - Write proper imports.
            - Avoid generic style coding, create proper and realistic code that can be executed in production environment.
            - Use **realistic naming conventions**, avoid placeholders like "foo" or "bar".
            - Structure the code into functions, classes, or modules if applicable.
            - Ensure the code is clean and readable — avoid boilerplate unless necessary.
            - If integration with APIs, databases, or file systems is required, simulate the structure.
            - If generating PySpark, use appropriate DataFrame operations, transformations, and UDFs.
            - If SQL, generate actual table structures, joins, and WHERE clauses based on context.
            - Avoid “Hello World” or template-style code — write as if you were building this for production.
            - Create directory structure based on the python directory structure.
            - Write mandatorily a set of realistic test cases using pytest. Generate sample input data to check the test.

            project_name/
            │
            ├── src/                  # Source code directory
            │   ├── package_name/     # Main package directory
            │   │   ├── __init__.py   # Initializes the package
            │   │   ├── module1.py    # Module 1
            │   │   ├── module2.py    # Module 2
            │   │   └── ...
            │   └── __init__.py       # (Optional) For src as a package itself
            │
            ├── tests/                # Test suite directory
            │   ├── test_module1.py   # Tests for module 1
            │   ├── test_module2.py   # Tests for module 2
            │   ├── ...
            │   └── __init__.py       # Initializes the test package
            │
            ├── data/                 # Data files (optional)
            │   ├── data1.txt
            │   ├── data2.csv
            │   └── ...
            │
            ├── scripts/              # Executable scripts (optional)
            │   ├── script1.py
            │   ├── script2.py
            │   └── ...
            │
            ├── requirements.txt      # Project dependencies
            ├── pyproject.toml        # Build system configuration
            ├── README.md             # Project description and instructions
            ├── LICENSE               # License information
            └── .gitignore            # Specifies intentionally untracked files that Git should ignore

            Please provide a complete code solution with proper comments and error handling. Mandatorily create all the files provided in the above directory template.

            The final response should look like the following:
            ===================path:<directory_structure>========================
            <generated_code>
            ===========================path:end===================================


            Recheck the code created once with the technical document for relevancy, else recreate or change.
            """

            return self.generate_response(prompt)
        except Exception as e:
            self.logger.error(f"Error while generating pyspark code: {str(e)}")

    def parse_llm_output(self):
        self.logger.info("Parsing LLM output, generating code directory.")
        try:
            pattern = re.compile(r"=+path:(.*?)=+\n(.*?)(?=\n=+path:|\Z)", re.DOTALL)
            matches = pattern.findall(self.llm_response)
            self.llm_parser = {path.strip(): content.strip() for path, content in matches}
            self.logger.info("Successfully parsed LLM output.")
            return self.llm_parser 
        except Exception as e:
            self.logger.error(f"Error during parsing: {str(e)}")

    def clean_files_dict(self):
        self.logger.info("Cleaning code directory.")
        try:
            self.cleaned = {}
            for path, content in self.llm_parser.items():
                # Remove leading './' if present
                clean_path = path.lstrip("./")

                # Remove markdown triple backticks and language tags from content
                # Regex removes ```python or ``` and closing ```
                content_clean = re.sub(r"^```[a-zA-Z]*\n", "", content)  # Remove opening ```
                content_clean = re.sub(r"```$", "", content_clean)       # Remove closing ```
                
                self.cleaned[clean_path] = content_clean
                self.logger.info("Successfully cleaned code directory.")
            return self.cleaned
        except Exception as e:
            self.logger.error(f"Error during code directory cleaning: {str(e)}")


    def github_api_headers(self):
        return {
            "Authorization": f"token {self.GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
        }

    def push_to_github(self, commit_message="Initial commit by library"):
        self.logger.info("\n##---STEP-5: Github process started---##")
        if not self.GITHUB_TOKEN:
            return False, "GitHub token is not set. Please set GITHUB_TOKEN environment variable."

        try:
            # 1. Get the latest commit SHA
            ref_url = f"{self.GITHUB_API}/repos/{self.GITHUB_OWNER}/{self.GITHUB_REPO}/git/ref/heads/{self.GITHUB_BRANCH}"
            ref_resp = requests.get(ref_url, headers=self.github_api_headers())
            ref_resp.raise_for_status()
            latest_commit_sha = ref_resp.json()["object"]["sha"]

            # 2. Get the tree SHA of the latest commit
            commit_url = f"{self.GITHUB_API}/repos/{self.GITHUB_OWNER}/{self.GITHUB_REPO}/git/commits/{latest_commit_sha}"
            commit_resp = requests.get(commit_url, headers=self.github_api_headers())
            commit_resp.raise_for_status()
            base_tree_sha = commit_resp.json()["tree"]["sha"]
            if not base_tree_sha:
                return False, "Base tree SHA is missing."

            # 3. Create blobs from file contents
            blobs = []
            for path, content in self.cleaned.items():
                if path.startswith("/"):
                    path = path.lstrip("/")  # Make path relative

                blob_url = f"{self.GITHUB_API}/repos/{self.GITHUB_OWNER}/{self.GITHUB_REPO}/git/blobs"
                blob_resp = requests.post(
                    blob_url,
                    headers=self.github_api_headers(),
                    json={"content": content, "encoding": "utf-8"},
                )
                blob_resp.raise_for_status()
                blob_sha = blob_resp.json()["sha"]

                blobs.append({
                    "path": path,
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob_sha,
                })

            if not blobs:
                return False, "No files to commit. Blob list is empty."

            # 4. Create a new tree
            tree_url = f"{self.GITHUB_API}/repos/{self.GITHUB_OWNER}/{self.GITHUB_REPO}/git/trees"
            tree_payload = {
                "base_tree": base_tree_sha,
                "tree": blobs
            }
            tree_resp = requests.post(tree_url, headers=self.github_api_headers(), json=tree_payload)
            tree_resp.raise_for_status()
            new_tree_sha = tree_resp.json()["sha"]

            # 5. Create a new commit
            new_commit_payload = {
                "message": commit_message,
                "tree": new_tree_sha,
                "parents": [latest_commit_sha]
            }
            commit_url = f"{self.GITHUB_API}/repos/{self.GITHUB_OWNER}/{self.GITHUB_REPO}/git/commits"
            commit_resp = requests.post(commit_url, headers=self.github_api_headers(), json=new_commit_payload)
            commit_resp.raise_for_status()
            new_commit_sha = commit_resp.json()["sha"]

            # 6. Update the branch to point to the new commit
            update_url = f"{self.GITHUB_API}/repos/{self.GITHUB_OWNER}/{self.GITHUB_REPO}/git/refs/heads/{self.GITHUB_BRANCH}"
            update_resp = requests.patch(update_url, headers=self.github_api_headers(), json={"sha": new_commit_sha})
            update_resp.raise_for_status()
            self.logger.info(f"Code directory pushed to repository: {self.GITHUB_REPO},{self.GITHUB_BRANCH} successfully.")
            return True, "Pushed successfully."

        except requests.exceptions.HTTPError as e:
            self.logger.error(f"Exception raised during git-push: {str(e)}")
            return False, f"HTTPError: {e.response.status_code} {e.response.reason} - {e.response.text}"
        except Exception as e:
            self.logger.error(f"Exception raised during git-push: {str(e)}")
            return False, str(e)

    def run_sdlc(self):
        try:
            self.logger.info("Starting SDLC process.")
            self.pdf_extractor()
            self.functional_document()
            self.technical_document()
            self.generate_pyspark_code()
            self.parse_llm_output()
            self.clean_files_dict()
            self.push_to_github()
            self.logger.info("Completed SDLC process.")
        except Exception as e:
            print(e)

