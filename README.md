# Price Regulation Monitoring System

A comprehensive platform for government price regulation monitoring and enforcement, built with Django REST Framework and Next.js.

## 🚀 Features

### Core Functionality
- **Product Management**: Register and manage government-regulated products with official prices
- **Web Scraping**: Automated scraping of ecommerce sites to monitor actual market prices
- **Violation Detection**: Automatic comparison of scraped prices with government regulations
- **Case Management**: Investigation workflow for confirmed violations
- **Multi-Session Support**: Track user sessions across multiple devices
- **Role-Based Access**: Admin, Investigator, and Regulator dashboards

### User Roles
- **Admin**: Manage products, trigger scraping jobs, oversee system operations
- **Investigator**: Review violations, confirm/dismiss cases, manage investigation workflow
- **Regulator**: View analytics, generate reports, monitor compliance metrics

## 🏗️ Architecture

### Backend (Django)
- **Framework**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT with refresh tokens
- **Task Queue**: Celery + Redis
- **Session Management**: Database-tracked multi-session support

### Frontend (Next.js)
- **Framework**: Next.js 14 with App Router
- **Styling**: TailwindCSS
- **State Management**: React Query (TanStack Query)
- **Authentication**: JWT in HttpOnly cookies
- **Charts**: Recharts for data visualization

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 13+
- Redis 6+
- Docker & Docker Compose (optional)

## 🚀 Quick Start Options

### Option 1: Docker with Local PostgreSQL
```bash
git clone <repository-url>
cd price-regulation-monitoring-system
docker-compose up -d
```

### Option 2: Docker with Neon Database (Recommended)
```bash
git clone <repository-url>
cd price-regulation-monitoring-system
chmod +x setup-neon.sh
./setup-neon.sh
```

### Option 3: Manual Setup
Follow the detailed instructions in the [Manual Setup](#-manual-setup) section below.

## 🌟 Neon Database Setup (Recommended)

For the best experience, we recommend using **Neon Database** (serverless PostgreSQL):

1. **Sign up for Neon**: https://neon.tech/
2. **Get connection details** from your Neon dashboard
3. **Run the setup script**:
   ```bash
   ./setup-neon.sh
   ```
4. **Follow the prompts** to configure your Neon credentials

📖 **Detailed Neon setup guide**: [NEON_SETUP_GUIDE.md](NEON_SETUP_GUIDE.md)

## 🛠️ Manual Setup

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**
   ```bash
   cp env.example .env
   # Edit .env with your database and Redis settings
   ```

5. **Database setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Start services**
   ```bash
   # Terminal 1: Django server
   python manage.py runserver

   # Terminal 2: Celery worker
   celery -A price_monitoring worker --loglevel=info

   # Terminal 3: Celery beat (optional)
   celery -A price_monitoring beat --loglevel=info
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Environment configuration**
   ```bash
   cp env.local.example .env.local
   # Edit .env.local with your API URL
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

## 👥 Demo Users

The system comes with demo users for testing:

- **Admin**: admin@example.com / admin123
- **Investigator**: investigator@example.com / investigator123
- **Regulator**: regulator@example.com / regulator123

## 📊 API Endpoints

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/refresh/` - Refresh token
- `GET /api/auth/me/` - Get current user

### Products
- `GET /api/products/` - List regulated products
- `POST /api/products/` - Create product (Admin only)
- `PUT /api/products/{id}/` - Update product (Admin only)
- `DELETE /api/products/{id}/` - Delete product (Admin only)

### Violations
- `GET /api/violations/` - List violations
- `POST /api/violations/{id}/confirm/` - Confirm violation (Investigator)
- `POST /api/violations/{id}/dismiss/` - Dismiss violation (Investigator)

### Cases
- `GET /api/cases/` - List cases
- `POST /api/cases/` - Create case
- `PUT /api/cases/{id}/` - Update case
- `POST /api/cases/{id}/close/` - Close case

### Scraping
- `GET /api/scraping/results/` - List scraped products
- `POST /api/scraping/trigger/` - Trigger scraping job (Admin)
- `GET /api/scraping/jobs/` - List scraping jobs

### Reports
- `GET /api/reports/summary/` - Get summary report
- `GET /api/reports/export/` - Export data (CSV)
- `GET /api/reports/dashboard-metrics/` - Dashboard metrics

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=price_monitoring_db
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
python manage.py test
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📈 Monitoring

### Celery Monitoring
- Use Flower for Celery monitoring: `pip install flower && celery -A price_monitoring flower`

### Database Monitoring
- Access PostgreSQL logs through Docker: `docker-compose logs db`

## 🚀 Deployment

### Production Deployment

1. **Update environment variables for production**
2. **Set DEBUG=False**
3. **Use production database and Redis**
4. **Configure proper CORS origins**
5. **Set up SSL certificates**
6. **Use a production WSGI server (Gunicorn)**

### Docker Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the API endpoints

## 🔄 Workflow

1. **Admin** uploads regulated products with government prices
2. **System** automatically scrapes ecommerce sites for current prices
3. **System** compares prices and creates violations for overpriced items
4. **Investigator** reviews violations and confirms/dismisses them
5. **System** creates cases for confirmed violations
6. **Investigator** manages cases through investigation workflow
7. **Regulator** monitors compliance through dashboards and reports

## 🎯 Future Enhancements

- Real-time notifications
- Advanced analytics and ML predictions
- Mobile app support
- Integration with more ecommerce platforms
- Automated penalty calculation
- Email/SMS notifications
- Advanced reporting features
