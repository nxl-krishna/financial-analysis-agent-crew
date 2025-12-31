# 1. Define the "Base Image" (The Foundation)
# We use the official AWS Lambda Python 3.12 image. 
# It comes pre-installed with the AWS "Run Time Interface" (RIC).
FROM public.ecr.aws/lambda/python:3.12

# 2. Copy the dependencies file
# We copy ONLY requirements.txt first to leverage "Docker Layer Caching"
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# 3. Install the libraries
# --no-cache-dir: Keeps the image small (don't save the pip cache)
# --target "${LAMBDA_TASK_ROOT}": Installs libs directly where Lambda expects them
RUN pip install --no-cache-dir -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# 4. Copy your actual code
# We do this LAST because code changes often, but dependencies change rarely.
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# 5. Define the "Entry Point"
# This tells AWS: "When triggered, look for the file 'lambda_function.py' 
# and call the function named 'lambda_handler'"
CMD [ "lambda_function.lambda_handler" ]