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
    Gaming platform API handler with security improvements
    """
    try:
        # Log the request for security monitoring
        logger.info(f"Lambda invoked with event: {json.dumps(event, default=str)}")
        
        # Get user identity from event context (API Gateway integration)
        user_id = event.get('requestContext', {}).get('authorizer', {}).get('principalId', 'anonymous')
        
        # Validate request method and path
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        
        # Basic routing for gaming platform APIs
        if path == '/health':
            return create_response(200, {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})
        
        elif path == '/gaming/instances' and http_method == 'GET':
            return list_gaming_instances(user_id)
        
        elif path == '/gaming/instances' and http_method == 'POST':
            return create_gaming_instance(event, user_id)
        
        elif path.startswith('/gaming/instances/') and http_method == 'PUT':
            instance_id = path.split('/')[-1]
            return manage_gaming_instance(event, instance_id, user_id)
        
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
            'Access-Control-Allow-Headers': 'Content-Type,Authorization'
        }
    }

def list_gaming_instances(user_id):
    """List gaming instances for user"""
    # This would connect to database with proper parameterized queries
    # Example of secure database query structure:
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # SECURE: Parameterized query prevents SQL injection
        query = '''
            SELECT instance_id, instance_type, status, created_at, last_accessed
            FROM gaming_instances 
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
        'instances': [],
        'message': 'No active gaming instances found'
    })

def create_gaming_instance(event, user_id):
    """Create new gaming instance for user"""
    try:
        body = json.loads(event.get('body', '{}'))
        instance_type = body.get('instance_type', 'g4dn.xlarge')  # Default gaming instance
        
        # Validate instance type against allowed list
        allowed_instances = ['g4dn.xlarge', 'g4dn.2xlarge', 'g5.xlarge']
        if instance_type not in allowed_instances:
            return create_response(400, {'error': 'Invalid instance type'})
        
        # Mock EC2 instance creation (would use boto3 EC2 client)
        ec2_client = boto3.client('ec2')
        
        # This would create the actual instance with proper security groups
        mock_response = {
            'instance_id': 'i-gaming-' + datetime.now().strftime('%Y%m%d%H%M%S'),
            'instance_type': instance_type,
            'status': 'launching',
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat()
        }
        
        return create_response(201, mock_response)
        
    except json.JSONDecodeError:
        return create_response(400, {'error': 'Invalid JSON in request body'})
    except Exception as e:
        logger.error(f"Instance creation error: {str(e)}")
        return create_response(500, {'error': 'Failed to create instance'})

def manage_gaming_instance(event, instance_id, user_id):
    """Start, stop, or terminate gaming instance"""
    try:
        body = json.loads(event.get('body', '{}'))
        action = body.get('action')
        
        if action not in ['start', 'stop', 'terminate']:
            return create_response(400, {'error': 'Invalid action'})
        
        # Verify user owns this instance (security check)
        # This would query database to verify ownership
        
        # Mock response
        return create_response(200, {
            'instance_id': instance_id,
            'action': action,
            'status': 'pending',
            'user_id': user_id
        })
        
    except json.JSONDecodeError:
        return create_response(400, {'error': 'Invalid JSON in request body'})
    except Exception as e:
        logger.error(f"Instance management error: {str(e)}")
        return create_response(500, {'error': 'Failed to manage instance'})

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
        password=os.environ['DB_PASS'],
        sslmode='require'  # Enforce SSL
    )
    """