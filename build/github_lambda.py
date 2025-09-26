import json
import os
import logging
import boto3
from datetime import datetime, timedelta
# import psycopg2
# import psycopg2.extras

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Basic EC2 deployment platform API handler
    This is a learning/development implementation for web application management
    """
    try:
        # Log the request for security monitoring
        logger.info(f"Lambda invoked with event: {json.dumps(event, default=str)}")
        
        # Get user identity from event context (API Gateway integration)
        user_id = event.get('requestContext', {}).get('authorizer', {}).get('principalId', 'anonymous')
        
        # Validate request method and path
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        
        # Basic routing for web application management APIs
        if path == '/health':
            return create_response(200, {
                'status': 'healthy', 
                'timestamp': datetime.utcnow().isoformat(),
                'platform': 'EC2 Deployment Automation',
                'version': '1.0.0'
            })
        
        elif path == '/web/instances' and http_method == 'GET':
            return list_web_instances(user_id)
        
        elif path == '/web/instances' and http_method == 'POST':
            return create_web_instance(event, user_id)
        
        elif path.startswith('/web/instances/') and http_method == 'PUT':
            instance_id = path.split('/')[-1]
            return manage_web_instance(event, instance_id, user_id)
        
        elif path == '/web/applications' and http_method == 'GET':
            return list_web_applications(user_id)
            
        else:
            return create_response(404, {'error': 'Endpoint not found'})
            
    except Exception as e:
        logger.error(f"Lambda error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

def create_response(status_code, body):
    """Create standardized API response"""
    return {
        'statusCode': status_code,
        'body': json.dumps(body),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  # Configure properly for production
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'X-Platform': 'EC2-Deployment-Automation'
        }
    }

def list_web_instances(user_id):
    """List web server instances for user"""
    # This would connect to database with proper parameterized queries
    # Example of secure database query structure:
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # SECURE: Parameterized query prevents SQL injection
        query = '''
            SELECT instance_id, instance_type, status, created_at, last_accessed, application_name
            FROM web_instances 
            WHERE user_id = %s AND status != 'terminated'
            ORDER BY created_at DESC
        '''
        cursor.execute(query, (user_id,))
        instances = cursor.fetchall()
        
        return create_response(200, {
            'instances': [dict(instance) for instance in instances]
        })
        
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        return create_response(500, {'error': 'Database error'})
    finally:
        if 'conn' in locals():
            conn.close()
    """
    
    # Mock response for now
    return create_response(200, {
        'instances': [
            {
                'instance_id': 'i-web-12345',
                'instance_type': 't3.micro',
                'status': 'running',
                'application': 'Apache Web Server',
                'availability_zone': 'us-east-1a',
                'public_ip': '54.123.45.67',
                'created_at': '2024-09-26T10:00:00Z'
            },
            {
                'instance_id': 'i-web-67890',
                'instance_type': 't3.micro', 
                'status': 'running',
                'application': 'Apache Web Server',
                'availability_zone': 'us-east-1b',
                'public_ip': '54.123.45.68',
                'created_at': '2024-09-26T10:05:00Z'
            }
        ],
        'message': 'Web server instances retrieved successfully'
    })

def create_web_instance(event, user_id):
    """Create new web server instance for user"""
    try:
        body = json.loads(event.get('body', '{}'))
        instance_type = body.get('instance_type', 't3.micro')  # Default web server instance
        application = body.get('application', 'apache')
        
        # Validate instance type against allowed list
        allowed_instances = ['t3.micro', 't3.small', 't3.medium']
        if instance_type not in allowed_instances:
            return create_response(400, {'error': 'Invalid instance type'})
        
        # Validate application type
        allowed_applications = ['apache', 'nginx', 'nodejs', 'python-flask']
        if application not in allowed_applications:
            return create_response(400, {'error': 'Invalid application type'})
        
        # Mock EC2 instance creation (would use boto3 EC2 client)
        ec2_client = boto3.client('ec2')
        
        # This would create the actual web server instance
        mock_response = {
            'instance_id': 'i-web-' + datetime.now().strftime('%Y%m%d%H%M%S'),
            'instance_type': instance_type,
            'application': application,
            'status': 'launching',
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'estimated_ready_time': (datetime.utcnow() + timedelta(minutes=5)).isoformat()
        }
        
        return create_response(201, mock_response)
        
    except json.JSONDecodeError:
        return create_response(400, {'error': 'Invalid JSON in request body'})
    except Exception as e:
        logger.error(f"Instance creation error: {str(e)}")
        return create_response(500, {'error': 'Failed to create web server instance'})

def manage_web_instance(event, instance_id, user_id):
    """Start, stop, restart, or terminate web server instance"""
    try:
        body = json.loads(event.get('body', '{}'))
        action = body.get('action')
        
        if action not in ['start', 'stop', 'restart', 'terminate']:
            return create_response(400, {'error': 'Invalid action'})
        
        # Verify user owns this instance (security check)
        # This would query database to verify ownership
        
        # Mock response
        return create_response(200, {
            'instance_id': instance_id,
            'action': action,
            'status': 'pending',
            'user_id': user_id,
            'message': f'Web server instance {action} initiated successfully'
        })
        
    except json.JSONDecodeError:
        return create_response(400, {'error': 'Invalid JSON in request body'})
    except Exception as e:
        logger.error(f"Instance management error: {str(e)}")
        return create_response(500, {'error': 'Failed to manage web server instance'})

def list_web_applications(user_id):
    """List deployed web applications"""
    # Mock response showing web applications running on the platform
    return create_response(200, {
        'applications': [
            {
                'name': 'Demo Website',
                'url': 'http://alb-dns-name/',
                'status': 'active',
                'instances': ['i-web-12345', 'i-web-67890'],
                'health_check': 'passing'
            },
            {
                'name': 'API Service',
                'url': 'http://alb-dns-name/api/',
                'status': 'active', 
                'instances': ['i-web-12345'],
                'health_check': 'passing'
            }
        ],
        'total_applications': 2,
        'load_balancer': {
            'dns_name': 'example-alb-123456789.us-east-1.elb.amazonaws.com',
            'status': 'active'
        }
    })

def get_db_connection():
    """Get secure database connection with environment variables"""
    return None  # Placeholder
    """
    # Secure database connection using environment variables
    return psycopg2.connect(
        host=os.environ['DB_HOST'],
        port=os.environ.get('DB_PORT', 5432),
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        ******'DB_PASS'],
        sslmode='require'  # Enforce SSL
    )
    """