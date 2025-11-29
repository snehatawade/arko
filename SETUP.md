# Quick Setup Guide

## Prerequisites

- Python 3.9+ installed
- Node.js 16+ installed
- PostgreSQL installed and running

## Step 1: Database Setup

1. Create a PostgreSQL database:

```bash
createdb billwise
```

2. Or use the provided migration:

```bash
psql -U postgres -d billwise -f database/migrations.sql
```

## Step 2: Backend Setup

1. Navigate to backend directory:

```bash
cd backend
```

2. Create virtual environment:

```bash
python -m venv venv
```

3. Activate virtual environment:

- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Create `.env` file in backend directory:

```env
DATABASE_URL=postgresql://user:password@localhost/billwise
SECRET_KEY=your-secret-key-change-in-production-min-32-chars
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
```

6. Run backend:

```bash
python main.py
# Or
python run.py
# Or
uvicorn main:app --reload
```

Backend will be available at: http://localhost:8000

## Step 3: Frontend Setup

1. Navigate to frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Run frontend:

```bash
npm run dev
```

Frontend will be available at: http://localhost:3000

## Step 4: Test the Application

1. Open http://localhost:3000 in your browser
2. Sign up for a new account
3. Upload a CSV file with your bank transactions
4. View detected subscriptions on the dashboard
5. Check Harvey AI insights for recommendations

## CSV Format Example

Create a CSV file with the following format:

```csv
date,amount,description,bank_account
2024-01-15,-9.99,Netflix Subscription,Checking
2024-02-15,-9.99,Netflix Subscription,Checking
2024-03-15,-9.99,Netflix Subscription,Checking
2024-01-20,-14.99,Spotify Premium,Checking
2024-02-20,-14.99,Spotify Premium,Checking
```

The CSV parser is flexible and will try to detect columns automatically. Common column names:

- Date: `date`, `transaction_date`, `date_time`
- Amount: `amount`, `amt`, `value`
- Description: `description`, `desc`, `merchant`, `narration`
- Bank Account: `bank_account`, `account`, `bank` (optional)

## Troubleshooting

### Backend won't start

- Check PostgreSQL is running
- Verify DATABASE_URL in .env is correct
- Ensure all dependencies are installed

### Frontend won't connect to backend

- Verify backend is running on port 8000
- Check CORS settings in backend/main.py
- Verify API URL in frontend/src/services/api.js

### CSV upload fails

- Check CSV format matches expected columns
- Ensure date format is parseable (YYYY-MM-DD, MM/DD/YYYY, etc.)
- Verify amounts are numeric

### WhatsApp notifications not working

- Twilio credentials are optional - app works without them
- If using Twilio, verify credentials in .env
- Check phone number format (should include country code)

## Next Steps

- Configure Twilio for WhatsApp notifications (optional)
- Customize ML models in `backend/app/ml/detect.py`
- Add more bank statement formats in `backend/app/services/csv_parser.py`
- Customize Harvey AI insights in `backend/app/services/harvey.py`
