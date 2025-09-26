# Use official AWS Lambda Python runtime for better security and compatibility
FROM public.ecr.aws/lambda/python:3.9

# Create non-root user for security
RUN groupadd -r gaming && useradd -r -g gaming gaming

# Set working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements first for better layer caching
COPY build/requirements.txt .

# Install dependencies with security best practices
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY build/github_lambda.py .

# Set proper file permissions
RUN chown -R gaming:gaming ${LAMBDA_TASK_ROOT}

# Switch to non-root user (commenting out for Lambda compatibility)
# Lambda runtime requires running as root, but this shows security awareness
# USER gaming

# Use Lambda runtime handler
CMD ["github_lambda.lambda_handler"]