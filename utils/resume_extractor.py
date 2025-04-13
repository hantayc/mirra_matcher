import json
from datetime import datetime
from openai import OpenAI

class resume_extractor:
    def __init__(self, api_key):
        self.current_month_year = datetime.now().strftime("%B %Y")
        self.client = OpenAI(api_key =api_key)
        print("Resume extractor is loaded...")
    
    def reformat_resume(self, resume):
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": [{
                    "type": "text",
                    "text": f"You are a tool tasked with reorganizing resumes into a structured markdown format. Approach this task step-by-step, take your time, and do not skip any steps in the provided instructions. I will input a series of resumes, so please follow the instructions below carefully:\n\nInstructions Overview: Reorganizing the Resume\n- You will reorganize the resume into 4 main sections: Professional Background, Education, Credentials, and Hard Skills. You should preserve exact text without rephrasing when possible; however, you may split a phrase into separate bullet points while preserving the original wording as closely as possible. \n\nStep 1: Defining Hard Skills and Soft Skills\n- Hard skills are defined as specific, measurable, and technical abilities that are acquired through education, training, or hands-on experience.\n- Soft skills are defined as personal attributes, interpersonal abilities, and non-technical skills. Some examples of soft skills are communication, teamwork, adaptability, problem-solving, time management, creativity, and work ethic. \nStep 1.1: Remove Soft Skills\n- Remove any soft skills from the output entirely, unless they are explicitly associated to a hard skill. \n\nStep 2: \"Professional Background\" section\n- In the Professional Background section, organize the information from each professional experience into the following labeled sections: \n1. Job Title: Original Job Title.\n2. Job Title Base: If a Job Title is mentioned, then clean it by naming the base title of the position excluding any descriptive details that were included in the job title like industry, location, level, or any other additional information. If abbreviations are used to describe seniority level, spell them out. Below are some examples of cleaned job title bases:\nJob Title Example 1 - \"Sr Marketing Manager V\" \nJob Title Base Example 1 - \"Senior Marketing Manager\"\nJob Title Example 2 - \"Staff Business Analyst - Software\" \nJob Title Base Example 2 - \"Staff Business Analyst\"\nJob Title Example 3 - \"Jr. AWS Infrastructure Consultant with Project Management Experience\" \nJob Title Base Example 3 - \"Junior AWS Infrastructure Consultant\"\n3. Field of Job Title: Derive the field based on the title and context of the position (e.g., \"Marketing\", \"Engineering\", etc.).\n4. Related fields of study: For the given job title, infer the most suitable university fields of study for the role. Choose up to 3 fields (If none are suitable, then do not include any) from the following list: [\"Mechanical Engineering\", \"Computer Science\", \"Biological Science\", \"Mathematics\", \"Statistics\", \"Physical Science\", \"Information Science\", \"Electrical Engineering\", \"Economics\", \"Information Technology\", \"Data Science\", \"Medicine\", \"Health Science\", \"Business\", \"Finance\", \"Law\", \"Accounting\", \"Criminology\", \"Behavioral Science\", \"Analytics\", \"Civil Engineering\", \"Aerospace\", \"Industrial Engineering\", \"Environmental Science\", \"Agriculture\", \"Communications\", \"Hospitality\", \"Education\", \"Astronomy\", \"Chemistry\", \"Physics\", \"Geology\", \"Actuarial Science\", \"Architecture\", \"Operations Research\", \"Robotics\", \"Supply Chain\", \"Biomedical Engineering\", \"Software Engineering\", \"Materials Science\", \"Social Science\", \"Psychology\", \"Philosophy\", \"Linguistics\", \"History\", \"Public Administration\", \"Urban Studies\", \"Design\", \"Sports Science\", \"Nutrition Science\", \"Chemical Engineering\", \"Political Science\", \"Anthropology\", \"Sociology\", \"Artificial Intelligence\", \"Cybersecurity\", \"Information Systems\", \"Bioinformatics\"]\n5. Company Name: Only include the name of the company, excluding any additional details.\n6. Company Industry: The industry of the company.\n7. Date Range: If the date range given uses the present or current date as the end of the range, replace it with {self.current_month_year}.\n8. Job Duration: If a range of dates is given, calculate the number of years as a float (e.g., 1.25 years for 1 year 3 months)\n9. Unique Job ID: Create a unique ID by appending the \"Job Title Base\", \"Company Name\", and \"Job Duration\" using \"|\" and without spaces.\n- Example 1: SoftwareEngineer|Google|1.05\n- Example 2: DataAnalyst|Apple|5.75\n10. Job Experience Hard Skills: List bullet points of phrases that describe hard skills or the practical application of hard skills during the given professional experience. Remove any soft skills or the practical application of soft skills from the output entirely, unless they are explicitly associated with a hard skill.\n- For each \"Job Experience Hard Skills\" bullet point in the \"Professional Background\" section, list the job duration next to it in parentheses.\n\nStep 2.1: Remove Quantification Descriptions\n- For every single \"Job Experience Hard Skills\" bullet point, remove any text that quantifies output, including performance results, quantities of items, percentages, and dollar amounts. However, you must not remove any years of experience duration information or numbers that represent the name of a skill, series, version, or year.\nExample Input 1: \"Optimized Hive queries and Spark jobs, achieving a 15% performance improvement and reducing infrastructure costs significantly\"\nExample Output 1: \"Optimized Hive queries and Spark jobs, achieving a performance improvement and reducing infrastructure costs\"\nExample Input 2: \"Created reports that increased data accuracy by 25% and reduced manual data entry by 40%\"\nExample Output 2: \"Created reports that increased data accuracy and reduced manual data entry\"\nExample Input 3: \"Engineered demand forecasting models for 70+ product categories using Prophet, greatly improving inventory management and achieving a 10% increase in product availability.\"\nExample Output 3: \"Engineered demand forecasting models for product categories using Prophet, improving inventory management and achieving an increase in product availability.\"\nExample Input 4: \"Implemented multiple A/B testing strategies for marketing campaigns, resulting in a 25% increase in conversion rates and $2M additional revenue.\"\nExample Output 4: \"Implemented A/B testing strategies for marketing campaigns, increasing conversion rates and additional revenue.\"\nExample Input 5: \"Automated data collection and cleaning processes using Python, saving 20 hours per week of manual work\"\nExample Output 5: \"Automated data collection and cleaning processes using Python, saving manual work\"\nExample Input 6: \"Managed over 240 inbound sales inquiries, converting 18% into warm leads for Territory Managers and closing 22% of the inbound sales inquiries as new accounts.\"\nExample Output 6: \"Managed inbound sales inquiries, converting into warm leads for Territory Managers and closing the inbound sales inquiries as new accounts.\"\nExample Input 7: \"Maintained data pipeline up-time of 99.8% while ingesting streaming and transactional data\"\nExample Output 7: \"Maintained data pipeline up-time while ingesting streaming and transactional data\"\nExample Input 8: \"Recreated various ETL solutions for more than 30 applications in StreamSets\"\nExample Output 8: \"Recreated ETL solutions for applications in StreamSets\"\n\nStep 2.2: Remove Competency-Level Descriptors\n- While preserving the original wording as closely as possible, remove all competency-level descriptors from each \"Job Experience Hard Skills\" bullet point. Some examples of competency-level descriptors include (but are not limited to): \"experience in\", \"knowledge of\", \"skilled in\", \"familiarity with\", \"expertise in\", \"mastery of\", \"proficiency in\", \"experience with\", \"utilized\", \"used\", and \"hands-on experience with\".\n- Do not remove the duration of experience needed.\nExample input 1: \"Experience with SQL Server, Oracle, and MongoDB\"\nExample output 1: \"SQL Server, Oracle, and MongoDB\"\nExample input 2: \"Working knowledge of AWS operations (S3, EC2), Java/JEE, SOAP/REST/Micro Services, XML\"\nExample output 2: \"AWS operations (S3, EC2), Java/JEE, SOAP/REST/Micro Services, XML\"\nExample input 3: \"Proficiency with RAG and GenAI\"\nExample output 3: \"RAG and GenAI\"\nExample input 4: \"Mastery of core programming languages such as Java, Python, and JavaScript\"\nExample output 4: \"core programming languages such as Java, Python, and JavaScript\"\nExample input 5: \"Demonstrated understanding of WAN, LAN, and VPN networks, including the relationship between network infrastructure and IP-enabled devices.\"\nExample output 5: \"WAN, LAN, and VPN networks, including the relationship between network infrastructure and IP-enabled devices.\"\nExample input 6: \"Strong knowledge and work experience with machine learning techniques, fine-tuning, and large language models (LLMs)\"\nExample output 6: \"machine learning techniques, fine-tuning, and large language models (LLMs)\"\nExample input 7: \"Utilized MDG cloud edition, MDG cloud-ready mode, Master Data Integration, One Domain Model\"\nExample output 7: \"MDG cloud edition, MDG cloud-ready mode, Master Data Integration, One Domain Model\"\nExample input 8: \"Knowledge of DevOps process and CI:CD toolset\"\nExample output 8: \"DevOps process and CI:CD toolset\"\nExample input 9: \"Hands-on experience with Oracle Enterprise Manager\"\nExample output 9: \"Oracle Enterprise Manager\"\nExample input 10: \"Used Power Automate, Power Apps, Power BI, SharePoint\"\nExample output 10: \"Power Automate, Power Apps, Power BI, SharePoint\"\nExample input 11: \"Extensive knowledge of Agile/Scrum methodology and practices\"\nExample output 11: \"Agile/Scrum methodology and practices\"\n\nStep 3: \"Education\" section: \n- In the education section, organize the information from each formal education qualification into the following sections: \n1. Degree level: Any high school level degrees should be removed from the output entirely.\n2. Major Field of Study\n3. Minor Field of Study\n4. Institution Name\n5. Date Range Enrolled\n6. Graduation Year\n7. Duration: If a range of dates is listed for the degree, include the number of years as a float. If a date range was not specified, use a duration of 4 years for a bachelor's, 2 years for a master's, 4 years for a PhD, and 2 years for Postdoctoral.\n8. GPA (if provided)\n9. Unique Education ID: Create a unique ID by appending the \"Degree Level\", \"Major\", \"Institution Name\", and \"Duration\" using \"|\" and without spaces.\n\nStep 4: \"Credentials\" section\n- Credentials are defined as Certifications, licenses, security clearances, or similar credential qualifications. \n- Exclude volunteering, fraternities, or other non-professional credentials from the output entirely.\n\nStep 5: \"Hard Skills\" section\n- In this section, extract hard skills that are listed in a skills section, a summary section, or are not listed under a professional experience in the \"Professional Background\" section.\n1. Identify the distinct Hard Skills: When multiple distinct hard skills are listed together and they meet any of the 3 conditions below, the hard skills should each be treated as a logically separate qualification.\nCondition 1: The hard skills are listed in a comma-separated list.\nCondition 2: The hard skills are grouped by parentheses or connected by parenthetical examples.\nCondition 3: The hard skills are grouped using connectors such as \"/\", \"and\", or \"&\".  \n2. Parsing Rule: If hard skills meet any of the three conditions above, you must treat each hard skill as a distinct hard skill and then parse each into separate bullet points.\nExample Input 1: \"Programming Languages: SQL, Python, JAVA\"\nExample Output 1: \n\"- Programming Languages\n- SQL\n- Python\n- JAVA\"\nExample Input 2: \"HTML/CSS\"\nExample Output 2: \n\"- HTML\n- CSS\"\nExample Input 3: \"Virtualization (VMware, VirtualBox)\"\nExample Output 3: \n\"- Virtualization\n- VMware\n- VirtualBox\"\nExample Input 4: \"Linux (Ubuntu/CentOS)\"\nExample Output 4:\n\"- Linux\n- Ubuntu\n- CentOS\"\nExample Input 5: \"AWS operations (S3, EC2), Java/JEE, SOAP/REST/Micro Services, XML\"\nExample Output 5:\n\"- AWS operations\n- S3\n- EC2\n- Java\n- JEE\n- SOAP\n- REST\n- Micro Services\n- XML\"\nExample Input 6: \"JavaScript (ECMAScript 2016)\"\nExample Output 6:\n\"- JavaScript\n- ECMAScript 2016\"\nExample Input 7: \"Data Analysis & Fraud Modeling\"\nExample Output 7: \n\"- Data Analysis\n- Fraud Modeling\"\n3. Include All Modifiers: If any modifiers are used to describe a hard skill, ensure you include them when parsing into separate bullet points. The modifier should be included as part of the distinct hard skill, resulting in one unified distinct hard skill.\nExample Input 8: \"WAN, LAN, and VPN networks\"\nExample Output 8:\n\"- WAN networks\n- LAN networks\n- VPN networks\"\nExample Input 9: \"project management standards and procedures\"\nExample Output 9: \n\"- project management standards\n- project management procedures\"\nExample Input 10: \"Cisco Routers series 9300,7300,6330\"\nExample Output 10: \n\"- Cisco Routers series 9300\n- Cisco Routers series 7300\n- Cisco Routers series 6330\"\nExample Input 11: \"Checkpoint (NGX R65, 3100, 5100, 5900)\"\nExample Output 11: \n\"- Checkpoint NGX R65\n- Checkpoint 3100\n- Checkpoint 5100\n- Checkpoint 5900\"\nExample Input 12: \"AWS (EC2, SQS, SNS, RDS, Cloud Watch, Route 53, IAM, AWS Fargate)\"\nExample Output 12: \n\"- AWS EC2\n- AWS SQS\n- AWS SNS\n- AWS RDS\n- AWS Cloud Watch\n- AWS Route 53\n- AWS IAM\n- AWS Fargate\"\nExample Input 13: \"Angular13/14/15\"\nExample Output 13: \n\"- Angular13\n- Angular14\n- Angular15\"\n4. Remove Soft Skills: Remove any soft skills from the output entirely unless they are explicitly associated to a hard skill.\n5. Exclude any certifications, licenses, and clearances from this section even if they are listed as a skill. If a hard skill includes both a technology and an indication of a certification (e.g., \"Certified Salesforce Administrator\", \"AEM Assets Developer Professional\", \"AWS Certified Cloud Practitioner\"), it must be categorized under \"Credentials\" and excluded from \"Hard Skills\".\n\nStep 6: Exclude all emails, phone numbers, addresses, URL links, or personal names from the output entirely. You may include the names of things like universities and institutions.\n\nStep 7: Output Order\n- Output the reformatted resume in the following section order using level one headings: \n1. \"Professional Background\"\n2. \"Education\"\n3. \"Credentials\"\n4. \"Hard Skills\"\n"
                }]
            },{
                "role": "user",
                "content": [{
                    "type": "text",
                    "text": resume
                }]
            }],
            response_format={
                "type": "text"
            },
            temperature=0,
            max_completion_tokens=15000,
            top_p=1,
            seed = 123,
            frequency_penalty=0,
            presence_penalty=0
        )

        print("reformat_resume is completed..")

        return response.choices[0].message.content

    def extract_resume_skills(self, resume):
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": [{
                    "type": "text",
                    "text": "You are a tool tasked with:\n1. Identifying which hard skills (from the list provided in the \"Hard Skills\" section) were used in each professional job experience and education experience.\n2. Calculating the total years of experience for each hard skill by summing relevant durations.\n3. Outputting all results in a structured JSON format.\nPlease read and follow the instructions below carefully and do not skip any steps.\n\nStep 1: Match Each Hard Skill to Relevant Job IDs\n1. For each hard skill in the \"Hard Skills\" section, review every job in the \"Professional Background\" section and infer which jobs the hard skill was used in by reviewing every \"Job Experience Hard Skills\" bullet point. \n2. If you identify a \"Job Experience Hard Skills\" bullet point that the hard skill was likely used in, append the Job ID of that job to the skill's \"experience_id\" array.\nExample 1: If a \"Job Experience Hard Skills\" bullet in the \"Professional Background\" section mentions \"NLP\", \"deep learning\", or \"TensorFlow\", and \"Python\" is listed in the \"Hard Skills\" section, you should infer \"Python\" was used. Therefore, add the Job ID to the \"experience_id\" list for the given skill. \nExample 2: If a \"Job Experience Hard Skills\" bullet point mentions \"front-end web development\" or \"building responsive UIs\" and you see \"HTML\" or \"CSS\" in the Hard Skills list, you should infer those skills were used. Therefore, add the Job ID to the \"experience_id\" list for the given skill.\nExample 3: If a \"Job Experience Hard Skills\" bullet point mentions \"querying relational databases\" or \"optimizing SQL statements\" and you see \"SQL\" in the Hard Skills list, you should infer \"SQL\" was used. Therefore, add the Job ID to the \"experience_id\" list for the given skill.\n\nStep 2: Match Each Hard Skill to Relevant Education IDs\n1. For each hard skill in the \"Hard Skills\" section, review every education experience in the \"Education\" section and infer which degree the hard skill was used in by reviewing the major and degree level. \n2. If you identify an education experience that the hard skill was likely used in, append the Education ID of that degree to the skill's \"experience_id\" array.\nExample 1: If an education experience in the \"Education\" section is a master's degree in computer science, and \"JAVA\" is listed in the \"Hard Skills\" section, you should infer \"JAVA\" was used. Therefore, add the Education ID to the \"experience_id\" list for the given skill. \nExample 2: If an education experience in the \"Education\" section is a master's degree in information systems, and \"SQL\" is listed in the \"Hard Skills\" section, you should infer \"SQL\" was used. Therefore, add the Education ID to the \"experience_id\" list for the given skill. \n\nStep 3: Sum the Total Years for Each Skill\n1. Once you have evaluated every \"Professional Background\" and \"Education\" for a given hard skill, sum the total duration of each appended Job ID and Education ID in the skill's \"years\" key.\n2. Repeat this for every hard skill listed in the \"Hard Skills\" section, until you have the total duration for each.\n\nStep 4: Generate Structured JSON Output\n- Output the structured JSON, each skill object must include:\n1. \"skill\": A single hard skill.\n2. \"years\": a single numeric value representing total years of experience.\n3. \"experience_id\": an array of Job IDs and/or Education IDs where the skill was used."
                }]
            },{
                "role": "user",
                "content": [{
                    "type": "text",
                    "text": resume
                }]
            }],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "resume_skill_extraction",
                    "strict": True,
                    "schema": {
                        "$id": "resume_extraction_schema",
                        "type": "object",
                        "title": "Resume Extraction Schema - Skills Only",
                        "required": [
                            "skills"
                        ],
                        "properties": {
                            "skills": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": [
                                        "skill",
                                        "years",
                                        "experience_id"
                                    ],
                                    "properties": {
                                        "skill": {
                                            "type": "array",
                                            "items": {
                                                "anyOf": [{
                                                    "type": "string"
                                                },{
                                                    "type": "array",
                                                    "items": {
                                                        "type": "string"
                                                    }
                                                }]
                                            },
                                            "description": "Hard Skills."
                                        },
                                        "years": {
                                            "type": "number",
                                            "description": "Total years of experience with this specific skill."
                                        },
                                        "experience_id": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            },
                                            "description": "One or more identifiers associated with this skill."
                                       }
                                    },
                                    "additionalProperties": False
                                },
                                "description": "Collection of extracted hard skills. Each item represents a skill along with total years of experience."
                            }
                        },
                        "additionalProperties": False
                    }
                }
            },
            temperature=0,
            max_completion_tokens=10000,
            top_p=1,
            seed = 123,
            frequency_penalty=0,
            presence_penalty=0
        )
        print("extract_resume_skills is completed..")
  
        return response.choices[0].message.content

    def extract_resume_info(self, resume):
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": [{
                    "type": "text",
                    "text": """You are a tool used to extract information from a resume into structured JSON format. Approach this task step-by-step, take your time, and do not skip any steps. I will input a series of resumes, so please follow the instructions below carefully:\n\nPart 1: Defining Hard Skills, Background, and Credential Qualifications\n- Categorize the hard skills under \"skill\" keys, professional background under \"background\" keys, and credentials under \"credential\" keys using the following definitions:\n\n\"Hard Skills\" Definition: Specific, teachable, and measurable abilities that are acquired through education, training, or hands-on experience. \n- Hard skills should include those listed under \"Job Experience Hard Skills\" and \"Additional Job Experience Hard Skills\".\n\n\"Professional Background\" Definition: The job titles or roles the candidate has.\n- Exclude the practical application of skills or abilities.\n\n\"Credentials\" Definition: Certifications, licenses, security clearances, certificates, or similar professional credential qualifications. \n- If a qualification includes both a technology and an indication of a certification (e.g., \"Salesforce Administrator Certification\", \"AEM Assets Developer Professional\", \"AWS Certified Cloud Practitioner\"), it must be categorized under the \"Credentials\" category and excluded from the \"Hard Skills\" category.\n\nPart 2: Extracting Hard Skills\nStep 1: Parsing Hard Skills into Verb Phrases and Noun Phrases\n- Parse every single hard skill by carefully following these steps:\n1. Parse every single hard skill bullet point into their verb phrases and noun phrases. \n2. Store these parsed verb phrases and noun phrases together, under the same key and grouped together in an array. Include only noun phrases that do not already appear in a verb phrase. \n3. Do not include the preposition or infinitive in any supporting (adjunct) prepositional phrases or infinitive phrases. However, \"of\" and any other short preposition that is part of the core (head) noun phrase may be included (e.g., \"Development of modeling tools\", \"Configuration in AWS\", etc.).\nExample input 1 - \"Expert in ReactJS\"\nExample parsed output 1 - {\"skill\": [\"ReactJS\"]}\nExample input 2 - \"Hands-on experience with SQL\"\nExample parsed output 2 - {\"skill\": [\"SQL\"]}\nExample input 3 - \"S3\"\nExample parsed output 3 - {\"skill\": [\"S3\"]}\nExample input 4 - \"provided Tier 3 support to the service desk for M365 related issues\"\nExample parsed output 4 - {\"skill\": [\"provided Tier 3 support\", \"the service desk\", \"M365 related issues\"]}\nExample input 5 - \"Combined data from multiple systems into a unified source for analytics\"\nExample parsed output 5 - {\"skill\": [\"Combined data\", \"multiple systems\", \"a unified source\", \"analytics\"]}\n\nStep 2: Identifying and Handling Multiple Hard Skills\nStep 2.1: Identifying Distinct Hard Skills in a Phrase\n- Identify logical AND relationships: When multiple distinct hard skills are listed together in a single phrase and they meet any of the 3 AND conditions below, each hard skill should be treated as a logically separate skill and therefore separately extracted as a distinct hard skill.\nAND Condition 1: The hard skills are listed in a comma-separated list.\nAND Condition 2: The hard skills are grouped by parentheses or connected by parenthetical examples.\nAND Condition 3: The hard skills are grouped using connectors such as \"/\", \"and\", \"or\", or \"&\".\nExample input 1 - \"Proficiency with SQL Server, Oracle, and MongoDB\" \nExample output 1 - {\"skill\": [\"SQL Server\"]}, {\"skill\": [\"Oracle\"]}, {\"skill\": [\"MongoDB\"]} \nExample input 2 - \"AWS: Event Bridge, Cloud Watch, Cloud Trail\"\nExample output 2 - {\"skill\": [\"AWS\"]}, {\"skill\": [\"Event Bridge\"]}, {\"skill\": [\"Cloud Watch\"]}, {\"skill\": [\"Cloud Trail\"]} \nExample input 3 - \"Understanding of RAG and GenAI\"\nExample output 3 - {\"skill\": [\"RAG\"]}, {\"skill\": [\"GenAI\"]}\nExample input 4 - \"Proficiency with cloud platforms such as AWS and Azure\"\nExample output 4 - {\"skill\": [\"cloud platforms\"]}, {\"skill\": [\"AWS\"]}, {\"skill\": [\"Azure\"]}\nExample input 5 - \"Knowledge of Data warehousing schemes, Dimensional modeling, and implementing data storage solutions\" \nExample output 5 - {\"skill\": [\"Data warehousing schemes\"]}, {\"skill\": [\"Dimensional modeling\"]}, {\"skill\": [\"implementing data storage solutions\"]}\n- If any modifiers are used to describe a hard skill you should include them when parsing. The modifier should be included as part of the distinct hard skill, resulting in one unified distinct hard skill. Competency-level descriptors should not be considered as modifiers.\nExample input 6 - \"Demonstrated knowledge of WAN, LAN, and VPN networks.\"\nExample output 6 - {\"skill\": [\"WAN networks\"]}, {\"skill\": [\"LAN networks\"]}, {\"skill\": [\"VPN networks\"]}\nExample input 7 - \"project management standards and procedures\"\nExample output 7 - {\"skill\": [\"project management standards\"]}, {\"skill\": [\"project management procedures\"]}\n\nStep 2.2: Separating Actions and Nominalizations into Distinct Verb Phrases \n1. Identify Every Action or Nominalization  \n- Treat each finite verb, gerund (e.g., \"created\", \"built\"), infinitive verb phrase (e.g., \"to perform\"), or nominalization (e.g., \"development\", \"integration\", \"configuration\") as a distinct item.\n2. Repeat Shared Objects  \n- Coordinate conjunctions (e.g., \"and\", \"or\", commas) that join two or more actions or nominalizations, meaning each one must be separated and repeated with any shared objects.\n- If multiple actions or nominalizations share the same objects (including any phrases introduced by \"for\", \"with\", \"using\", \"to\", etc.), repeat those objects under each separate action or nominalization.  \nExample input 1 - \"created, integrated, and optimized custom solutions for enterprise software applications\"\nExample output 1 - {\"skill\": [\"created custom solutions\", \"enterprise software applications\"]}, {\"skill\": [\"integrated custom solutions\", \"enterprise software applications\"]}, {\"skill\": [\"optimized custom solutions\", \"enterprise software applications\"]} \nExample input 2 - \"developed, established, and maintained operational standards and procedures using Agile methodology\"\nExample output 2 - {\"skill\": [\"developed operational standards\", \"Agile methodology\"]}, {\"skill\": [\"developed operational procedures\", \"Agile methodology\"]}, {\"skill\": [\"established operational standards\", \"Agile methodology\"]}, {\"skill\": [\"established operational procedures\", \"Agile methodology\"]}, {\"skill\": [\"maintained operational standards\", \"Agile methodology\"]}, {\"skill\": [\"maintained operational procedures\", \"Agile methodology\"]}\nExample input 3 - \"Developed modeling, simulation, and design tools for statistical analysis\"\nExample output 3 - {\"skill\": [\"Developed modeling tools\", \"statistical analysis\"]}, {\"skill\": [\"Developed simulation tools\", \"statistical analysis\"]}, {\"skill\": [\"Developed design tools\", \"statistical analysis\"]}\n3. Treat Infinitive or Gerund Phrases as Objects When They Indicate Purpose or Additional Detail\n- If there is a \"to + verb\" or \"-ed\" phrase that represents a goal, purpose, or function (e.g., \"to perform large-scale simulations\", \"developed NLP models\"), treat it as part of the object set.\n- Do not include the preposition or infinitive in any supporting (adjunct) prepositional phrases or infinitive phrases. However, \"of\" and any other short preposition that is part of the core (head) noun phrase may be included.\nExample input 4 - \"Supported development of, and analysis with, advanced numerical computational fluid dynamics tools to perform large-scale simulations\"\nExample output 4 - {\"skill\": [\"Supported development\", \"advanced numerical computational fluid dynamics tools\", \"perform large-scale simulations\"]}, {\"skill\": [\"Supported analysis\", \"advanced numerical computational fluid dynamics tools\", \"perform large-scale simulations\"]} \n4. Identify Logical AND Relationships (Using Step 2.1's Criteria)\n- If any objects in the phrase meet any of the 3 AND conditions from Step 2.1 (commas, parentheses, or connectors like \"and\", \"or\", '/\"), separate those objects into distinct skill entries. This ensures each action or nominalization is paired with each relevant object, split out as individual \"skill\" keys when AND conditions exist.\nExample input 5 - \"Cloud deployment with AWS, Azure, and Google Cloud\"\nExample output 5 - {\"skill\": [\"Cloud deployment\", \"AWS\"]}, {\"skill\": [\"Cloud deployment\", \"Azure\"]}, {\"skill\": [\"Cloud deployment\", \"Google Cloud\"]}\nExample input 6 - \"version control using Git, SVN, and Mercurial\"\nExample output 6 - {\"skill\": [\"version control\", \"Git\"]}, {\"skill\": [\"version control\", \"SVN\"]}, {\"skill\": [\"version control\", \"Mercurial\"]}\nExample input 7 - \"Created multiple forms using HTML, CSS, JavaScript, jQuery, AJAX\"\nExample output 7 - {\"skill\": [\"Created multiple forms\", \"HTML\"]}, {\"skill\": [\"Created multiple forms\", \"CSS\"]}, {\"skill\": [\"Created multiple forms\", \"JavaScript\"]}, {\"skill\": [\"Created multiple forms\", \"jQuery\"]}, {\"skill\": [\"Created multiple forms\", \"AJAX\"]}\nExample input 8 - \"Used Web Services for project management, architecture, production, application development and ongoing maintenance\"\nExample output 8 - {\"skill\": [\"Used Web Services\", \"project management\"]}, {\"skill\": [\"Used Web Services\", \"architecture\"]}, {\"skill\": [\"Used Web Services\", \"production\"]}, {\"skill\": [\"Used Web Services\", \"application development\"]}, {\"skill\": [\"Used Web Services\", \"ongoing maintenance\"]}\n5. Replicate All Relevant Parts in Each Sub-Phrase  \n- If multiple actions or nominalizations are followed by multiple objects, replicate both the action (or nominalization) and each object so that no detail is lost (i.e., every action is paired with every object if they are logically AND; or combined in nested arrays if they are logically OR).  \n- If the phrase includes supporting details, include them in each repeated sub-phrase. \nExample input 9 - \"Developed comprehensive threat detection and response strategies using cybersecurity architectures, IDS/IPS, SIEM tools, and firewalls\"\nExample output 9 - {\"skill\": [\"Developed comprehensive threat detection\", \"cybersecurity architectures\"]}, {\"skill\": [\"Developed comprehensive threat detection\", \"IDS\"]}, {\"skill\": [\"Developed comprehensive threat detection\", \"IPS\"]}, {\"skill\": [\"Developed comprehensive threat detection\", \"SIEM tools\"]}, {\"skill\": [\"Developed comprehensive threat detection\", \"firewalls\"]}, {\"skill\": [\"Developed comprehensive response strategies\", \"cybersecurity architectures\"]}, {\"skill\": [\"Developed comprehensive response strategies\", \"IDS\"]}, {\"skill\": [\"Developed comprehensive response strategies\", \"IPS\"]}, {\"skill\": [\"Developed comprehensive response strategies\", \"SIEM tools\"]}, {\"skill\": [\"Developed comprehensive response strategies\", \"firewalls\"]}\nExample input 10 - \"built and deployed NLP/AI/ML models\"\nExample output 10 - {\"skill\": [\"built NLP models\"]}, {\"skill\": [\"built AI models\"]}, {\"skill\": [\"built ML models\"]}, {\"skill\": [\"deployed NLP models\"]}, {\"skill\": [\"deployed AI models\"]}, {\"skill\": [\"deployed ML models\"]}\nExample input 11 - \"wrote and tested code using PostgreSQL/MySQL queries and Python\"\nExample output 11 - {\"skill\": [\"wrote code\", \"PostgreSQL queries\", \"MySQL queries\" ]}, {\"skill\": [\"wrote code\", \"Python\"]}, {\"skill\": [\"tested code\", \"PostgreSQL queries\", \"MySQL queries\" ]}, {\"skill\": [\"tested code\", \"Python\"]}\nExample input 12 - \"designed and managed data warehouses using Snowflake, Databricks, and AWS\"\nExample output 12 - {\"skill\": [\"designed data warehouses\", \"Snowflake\"]}, {\"skill\": [\"managed data warehouses\", \"Snowflake\"]}, {\"skill\": [\"designed data warehouses\", \"Databricks\"]}, {\"skill\": [\"managed data warehouses\", \"Databricks\"]}, {\"skill\": [\"designed data warehouses\", \"AWS\"]}, {\"skill\": [\"managed data warehouses\", \"AWS\"]}\nExample input 13 - \"Designed and implemented solutions incorporating architectures such as SOA, Event Driven, MVC, Django, and serverless\"\nExample output 13 - {\"skill\": [\"Designed solutions\", \"architectures\", \"SOA\"]}, {\"skill\": [\"Designed solutions\", \"architectures\", \"Event Driven\"]}, {\"skill\": [\"Designed solutions\", \"architectures\", \"MVC\"]}, {\"skill\": [\"Designed solutions\", \"architectures\", \"Django\"]}, {\"skill\": [\"Designed solutions\", \"architectures\", \"serverless\"]}, {\"skill\": [\"implemented solutions\", \"architectures\", \"SOA\"]}, {\"skill\": [\"implemented solutions\", \"architectures\", \"Event Driven\"]}, {\"skill\": [\"implemented solutions\", \"architectures\", \"MVC\"]}, {\"skill\": [\"implemented solutions\", \"architectures\", \"Django\"]}, {\"skill\": [\"implemented solutions\", \"architectures\", \"serverless\"]}\nExample input 14 - \"Created and updated the Swagger files to configure the definition objects and parameters of service end points\"\nExample output 14 - {\"skill\": [\"Created the Swagger files\", \"configure the definition objects\"]}, {\"skill\": [\"Created the Swagger files\", \"configure the parameters\", \"service end points\"]}, {\"skill\": [\"updated the Swagger files\", \"configure the definition objects\"]}, {\"skill\": [\"updated the Swagger files\", \"configure the parameters\", \"service end points\"]}\n\nStep 2.3: Handling Abbreviations and Acronyms in Hard Skills\n- If both a hard skill and its abbreviation or acronym are given, you should treat them as separate and distinct hard skills.\nExample input 1 - \"SSIS (SQL Server Integration Services)\"\nExample output 1 - {\"skill\": [\"SSIS\"], \"skill\": [\"SQL Server Integration Services\"]}\nExample input 2 - \"Involved in SDLC (System Development Life Cycle) of the total system and followed Agile/Scrum\"\nExample output 2 - {\"skill\": [\"SDLC\", \"total system\", \"followed Agile\"]}, {\"skill\": [\"SDLC\", \"total system\", \"followed Scrum\"]}, {\"skill\": [\"System Development Life Cycle\", \"total system\", \"followed Agile\"]}, {\"skill\": [\"System Development Life Cycle\", \"total system\", \"followed Scrum\"]}\n\nStep 3: Extract the Job IDs\n- For each hard skill that is listed under \"Job Experience Hard Skills\" extract the Job ID into the \"job_id\" key. \n- For hard skills listed under the \"Hard Skills\" section, leave job_id blank.\n\nPart 3: Extracting Professional Background and Credentials\nStep 1: Handling Multiple Job Titles\n - If multiple job titles for a professional experience are given using connectors such as \"/\", \"and\", \"&\", parentheses, or are simply separated by commas, you should separate them as distinct string items and store them in a shared array. \nExample input 1 - \"Business Analyst/Business Operations Analyst\"\nExample output 1 - {\"background\" : [\"Business Analyst\", \"Business Operations Analyst\"]}\nExample input 2 - \"IT Specialist & IT Manager\"\nExample output 2 - {\"background\" : [\"IT Specialist\", \"IT Manager\"]}\n- If any modifiers are used to describe the roles, ensure you include them with each role.\nExample input 3 - \"Senior Software Engineer/Developer\"\nExample output 3 - {\"background\" : [\"Senior Software Engineer\", \"Senior Software Developer\"]}\nExample input 4 - \"Salesforce Engineer & Architect\"\nExample output 4 - {\"background\" : [\"Salesforce Engineer\", \"Salesforce Architect\"]}\n\nStep 2: Handling Multiple Credentials in a Single Phrase\n - If multiple credentials are grouped using connectors such as \"/\", \"and\", \"&\", parentheses, or are simply separated by commas, you should separate them and extract them as separate keys. \nExample input 1 - \"Salesforce Certified Administrator/Salesforce Certified Advanced Administrator\"\nExample output 1 - {\"credential\": [\"Salesforce Certified Administrator\"]}, {\"credential\": [\"Salesforce Certified Advanced Administrator\"]}\n- If any modifiers are used to describe the roles, ensure you include them with each role.\nExample input 2 - \"AWS Certified Cloud Practitioner/Solutions Architect\"\nExample output 2 - {\"credential\": [\"AWS Certified Cloud Practitioner\"]}, {\"credential\": [\"AWS Certified Solutions Architect\"]}\nExample input 3 - \"Certified as IAT and IAM Level III\"\nExample output 3 - {\"credential\": [\"IAM Level III\"], \"credential\": [\"IAT Level III\"]}\n\nStep 3: Handling Abbreviations and Acronyms in Professional Background and Credentials\n- If both a qualification and its abbreviation or acronym are given for either a professional background or a credential, you should separate them and extract them as separate keys.\nExample input 1 - \"CCNP (Cisco Certified Network Professional)\"\nExample output 1 - {\"credential\": [\"CCNP\"]}, {\"credential\": [\"Cisco Certified Network Professional\"]}\nExample input 2 - \"CheckPoint Certified Security Administrator (CCSA) and CheckPoint Certified Security Expert (CCSE)\"\nExample output 2 - {\"credential\": [\"CheckPoint Certified Security Administrator\"]}, {\"credential\": [\"CCSA\"]}, {\"credential\": [\"CheckPoint Certified Security Expert\"]}, {\"credential\": [\"CCSE\"]}\n\nStep 4: Add Additional Background Information \nFor each \"background\" key in the list:\n1. Add the years of experience under the \"years\" key, using the job duration information.\n2. Identify and include any associated industries explicitly mentioned for that professional experience in a key called \"industry\" as separate values in an array. If no industries are listed for the professional experience, then do not list anything.\n3. Store the related fields of study for a job title in the \"related_fields_of_study\" key.\n4. Store the \"Job Title Base\" value and the \"Field of Job Title\" value in the \"background\" array with the job title. However, if the \"Job Title Base\" value is the exact same as the job title, do not include it in the array. \nExample Input 1:\nJob Title: \"Software Engineer Intern (Summer 2024)\",\nJob Title Base: \"Software Engineer Intern\"\nField of Job Title: \"Software Engineering\" \nExample Output 1:\n{\"background\": [\"Software Engineer Intern (Summer 2024)\", \"Software Engineer\", \"Software Engineering\"]}\nExample Input 2:\nJob Title: \"Data Engineer\"\nJob Title Base: \"Data Engineer\"\nField of Job Title: \"Data Engineering\" \nExample Output 2:\n{\"background\": [\"Data Engineer\", \"Data Engineering\"]}\nExample Input 3:\nJob Title: \"Technical Program Manager\"\nJob Title Base: \"Technical Program Manager\"\nField of Job Title: \"Information Technology\" \nExample Output 3:\n{\"background\": [\"Technical Program Manager\", \"Information Technology\"]}\n\nPart 4: Extracting Education Qualifications\n- Next, extract the level of education qualifications from the resume by following these steps:\nStep 1 - Extract the levels of education as \"education_level\" keys and categorize them under one of the following values that fits best: \"High School Diploma\", \"Associate's\", \"Current Bachelor's Student\", \"Some Bachelor's\", \"Bachelor's\", \"Some Master's\", \"Current Master's Student\", \"Master's\", \"PhD\", \"Postdoctoral\", \"Vocational\".\n\nStep 2 - For each level of education in the list, identify and include any fields of study mentioned in the \"field_of_study\" key as separate values in an array. If the field of study was a major, list the field under the \"major\" key, and if it was a minor list it under the \"minor\" key. If no fields of study are listed, then do not list anything.\n\nPart 5: Organize and Structure the Output\n- Organize the skills, professional background, education, and credentials under respective JSON objects and output the final JSON."""
                }]
            }, {
                "role": "user",
                "content": [{
                    "type": "text",
                    "text": resume
                }]
            }],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "resume_extraction",
                    "schema": {
                        "$id": "resume_extraction_schema",
                        "type": "object",
                        "title": "Resume Extraction Schema",
                        "required": [
                            "skills",
                            "professional_background",
                            "education",
                            "credentials"
                        ],
                        "properties": {
                            "skills": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": [
                                        "skill",
                                        "years",
                                        "job_id"
                                    ],
                                    "properties": {
                                        "skill": {
                                            "type": "array",
                                            "items": {
                                                "anyOf": [{
                                                    "type": "string"
                                                },{
                                                    "type": "array",
                                                    "items": {
                                                        "type": "string"
                                                    }
                                                }]
                                            },
                                            "description": "Hard skills."
                                        },
                                         "years": {
                                            "type": "number",
                                            "description": "Total years of experience with this specific skill."
                                        },
                                        "job_id": {
                                            "type": "string",
                                            "description": "A job identifier associated with this skill."
                                        }
                                    },
                                    "additionalProperties": False
                                },
                                "description": "Collection of extracted hard skills. Each item represents a skill along with total years of experience."
                            },
                            "education": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": [
                                        "education_level",
                                        "major",
                                        "minor",
                                        "gpa",
                                        "institution"
                                    ],
                                    "properties": {
                                    "gpa": {
                                        "type": "number",
                                        "description": "Candidate's GPA (if provided)."
                                    },
                                    "major": {
                                        "type": "array",
                                        "items": {
                                            "type": "string"
                                        },
                                        "description": "List of major fields of study if specified by the candidate."
                                    },
                                    "minor": {
                                        "type": "array",
                                        "items": {
                                            "type": "string"
                                        },
                                        "description": "List of minor fields of study if specified by the candidate."
                                    },
                                    "institution": {
                                        "type": "string",
                                        "description": "Name of the educational institution (if provided)."
                                    },
                                    "education_level": {
                                        "enum": [
                                            "High School Diploma",
                                            "Associate's",
                                            "Current Bachelor's Student",
                                            "Bachelor's",
                                            "Some Bachelor's",
                                            "Current Master's Student",
                                            "Some Master's",
                                            "Master's",
                                            "PhD",
                                            "Postdoctoral",
                                            "Vocational"
                                        ],
                                        "type": "string",
                                        "description": "Normalized education level that best matches the candidate's stated qualification."
                                    }
                                },
                                    "additionalProperties": False
                                },
                                "description": "Collection of educational qualifications including level, fields of study (major/minor), GPA, and institution."
                            },
                            "credentials": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": [
                                        "credential"
                                    ],
                                    "properties": {
                                        "credential": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            },
                                            "description": "Array of credential details."
                                        }
                                    },
                                    "additionalProperties": False
                                },
                                "description": "Collection of extracted credentials such as certifications, licenses, or clearances."
                            },
                            "professional_background": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": [
                                        "background",
                                        "years",
                                        "industry",
                                        "related_fields_of_study"
                                    ],
                                    "properties": {
                                        "years": {
                                            "type": "number",
                                            "description": "Sum of years of experience in this background or role."
                                        },
                                        "industry": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            },
                                            "description": "Any explicitly mentioned industries for this background. Each item is one industry."
                                        },
                                        "background": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            },
                                            "description": "Background qualifications."
                                        },
                                        "related_fields_of_study": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            },
                                            "description": "The related field of studies for the given role."
                                        }
                                    },
                                    "additionalProperties": False
                                },
                                "description": "Collection of professional backgrounds or job titles along with total years of experience, plus any explicitly mentioned industries."
                            }
                        },
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            temperature=0,
            max_completion_tokens=15000,
            top_p=1,
            seed = 123,
            frequency_penalty=0,
            presence_penalty=0
        )
        print("extract_resume_info is completed..")
  
        return response.choices[0].message.content
    
    def format_skills_as_bullets(self, skills_json):
        """
            Takes a JSON/dict object with a "skills" key (each item has 'skill' and 'years'),
            and returns a string that includes a "# Hard Skills" header followed by bullet points:

            # Hard Skills
            - Some Skill (2.33 years)
        """
        lines = ["# Hard Skills\n"]
        for entry in skills_json.get("skills", []):
            skill_name = entry["skill"][0] if entry["skill"] else "Unknown Skill"
            years = entry.get("years", 0)
            lines.append(f"- {skill_name} ({years} years)")

        print("format_skills_as_bullets is completed..")
        
        return "\n".join(lines)

    def replace_hard_skills_section(self, resume_text, new_hard_skills_section):
        """
            Removes the existing # Hard Skills section from the input resume_text
            (from the # Hard Skills header to the end of the text)
            and appends the new_hard_skills_section at the end.
    
            :param resume_text: A string containing the full resume.
            :param new_hard_skills_section: A string containing the new # Hard Skills section (including the '# Hard Skills' header).
            :return: A string with the old # Hard Skills section removed and the new section appended.
        """
        lines = resume_text.split("\n")
    
        start_index = None
        # Find the line that matches "# Hard Skills"
        for i, line in enumerate(lines):
            if line.strip() == "# Hard Skills":
                start_index = i
                break

        # If there's no # Hard Skills in the resume, just append it
        if start_index is None:
            return resume_text.strip() + "\n\n" + new_hard_skills_section

        # Remove everything from the # Hard Skills header to the end
        updated_resume_lines = lines[:start_index]

        print("replace_hard_skills_section is completed..")

        # Append the new Hard Skills section
        return "\n".join(updated_resume_lines).strip() + "\n\n" + new_hard_skills_section

    def normalize_skill(self, skill_list):
        """
        Normalize the skill list: for every item, if it is a string, lower-case and strip it.
        If it’s a list (group of skills), convert it into a tuple of lower-case stripped strings.
        Returns a tuple representing the normalized skill value.
        """
        normalized = []
        for item in skill_list:
            if isinstance(item, str):
                normalized.append(item.strip().lower())
            elif isinstance(item, list):
                # Convert inner list to a tuple of lower-case strings.
                normalized.append(tuple(s.strip().lower() for s in item if isinstance(s, str)))
            else:
                # Fallback: convert any other type to string.
                normalized.append(str(item).strip().lower())
        return tuple(normalized)

    def is_duplicate(self, entry_a, entry_b):
        """
        Two entries are considered duplicates if:
        - Their normalized "skill" arrays are identical (order and grouping preserved), and
        - Either both have nonempty job_id and the job_ids are identical,
            OR at least one of the entries has an empty job_id.
        """
        norm_a = self.normalize_skill(entry_a["skill"])
        norm_b = self.normalize_skill(entry_b["skill"])
        if norm_a != norm_b:
            return False

        job_a = entry_a.get("job_id", "")
        job_b = entry_b.get("job_id", "")
        
        # If both job_id values are non-empty, they must match exactly.
        if job_a and job_b:
            return job_a == job_b
        # Otherwise, if at least one is empty, consider as duplicates.
        return True

    def compare_entries(self, entry_new, entry_existing):
        """
        Decide if 'entry_new' should replace 'entry_existing'.
        The one with the larger 'years' value wins.
        In case of equal years, we favor the one with a nonempty job_id.
        
        Returns True if entry_new should replace entry_existing.
        """
        if entry_new["years"] > entry_existing["years"]:
            return True
        elif entry_new["years"] < entry_existing["years"]:
            return False
        else:
            # If years are equal, give priority to an entry with a job_id.
            if entry_existing.get("job_id", "") == "" and entry_new.get("job_id", ""):
                return True
            else:
                return False

    def deduplicate_skills(self, resume_json):
        """
        Given a resume JSON (following the JSON schema provided) this function removes duplicate
        skill entries according to the following rules:
        1. Two entries are duplicates if their entire "skill" field (an array) are equal (case-insensitive),
            and either both have nonempty job_id (which then must match exactly) or at least one entry's job_id is empty.
        2. If duplicates are found and one entry has a job_id while the other doesn't,
            then the one with the larger 'years' value wins. If the 'years' values are equal,
            then the entry with a job_id is preferred.
        
        The function returns the updated JSON with a deduplicated "skills" array.
        """
        deduped = []  # will store the winning skills
        
        for entry in resume_json.get("skills", []):
            entry_winner = entry  # candidate entry
            duplicate_found = False  # flag to signal if a duplicate was encountered

            # Check against already deduplicated entries.
            indices_to_remove = []  # track which duplicates to remove if the new entry wins

            for i, existing in enumerate(deduped):
                if is_duplicate(entry_winner, existing):
                    duplicate_found = True
                    # Compare by years and job_id presence.
                    if compare_entries(entry_winner, existing):
                        # New entry wins over the existing one—mark existing for removal.
                        indices_to_remove.append(i)
                    else:
                        # Existing entry wins; do not add the new entry.
                        entry_winner = None
                        break

            # Remove any losing duplicate(s) (if the new entry won over them).
            for idx in sorted(indices_to_remove, reverse=True):
                deduped.pop(idx)
                
            # If entry_winner is still valid (i.e. it didn’t lose a duplicate check), add it.
            if entry_winner is not None:
                deduped.append(entry_winner)
        
        # Replace the "skills" list in the input JSON with the deduplicated list.
        resume_json["skills"] = deduped
        return resume_json


    def deduplicate_background_values(self, resume_json):
        """
        For each professional background entry in resume_json, deduplicate the 'background'
        array using a case-insensitive comparison. This function only deduplicates within
        each individual 'background' array and preserves the order of first appearance.
        """
        for entry in resume_json.get("professional_background", []):
            original_background = entry.get("background", [])
            seen = set()
            deduped_background = []
            for bg in original_background:
                # Normalize the string for comparison: lower-case and stripped.
                norm_bg = bg.lower().strip()
                if norm_bg not in seen:
                    seen.add(norm_bg)
                    deduped_background.append(bg)
            entry["background"] = deduped_background
        return resume_json

    def process_resume_to_json(self, resume_text):
        """
            Takes a raw resume string as input, processes it through various steps,
            and returns a JSON object with the extracted and updated resume information.
        """
        # 1. Reformat the resume text (based on your desired transformations).
        reformatted = self.reformat_resume(resume_text)

        # 2. Extract skills from the reformatted resume.
        extracted_skills = self.extract_resume_skills(reformatted)
        extracted_skills_json = json.loads(extracted_skills)
    
        # 3. Convert the extracted skills into bullet point format.
        hard_skills_bullets = self.format_skills_as_bullets(extracted_skills_json)
    
        # 4. Replace the existing hard-skills section with the newly formatted bullets.
        updated_resume = self.replace_hard_skills_section(reformatted, hard_skills_bullets)
    
        # 5. Extract all remaining resume info and store it in JSON.
        resume_json_raw = json.loads(self.extract_resume_info(updated_resume))

        # 6. Deduplicate skills
        deduped_skills = self.deduplicate_skills(resume_json_raw)

        # 7. Deduplicate background
        resume_json = self.deduplicate_background_values(deduped_skills)

        print("extraction is completed..")
    
        return resume_json
    