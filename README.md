# Arko - AI-Powered Subscription Management

Arko is an intelligent subscription management platform that identifies recurring subscriptions from bank CSV statements, provides AI insights using the agent Harvey, and sends proactive WhatsApp alerts for renewals, price hikes, and unusual activity.

## 🚀 Features

- **Authentication**: Secure signup, login, and JWT-based session handling
- **CSV Upload**: Upload bank statements and automatically detect subscriptions
- **Subscription Management**: View and manage all your subscriptions in one place
- **Harvey AI Insights**: Get AI-powered recommendations for cancellation, savings, and anomalies
- **WhatsApp Notifications**: Receive alerts for renewals, price increases, and recommendations
- **Profile Management**: Manage your account settings and view upload history

## 🛠️ Tech Stack

### Backend

- **FastAPI** (Python) - High-performance web framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **scikit-learn** - ML models for subscription detection
- **Twilio** - WhatsApp notifications
- **JWT** - Authentication

### Frontend

- **React** - UI library
- **Tailwind CSS** - Styling
- **React Router** - Navigation
- **Axios** - API client

## 📁 Project Structure

```
billHarvester/
├── backend/
│   ├── app/
│   │   ├── routes/          # API endpoints
│   │   ├── models.py        # Database models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── auth.py          # Authentication utilities
│   │   ├── database.py      # Database connection
│   │   ├── services/        # Business logic
│   │   │   ├── harvey.py    # AI insights service
│   │   │   ├── notifications.py  # WhatsApp service
│   │   │   └── csv_parser.py     # CSV parsing
│   │   └── ml/              # ML models
│   │       ├── detect.py    # Subscription detection
│   │       └── preprocess.py # Data preprocessing
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuration
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   └── App.jsx          # Main app component
│   └── package.json         # Node dependencies
└── database/
    └── migrations.sql       # Database schema
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL
- Twilio account (for WhatsApp notifications - optional)

### Backend Setup

1. **Navigate to backend directory:**

   ```bash
   cd backend
   ```

2. **Create virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database:**

   ```bash
   # Create database
   createdb billwise

   # Or use the migration file
   psql -U postgres -f ../database/migrations.sql
   ```

5. **Configure environment variables:**
   Create a `.env` file in the backend directory:

   ```env
   DATABASE_URL=postgresql://user:password@localhost/billwise
   SECRET_KEY=your-secret-key-change-in-production
   TWILIO_ACCOUNT_SID=your-twilio-account-sid
   TWILIO_AUTH_TOKEN=your-twilio-auth-token
   ```

6. **Run the backend:**

   ```bash
   python main.py
   # Or
   uvicorn main:app --reload
   ```

   Backend will run on `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**

   ```bash
   cd frontend
   ```

2. **Install dependencies:**

   ```bash
   npm install
   ```

3. **Run the frontend:**

   ```bash
   npm run dev
   ```

   Frontend will run on `http://localhost:3000`

## 📡 API Endpoints

### Authentication

- `POST /auth/signup` - Create new account
- `POST /auth/login` - Login
- `POST /auth/logout` - Logout

### Upload

- `POST /upload/csv` - Upload bank statement CSV

### Subscriptions

- `GET /subscriptions` - Get all subscriptions
- `GET /subscriptions/{id}` - Get subscription details
- `PATCH /subscriptions/{id}/cancel` - Cancel subscription

### Harvey AI

- `GET /harvey/recommendations` - Get AI recommendations
- `GET /harvey/savings` - Get savings calculations
- `GET /harvey/anomalies` - Get detected anomalies

### Profile

- `GET /profile` - Get user profile
- `PATCH /profile` - Update profile
- `DELETE /profile` - Delete account
- `GET /profile/csv-history` - Get upload history

### Notifications

- `POST /notify/whatsapp` - Send WhatsApp message

## 📊 CSV Format

The CSV upload expects the following columns (case-insensitive):

- `date` - Transaction date
- `amount` - Transaction amount
- `description` - Transaction description/merchant name
- `bank_account` (optional) - Bank account identifier

Example:

```csv
date,amount,description,bank_account
2024-01-15,-9.99,Netflix Subscription,Checking
2024-02-15,-9.99,Netflix Subscription,Checking
```

## 🤖 Harvey AI Features

Harvey provides:

- **Low-usage detection**: Identifies subscriptions with minimal usage
- **Cancellation recommendations**: Suggests subscriptions to cancel
- **Price increase alerts**: Detects when subscription prices increase
- **Savings calculations**: Estimates potential savings
- **Anomaly detection**: Flags unusual transactions
- **Churn prediction**: Predicts subscription cancellation probability

## 📱 WhatsApp Notifications

Configure Twilio credentials in `.env` to enable WhatsApp notifications. Notifications are sent for:

- New subscription detected
- Upcoming renewal (24 hours before)
- Price increase detected
- Unusual activity
- Harvey recommendations

## 🔒 Security

- Passwords are hashed using bcrypt
- JWT tokens for authentication
- CORS configured for frontend
- SQL injection protection via SQLAlchemy

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
