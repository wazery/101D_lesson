# ORB Error Troubleshooting Guide

## Problem: ERR_BLOCKED_BY_ORB Error

When you see this error:
```
(failed)net::ERR_BLOCKED_BY_ORB
```

This happens when browsers block cross-origin requests to S3 due to Opaque Response Blocking (ORB) security policy.

## ✅ Solution 1: Flask Image Proxy (RECOMMENDED)

**This is the approach we use in our application.**

Serve images through your Flask application instead of directly from S3:

### How it works:
1. Flask route `/image/<filename>` fetches images from S3
2. Flask serves the image with proper headers
3. No CORS issues since images come from same origin

### Benefits:
- ✅ Eliminates CORS/ORB issues completely
- ✅ No S3 bucket policy changes needed
- ✅ Works with private S3 buckets
- ✅ Simple to implement
- ✅ Better security control

### Code Implementation:
```python
@app.route('/image/<path:filename>')
def serve_image(filename):
    """Serve images from S3 through Flask to avoid CORS issues"""
    s3_client = get_s3_client()
    if not s3_client:
        return "S3 client error", 500
    
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=filename)
        content_type = response.get('ContentType', 'image/jpeg')
        image_data = response['Body'].read()
        
        return Response(
            image_data,
            mimetype=content_type,
            headers={
                'Cache-Control': 'public, max-age=3600',
                'Access-Control-Allow-Origin': '*'
            }
        )
    except ClientError as e:
        return "Image not found", 404

def generate_s3_url(bucket_name, key, use_presigned=False):
    """Generate S3 URL - serve through Flask to avoid CORS issues"""
    return url_for('serve_image', filename=key, _external=True)
```

## Alternative Solutions (if needed)

### Solution 2: Presigned URLs

Use presigned URLs with proper expiration:

```python
def generate_presigned_url(bucket_name, key):
    s3_client = get_s3_client()
    return s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': key},
        ExpiresIn=3600  # 1 hour
    )
```

### Solution 3: S3 CORS Configuration

Add CORS policy to your S3 bucket:

```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": [],
        "MaxAgeSeconds": 3000
    }
]
```

### Solution 4: S3 Bucket Policy

Make bucket objects publicly readable:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::your-bucket-name/*"
        }
    ]
}
```

## Testing the Fix

1. **Deploy the updated code:**
   ```bash
   git add .
   git commit -m "Fix ORB errors with Flask image proxy"
   git push
   ```

2. **Upload a test image**

3. **Check browser console** - should see no ORB errors

4. **Verify image URLs** - should be like:
   ```
   https://your-app.onrender.com/image/filename.jpg
   ```

## Why Flask Proxy Works

- **Same Origin**: Images served from same domain as app
- **No CORS**: Browser doesn't treat as cross-origin request
- **Security**: Full control over access and caching
- **Performance**: Can add caching headers and compression

This approach is production-ready and eliminates all CORS/ORB related issues! 🎉