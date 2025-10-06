# 🗄️ Database Setup Guide - Price Regulation Monitoring System

## 🚨 **Current Issue: Database Connection Failed**

The deployment is failing because it's trying to connect to a PostgreSQL database at `localhost:5432`, but no database server is running.

## 🔧 **Solution Options**

### **Option 1: Use SQLite (Quick Start - No Setup Required)**

The application now automatically falls back to SQLite if no database environment variables are set. This is perfect for:
- ✅ **Quick testing and development**
- ✅ **Demo purposes**
- ✅ **Small-scale deployments**

**No action required** - the app will work out of the box!

### **Option 2: Use PostgreSQL (Production Recommended)**

For production use, you need to set up a PostgreSQL database and configure environment variables.

#### **2.1 Railway PostgreSQL (Recommended)**

1. **Create Railway Account**: Go to [railway.app](https://railway.app)
2. **Create New Project**: Click "New Project"
3. **Add PostgreSQL**: Click "New" → "Database" → "PostgreSQL"
4. **Get Connection Details**: Click on your database → "Connect" tab
5. **Set Environment Variables** in your deployment platform:

```bash
DB_NAME=railway
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=containers-us-west-xxx.railway.app
DB_PORT=5432
```

#### **2.2 Neon PostgreSQL (Alternative)**

1. **Create Neon Account**: Go to [neon.tech](https://neon.tech)
2. **Create New Project**: Click "Create Project"
3. **Get Connection String**: Copy the connection string
4. **Parse Connection String** and set environment variables:

```bash
# Example connection string:
# postgresql://username:password@host:port/database

DB_NAME=neondb
DB_USER=neondb_owner
DB_PASSWORD=your_password_here
DB_HOST=ep-xxx.us-east-1.aws.neon.tech
DB_PORT=5432
```

#### **2.3 Local PostgreSQL (Development)**

1. **Install PostgreSQL** on your system
2. **Create Database**:
   ```sql
   CREATE DATABASE price_monitoring;
   CREATE USER price_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE price_monitoring TO price_user;
   ```
3. **Set Environment Variables**:
   ```bash
   DB_NAME=price_monitoring
   DB_USER=price_user
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

## 🚀 **Deployment Instructions**

### **For Railpack Deployment:**

1. **Connect your repository** to Railpack
2. **Set environment variables** in Railpack dashboard:
   - Go to your project → Settings → Environment Variables
   - Add the database variables (if using PostgreSQL)
3. **Deploy** - the app will automatically:
   - Use SQLite if no database variables are set
   - Use PostgreSQL if database variables are provided

### **For Docker Deployment:**

```bash
# With SQLite (no database setup needed)
docker build -t price-monitoring .
docker run -p 8000:8000 price-monitoring

# With PostgreSQL
docker run -p 8000:8000 \
  -e DB_NAME=your_db_name \
  -e DB_USER=your_db_user \
  -e DB_PASSWORD=your_db_password \
  -e DB_HOST=your_db_host \
  -e DB_PORT=5432 \
  price-monitoring
```

### **For Manual Server Deployment:**

```bash
# Set environment variables
export DB_NAME=your_db_name
export DB_USER=your_db_user
export DB_PASSWORD=your_db_password
export DB_HOST=your_db_host
export DB_PORT=5432

# Run deployment script
bash deploy.sh
```

## 🔍 **Troubleshooting**

### **Database Connection Issues:**

1. **Check Environment Variables**:
   ```bash
   echo "DB_NAME: $DB_NAME"
   echo "DB_USER: $DB_USER"
   echo "DB_HOST: $DB_HOST"
   echo "DB_PORT: $DB_PORT"
   ```

2. **Test Database Connection**:
   ```bash
   # For PostgreSQL
   psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME
   
   # For SQLite
   sqlite3 db.sqlite3
   ```

3. **Check Network Connectivity**:
   ```bash
   # Test if database host is reachable
   ping $DB_HOST
   telnet $DB_HOST $DB_PORT
   ```

### **Common Error Messages:**

- **`Connection refused`**: Database server is not running or not accessible
- **`Authentication failed`**: Wrong username/password
- **`Database does not exist`**: Database name is incorrect
- **`Host not found`**: Database host is incorrect

## 📊 **Database Comparison**

| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| **Setup** | ✅ No setup required | ⚙️ Requires setup |
| **Performance** | 🟡 Good for small apps | ✅ Excellent for production |
| **Concurrency** | 🟡 Limited | ✅ High concurrency |
| **Scalability** | 🟡 Limited | ✅ Highly scalable |
| **Backup** | 🟡 File-based | ✅ Advanced backup tools |
| **Production Ready** | 🟡 Small scale only | ✅ Enterprise ready |

## 🎯 **Recommendation**

### **For Quick Testing/Demo:**
- ✅ **Use SQLite** - No setup required, works immediately

### **For Production:**
- ✅ **Use PostgreSQL** - Better performance, scalability, and features
- 🚀 **Railway PostgreSQL** - Easiest to set up and manage

## 🔧 **Next Steps**

1. **Choose your database option** (SQLite for quick start, PostgreSQL for production)
2. **Set up environment variables** (if using PostgreSQL)
3. **Deploy your application**
4. **Access admin panel** at `/admin/` with `admin@example.com` / `admin123`

Your application will now work correctly with either database configuration! 🚀
