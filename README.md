# Replication Package of InitScope

## A Python-based Inefficiency Localization Tool tailored for Serverless Applications

## Abstract
Background: Serverless computing has gained significant popularity due to its scalability, cost efficiency, and abstraction of infrastructure management. However, a major challenge remains in the form of cold-start latency—a delay that occurs when serverless functions are invoked after an idle period, often caused by the initialization of application libraries. Localizing the source of this latency is particularly difficult due to the complex and dynamic nature of serverless applications.
Aims: This research aims to (1) develop and evaluate a developer-oriented tool for precise, code-centric localization of library initialization inefficiencies contributing to cold-start latency, (2) systematically create a taxonomy of recurring antipatterns associated with these initialization inefficiencies, and (3) empirically assess the practical impact and utility of the tool on software development practices through developer studies.
Method: We designed and implemented an inefficiency localization tool, INITSCOPE tailored for Python-based serverless applications. The tool leverages dynamic profiling, specifically statistical sampling and call-path profiling techniques, to precisely attribute cold-start inefficiencies at the source-code level. Using this tool, we conducted an extensive manual analysis to systematically identify and classify recurring anti-patterns in library initialization that contribute significantly to cold-start latency. To empirically evaluate its practical effectiveness, we carried out a mixed-method study consisting of a survey of 30 experienced serverless developers, supplemented by follow-up interviews with six participants who used the tool.
Results: The proposed approach, INITSCOPE, for localizing cold-start inefficiencies at the source-code level significantly outperformed all baseline methods, achieving 83.3% higher Top-N accuracy. With inefficiencies localized by INITSCOPE, our analysis identified four common library initialization antipatterns that significantly contribute to cold-start latency. Moreover, developer evaluations demonstrated the tool’s effectiveness in localizing these inefficiencies, enabling targeted optimizations that substantially reduced latency and memory usage. At the same time, qualitative feedback highlighted enhanced developer awareness and encouraged more performance-conscious coding practices.
Conclusions: The research proposed INITSCOPE, for localizing cold-start inefficiencies for serverless applications and provides empirical evidence of prevalent library initialization anti-patterns and demonstrates the value of a profiling-driven, developercentric approach in mitigating cold-start latency. Our findings underscore the importance of incorporating precise, code-level performance insights into serverless application development practices.

## Replication

In the following sections, we describe how to use this replication package

### File Structure
- `profiler`: contains the InitScope profiler 
- `visualizer_guide`: contains step by step guidance explaining "How to use InitScope visualizer". The live visualizer url is given in the end of this file.
- `data`: contains the data-files
- `cdf_plots`: contains the cumulative distribution plots of both initialization and execution latency
  Each subdirectory is named after the application and each of them contains 2 files `initialization_latency.png` and `execution_latency.png`
- `applications`:
    - This directory contains all the applications we evaluate in this work
    - Each sub directory represents application names which include both original and optimized code
        - `original`: represents the original code of each applications
        - `optimized`: represents the optimized code of each applications
            - `hanlder.py`: Is the serverless function handler which is the main program file. It may also have names as `lambda_function.py`
            - `requirements.txt`: The dependencies for each application
            - `Dockerfile`: The command file that allow you build Docker images for the application
            - Some applications may contain specialized files for machine learning model, input dataset etc.

### Prerequisites
- Access to AWS Console
- Access to AWS services including Lambda, S3, CloudWatch, ECR with execution role
- Python 3.9 runtime
- AWS CLI
- Docker

### Dependency Installations
```
pip install -r ./requirements.txt --platform manylinux2014_x86_64 --target=./$(PACKAGE_DIRNAME) --implementation cp --python-version $(PYTHON_VERSION) --only-binary=:all: --upgrade
```

### Create Deployment Package
```
rm -rf $(ZIP_FILE_NAME)
cd $(PACKAGE_DIRNAME); zip -r ../$(ZIP_FILE_NAME) .; cd ..
zip -r $(ZIP_FILE_NAME) handler.py
```

### Create AWS Lambda Function
Use the command below to create lambda function but provide appropriate data to all the place holders.
```
aws lambda create-function --function-name $(LAMBDA_NAME) \
--runtime $(RUNTIME) --role $(ROLE_ARN) --handler $(HANDLER) \
--zip-file fileb://$(ZIP_FILE_NAME) --timeout $(TIMEOUT) --memory-size $(MEMORY_SIZE) \
--environment $(ENV_VARS) --region $(AWS_REGION)
```

### Run The Application
Following make command can be used to request lambda function. You must provide a valid `API_URL`
```
invoke-par:
	@echo "Invoking in parallel..."
	@for i in {1..$(INVOKE_COUNT)}; do \
		curl --request POST \
			--url $(API_URL) \
			--header 'Content-Type: application/json' & \
	done; wait
```

### InitScope Visualizer with Live Profile Data
All the profiling data for the applications that InitScope optimizes are available here:
https://initscope.netlify.app/
