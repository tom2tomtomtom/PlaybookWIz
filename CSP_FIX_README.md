# 🔒 Content Security Policy (CSP) Fix - PlaybookWiz Intelligence System

## 🚨 Problem Solved

**Issue**: API key saving was failing with CSP error:
```
Refused to connect to 'http://localhost:8000/api/v1/auth/api-keys' because it violates the following Content Security Policy directive: "connect-src 'self' https:".
```

## ✅ Solution Implemented

### 1. **Updated Content Security Policy**
Modified `frontend/next.config.js` to allow localhost connections:
```javascript
{
  key: 'Content-Security-Policy',
  value: "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' http://localhost:8000 https://api.openai.com https://api.anthropic.com https://*.supabase.co wss://*.supabase.co; font-src 'self' data:; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none';"
}
```

### 2. **Environment Variable Configuration**
- **Frontend**: `frontend/.env.local`
  ```env
  NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
  NEXT_PUBLIC_SUPABASE_URL=your-supabase-url-here
  NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key-here
  ```

- **Backend**: `.env`
  ```env
  SUPABASE_URL=your-supabase-url-here
  SUPABASE_SERVICE_KEY=your-supabase-service-key-here
  ENCRYPTION_KEY=playbookwiz-32char-encryption-key
  ADMIN_SECRET=playbookwiz-admin-secret-2024
  ```

### 3. **Dynamic Backend URL**
Updated all frontend API calls to use environment variables:
```javascript
const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
await fetch(`${backendUrl}/api/v1/auth/api-keys`, { ... });
```

### 4. **Admin API Key Management**
Added admin endpoint to save API keys for users:
```bash
# Save API key for a user
python save_user_api_key.py
```

## 🚀 Quick Fix Instructions

### Option 1: Run the Fix Script
```bash
./fix_csp_and_setup.sh
```

### Option 2: Manual Steps

1. **Update environment files**:
   ```bash
   # Frontend
   echo "NEXT_PUBLIC_BACKEND_URL=http://localhost:8000" > frontend/.env.local
   
   # Backend (if needed)
   echo "ADMIN_SECRET=playbookwiz-admin-secret-2024" >> .env
   ```

2. **Rebuild frontend**:
   ```bash
   cd frontend
   npm run build
   cd ..
   ```

3. **Start services**:
   ```bash
   # Terminal 1: Backend
   ./start_backend.sh
   
   # Terminal 2: Frontend
   ./start_frontend.sh
   ```

## 🔑 API Key Management Options

### Option 1: Users Add Their Own Keys
1. Users go to Dashboard → API Key Configuration
2. Enter OpenAI or Claude API keys
3. Keys are encrypted and stored securely

### Option 2: Admin Saves Keys for Users
1. Run the admin script:
   ```bash
   python save_user_api_key.py
   ```
2. Enter user email and API key
3. Key is saved encrypted for that user

### Option 3: Bulk Save Keys
1. Set environment variables:
   ```bash
   export BULK_USERS="user1@example.com,user2@example.com"
   export OPENAI_API_KEY="sk-your-key"
   export ANTHROPIC_API_KEY="sk-ant-your-key"
   ```
2. Run bulk save:
   ```bash
   python save_user_api_key.py
   # Choose option 2 for bulk save
   ```

## 🧪 Testing the Fix

### 1. Test API Key Saving
1. Go to http://localhost:9000/dashboard
2. Enter an API key
3. Click "Save API Keys"
4. Should see "✓ API keys saved successfully!"

### 2. Test Intelligent Chat
1. Go to http://localhost:9000/chat
2. Upload a document first
3. Ask a question about the document
4. Should get response with sources and confidence

### 3. Test Document Upload
1. Go to http://localhost:9000/upload
2. Upload a PDF or PowerPoint
3. Should process successfully

## 🔍 Troubleshooting

### Still Getting CSP Errors?
1. **Clear browser cache** completely
2. **Hard refresh** (Ctrl+Shift+R or Cmd+Shift+R)
3. **Check browser console** for specific CSP violations
4. **Verify environment variables** are loaded correctly

### API Key Not Saving?
1. **Check backend logs** for authentication errors
2. **Verify Supabase credentials** in .env file
3. **Test admin endpoint** directly:
   ```bash
   curl -X POST http://localhost:8000/api/v1/admin/save-user-api-key \
     -H "Content-Type: application/json" \
     -d '{
       "user_email": "test@example.com",
       "provider": "openai", 
       "api_key": "sk-test",
       "admin_secret": "playbookwiz-admin-secret-2024"
     }'
   ```

### Frontend Not Loading?
1. **Check if frontend is built**:
   ```bash
   ls frontend/out/
   ```
2. **Rebuild if needed**:
   ```bash
   cd frontend && npm run build
   ```
3. **Check port 9000 is available**:
   ```bash
   lsof -i :9000
   ```

## 🎯 What's Fixed

✅ **CSP Policy**: Updated to allow localhost connections  
✅ **Environment Variables**: Proper configuration for all environments  
✅ **API Calls**: All frontend calls use dynamic backend URL  
✅ **Admin Management**: Script to save API keys for users  
✅ **Error Handling**: Better error messages and debugging  
✅ **Documentation**: Complete troubleshooting guide  

## 🌐 Production Deployment

For production, update the CSP to use your actual domain:
```javascript
connect-src 'self' https://your-backend-domain.com https://api.openai.com https://api.anthropic.com https://*.supabase.co wss://*.supabase.co
```

And set the production backend URL:
```env
NEXT_PUBLIC_BACKEND_URL=https://your-backend-domain.com
```

---

**🎉 Your PlaybookWiz Intelligence System is now fully functional with proper CSP configuration!**
