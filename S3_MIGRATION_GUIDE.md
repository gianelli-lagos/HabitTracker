# S3 Migration Guide - Profile Pictures

## Changes Made

Your application has been updated to properly use S3 for profile picture storage instead of local filesystem. Here are the changes:

### 1. **main.py** - Removed Local Upload Mounting
- **Removed**: `StaticFiles` import and mounting of `/uploads` directory
- **Why**: This was serving files from the local filesystem. Now all profile pictures are served from S3 via presigned URLs.
- **Impact**: `/uploads/` endpoints will no longer work. All images now come from S3.

### 2. **routers/users.py** - Enhanced Upload Endpoint
- **Added**: Comprehensive logging to track S3 uploads
- **Improved**: Error messages and debugging information
- **Endpoint**: `POST /users/upload-profile-picture`
- **Returns**: S3 presigned URL that's valid for 1 hour

### 3. **services/s3_service.py** - Added Logging
- **upload_profile_picture()**: Logs file size, S3 path, and presigned URL
- **delete_profile_picture()**: Logs deletion operations
- **get_profile_picture_url()**: Logs URL generation
- **Initialization**: Logs S3 configuration and validates environment variables

### 4. **Environment Variables** (Already Configured ✅)
```
S3_BUCKET_NAME=habittracker-profiles
S3_REGION=us-east-2
AWS_ACCESS_KEY_ID=***
AWS_SECRET_ACCESS_KEY=***
```

## Deployment Steps

### Step 1: Rebuild Docker Image
```bash
cd c:\Users\lacue\Documents\GitHub\HabitTracker
docker-compose build
```

### Step 2: Deploy Updated Application
```bash
docker-compose up -d
```

### Step 3: Test S3 Upload
```bash
# 1. Get an authentication token (login)
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"your_username","password":"your_password"}'

# 2. Upload a profile picture (replace TOKEN with actual JWT token)
curl -X POST "http://localhost:8000/users/upload-profile-picture" \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@/path/to/image.jpg"

# Expected response:
# {
#   "profile_picture_url": "https://habittracker-profiles.s3.us-east-2.amazonaws.com/profile-pictures/USER_ID.jpg?AWSAccessKeyId=...",
#   "message": "Profile picture uploaded successfully to S3"
# }
```

### Step 4: Check Logs for S3 Operations
```bash
# View application logs
docker-compose logs backend

# Look for these log entries:
# "S3 Configuration - Bucket: habittracker-profiles, Region: us-east-2"
# "S3 client initialized successfully"
# "Starting profile picture upload for user XXX"
# "File uploaded successfully to S3: profile-pictures/XXX.jpg"
# "S3 upload successful. Presigned URL: https://..."
```

### Step 5: Verify in S3 Console
1. Go to [AWS S3 Console](https://console.aws.amazon.com/s3)
2. Select `habittracker-profiles` bucket
3. Navigate to `profile-pictures/` folder
4. You should see uploaded images with filenames like `1.jpg`, `2.jpg`, etc.

## What Changed For Users

- **Old behavior**: `GET /uploads/9_cat.jpg` → served from local filesystem
- **New behavior**: Profile pictures are automatically served from S3 via presigned URLs
- **URL format**: `https://habittracker-profiles.s3.us-east-2.amazonaws.com/profile-pictures/USER_ID.EXT?AWSAccessKeyId=...`

## Database Considerations

The `profile_picture_url` field in the User model now stores the value `"s3"` (a marker). The actual URL is generated on-demand when the profile picture is retrieved via:
- `GET /users/{user_id}` - Returns a fresh presigned URL valid for 1 hour
- Presigned URLs expire after 1 hour for security

## Troubleshooting

### Issue: "S3_BUCKET_NAME environment variable is not set!"
**Solution**: Ensure `backend/.env` file exists with all S3 variables

### Issue: Upload returns 500 error
**Check logs for**:
- `ClientError during S3 upload` - AWS credentials issue
- `Failed to upload to S3` - Permission or bucket issue
- Run: `docker-compose logs backend` to see full error

### Issue: Image still showing from `/uploads/`
**This should not happen anymore because**:
1. The static mount is removed
2. Frontend should receive S3 URLs from the API
3. Clear browser cache if you see old URLs

### Issue: Presigned URL gives "Access Denied"
**Causes**:
- AWS credentials in `.env` are incorrect/expired
- S3 bucket name is wrong
- AWS user doesn't have S3 permissions

**Solution**: 
- Verify credentials in `backend/.env`
- Check [AWS IAM Console](https://console.aws.amazon.com/iam) for user permissions

## Verification Checklist

- [ ] Docker image rebuilt
- [ ] Application redeployed
- [ ] Logs show "S3 client initialized successfully"
- [ ] Profile picture upload returns S3 URL (not `/uploads/` path)
- [ ] S3 URL works in browser
- [ ] File visible in S3 Console
- [ ] Frontend displays profile picture from S3 URL

## Next Steps (If Issues Persist)

1. **Check Docker logs**: `docker-compose logs backend | grep -E "S3|profile|upload"`
2. **Verify AWS credentials**: Ensure IAM user has `s3:*` permissions on `habittracker-profiles` bucket
3. **Test S3 connection**: Run the included test file:
   ```bash
   docker-compose exec backend python test_s3_connection.py
   ```

## Important Notes

- ✅ All S3 credentials are already configured
- ✅ Logging is now comprehensive for debugging
- ✅ Local `/uploads/` directory is no longer used
- ⚠️ Old profile pictures in local `/uploads/` will not be accessible
- ⚠️ If you need to migrate old profile pictures to S3, they need to be re-uploaded

---

If you encounter any issues after deployment, the detailed logs will help identify exactly where the problem is. All three S3 functions now include comprehensive logging for debugging.
