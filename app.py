#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask S3 Gallery Application
معرض الصور باستخدام AWS S3
"""

import os
import boto3
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, Response
from werkzeug.utils import secure_filename
from botocore.exceptions import ClientError, NoCredentialsError
import uuid
import io
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

# Add CORS headers to help with cross-origin issues
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# AWS Configuration
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'my-gallery-bucket')

# Upload Configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_s3_client():
    """Initialize S3 client"""
    try:
        config = boto3.session.Config(
            signature_version='s3v4',
            s3={'addressing_style': 'virtual'}
        )
        
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION,
            config=config
        )
        return s3_client
    except Exception as e:
        print(f"Error initializing S3 client: {e}")
        return None

def generate_s3_url(bucket_name, key, use_presigned=False):
    """Generate S3 URL - serve through Flask to avoid CORS issues"""
    # Always serve through Flask to eliminate CORS/ORB issues
    try:
        # Try to use url_for if we have a request context
        return url_for('serve_image', filename=key, _external=True)
    except RuntimeError:
        # If no request context, return a relative URL that will work
        return f"/image/{key}"

def create_bucket_if_not_exists():
    """Create S3 bucket if it doesn't exist"""
    s3_client = get_s3_client()
    if not s3_client:
        return False
    
    try:
        # Check if bucket exists
        s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
        print(f"Bucket {S3_BUCKET_NAME} exists")
        return True
    except ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            # Bucket doesn't exist, create it
            try:
                if AWS_REGION == 'us-east-1':
                    s3_client.create_bucket(Bucket=S3_BUCKET_NAME)
                else:
                    s3_client.create_bucket(
                        Bucket=S3_BUCKET_NAME,
                        CreateBucketConfiguration={'LocationConstraint': AWS_REGION}
                    )
                print(f"Created bucket {S3_BUCKET_NAME}")
                return True
            except ClientError as create_error:
                print(f"Error creating bucket: {create_error}")
                return False
        else:
            print(f"Error checking bucket: {e}")
            return False

def upload_file_to_s3(file, filename):
    """Upload file to S3 bucket"""
    logging.info(f"Starting upload for file: {filename}")
    s3_client = get_s3_client()
    if not s3_client:
        logging.error("S3 client initialization failed")
        return False, "S3 client initialization failed"
    
    try:
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}_{secure_filename(filename)}"
        logging.info(f"Generated unique filename: {unique_filename}")
        
        # Upload file
        s3_client.upload_fileobj(
            file,
            S3_BUCKET_NAME,
            unique_filename,
            ExtraArgs={
                'ContentType': 'image/' + filename.rsplit('.', 1)[1].lower()
            }
        )
        
        logging.info(f"File uploaded successfully: {unique_filename}")
        # Return success with the filename (don't generate URL during upload)
        return True, unique_filename
    
    except ClientError as e:
        logging.error(f"Upload failed with ClientError: {e}")
        return False, f"Upload failed: {e}"
    except Exception as e:
        logging.error(f"Upload failed with unexpected error: {e}")
        return False, f"Unexpected error: {e}"

def list_s3_images():
    """List all images in S3 bucket"""
    s3_client = get_s3_client()
    if not s3_client:
        return []
    
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME)
        images = []
        
        if 'Contents' in response:
            for obj in response['Contents']:
                # Only include image files
                filename = obj['Key']
                if any(filename.lower().endswith(ext) for ext in ['png', 'jpg', 'jpeg', 'gif', 'webp']):
                    # Generate S3 URL (serve through Flask to avoid CORS issues)
                    image_url = generate_s3_url(S3_BUCKET_NAME, filename)
                    
                    images.append({
                        'filename': filename,
                        'url': image_url,
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        return images
    
    except ClientError as e:
        print(f"Error listing images: {e}")
        return []

@app.route('/')
def index():
    """Main gallery page"""
    images = list_s3_images()
    return render_template('index.html', images=images)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Upload page"""
    if request.method == 'POST':
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        # Check file type
        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload PNG, JPG, JPEG, GIF, or WebP files.', 'error')
            return redirect(request.url)
        
        # Check file size
        file.seek(0, 2)  # Seek to end of file
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > MAX_FILE_SIZE:
            flash('File too large. Maximum size is 16MB.', 'error')
            return redirect(request.url)
        
        # Upload to S3
        try:
            success, result = upload_file_to_s3(file, file.filename)
            
            if success:
                flash(f'File uploaded successfully!', 'success')
                return redirect(url_for('index'))
            else:
                flash(f'Upload failed: {result}', 'error')
                return redirect(request.url)
        except Exception as e:
            print(f"Upload error: {e}")
            flash(f'Upload error: {str(e)}', 'error')
            return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/image/<path:filename>')
def serve_image(filename):
    """Serve images from S3 through Flask to avoid CORS issues"""
    s3_client = get_s3_client()
    if not s3_client:
        return "S3 client error", 500
    
    try:
        # Download image from S3
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=filename)
        
        # Get content type
        content_type = response.get('ContentType', 'image/jpeg')
        
        # Stream the image
        image_data = response['Body'].read()
        
        return Response(
            image_data,
            mimetype=content_type,
            headers={
                'Cache-Control': 'public, max-age=3600',  # Cache for 1 hour
                'Access-Control-Allow-Origin': '*'
            }
        )
        
    except ClientError as e:
        print(f"Error serving image {filename}: {e}")
        return "Image not found", 404
    except Exception as e:
        print(f"Unexpected error serving image {filename}: {e}")
        return "Server error", 500

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        s3_client = get_s3_client()
        if s3_client:
            # Test S3 connection
            s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, MaxKeys=1)
            return jsonify({
                'status': 'healthy',
                'message': 'Application and S3 connection working',
                'bucket': S3_BUCKET_NAME
            }), 200
        else:
            return jsonify({
                'status': 'unhealthy',
                'message': 'S3 client initialization failed'
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'message': f'Health check failed: {str(e)}'
        }), 500

@app.route('/info')
def app_info():
    """Application information endpoint"""
    return jsonify({
        'app_name': 'Flask S3 Gallery',
        'version': '1.0.0',
        'bucket': S3_BUCKET_NAME,
        'region': AWS_REGION,
        'allowed_extensions': list(ALLOWED_EXTENSIONS),
        'max_file_size_mb': MAX_FILE_SIZE // (1024 * 1024)
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Initialize bucket
    create_bucket_if_not_exists()
    
    # Run app
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )