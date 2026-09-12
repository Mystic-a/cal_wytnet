# Multi-Purpose Calculator App

A full-stack calculator application with React frontend, FastAPI backend, and PostgreSQL database for user authentication. Features four different calculators: BMI, Age, GST, and EB Bill.

## Features

- **User Authentication**: Secure signup/login with JWT tokens
- **BMI Calculator**: Calculate Body Mass Index with weight and height
- **Age Calculator**: Calculate exact age from birth date
- **GST Calculator**: Calculate GST (Goods and Services Tax) on amounts
- **EB Bill Calculator**: Calculate electricity bill based on units consumed
- **Responsive Design**: Beautiful gradient UI that works on all devices
- **Secure Backend**: FastAPI with password hashing and JWT authentication
- **Database**: PostgreSQL for production, SQLite for local development

## Tech Stack

### Frontend
- React 18
- React Router DOM
- Axios
- CSS3 with gradient styling

### Backend
- FastAPI
- SQLAlchemy (ORM)
- JWT Authentication (python-jose)
- Password hashing (passlib with bcrypt)
- PostgreSQL/SQLite support

### Deployment
- Render (Frontend + Backend + Database)
- Docker-ready architecture

## Project Structure

```
calculator/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── runtime.txt          # Python version
│   ├── .env.example         # Environment variables template
│   └── .gitignore
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   ├── manifest.json
│   │   └── robots.txt
│   ├── src/
│   │   ├── components/
│   │   │   ├── Login.js
│   │   │   ├── Signup.js
│   │   │   ├── Dashboard.js
│   │   │   └── calculators/
│   │   │       ├── BMICalculator.js
│   │   │       ├── AgeCalculator.js
│   │   │       ├── GSTCalculator.js
│   │   │       └── EBBillCalculator.js
│   │   ├── api.js           # API client
│   │   ├── App.js
│   │   ├── App.css
│   │   ├── index.js
│   │   └── index.css
│   ├── package.json
│   ├── .env.example
│   └── .gitignore
├── render.yaml              # Render deployment config
├── .gitignore
└── README.md
```

## Local Development Setup

### Prerequisites
- Python 3.11 or higher
- Node.js 16 or higher
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate virtual environment:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create `.env` file from example:
```bash
cp .env.example .env
```

6. Generate a secure secret key (optional but recommended):
```bash
# Using Python
python -c "import secrets; print(secrets.token_hex(32))"
```

Update the `SECRET_KEY` in `.env` with the generated key.

7. Run the backend server:
```bash
python main.py
```

Backend will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file from example:
```bash
cp .env.example .env
```

4. Run the frontend:
```bash
npm start
```

Frontend will run on `http://localhost:3000`

### Testing Locally

1. Open your browser and go to `http://localhost:3000`
2. Sign up with a new account
3. Log in with your credentials
4. Use any of the four calculators from the dashboard

## API Documentation

### Authentication Endpoints

#### POST `/signup`
Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe"
}
```

#### POST `/token`
Login and get access token.

**Request Body (form-data):**
- `username`: string
- `password`: string

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### GET `/users/me`
Get current user information (requires authentication).

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe"
}
```

### Calculator Endpoints (All require authentication)

#### POST `/calculate/bmi`
Calculate Body Mass Index.

**Request Body:**
```json
{
  "weight": 70.5,
  "height": 175.0
}
```

**Response:**
```json
{
  "bmi": 23.02,
  "category": "Normal weight",
  "weight": 70.5,
  "height": 175.0
}
```

#### POST `/calculate/age`
Calculate age from birth date.

**Request Body:**
```json
{
  "birth_date": "1990-05-15"
}
```

**Response:**
```json
{
  "years": 36,
  "months": 4,
  "days": 28,
  "total_days": 13298,
  "birth_date": "1990-05-15"
}
```

#### POST `/calculate/gst`
Calculate GST on amount.

**Request Body:**
```json
{
  "amount": 1000.0,
  "gst_rate": 18.0
}
```

**Response:**
```json
{
  "original_amount": 1000.0,
  "gst_rate": 18.0,
  "gst_amount": 180.0,
  "total_amount": 1180.0
}
```

#### POST `/calculate/eb-bill`
Calculate electricity bill.

**Request Body:**
```json
{
  "units": 150.0,
  "rate_per_unit": 6.5
}
```

**Response:**
```json
{
  "units": 150.0,
  "rate_per_unit": 6.5,
  "energy_charges": 975.0,
  "fixed_charges": 48.75,
  "total_amount": 1023.75
}
```

## Deployment to Render

### Option 1: Using Blueprint (render.yaml) - Recommended

This method deploys everything at once using the `render.yaml` configuration file.

1. **Push your code to GitHub**:
```bash
git init
git add .
git commit -m "Initial commit: Calculator app"
git branch -M main
git remote add origin https://github.com/yourusername/calculator-app.git
git push -u origin main
```

2. **Connect to Render**:
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`
   - Click "Apply" to deploy

3. **Configure Environment Variables** (if needed):
   - The `render.yaml` file includes automatic configuration
   - SECRET_KEY is auto-generated
   - DATABASE_URL is automatically configured
   - Update the REACT_APP_API_URL in render.yaml to match your backend URL

4. **Wait for deployment**:
   - Backend service will be created
   - PostgreSQL database will be provisioned
   - Frontend will be built and deployed
   - This may take 5-10 minutes

### Option 2: Manual Deployment

#### Deploy Database
1. Go to Render Dashboard → New → PostgreSQL
2. Name: `calculator-db`
3. Choose the free plan
4. Click "Create Database"
5. Copy the "Internal Database URL" for the backend

#### Deploy Backend
1. Go to Render Dashboard → New → Web Service
2. Connect your repository
3. Configure:
   - **Name**: `calculator-backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**:
     - `DATABASE_URL`: Paste the database URL from step 1
     - `SECRET_KEY`: Generate using `openssl rand -hex 32`
4. Click "Create Web Service"
5. Copy your backend URL (e.g., `https://calculator-backend.onrender.com`)

#### Deploy Frontend
1. Go to Render Dashboard → New → Static Site
2. Connect your repository
3. Configure:
   - **Name**: `calculator-frontend`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/build`
   - **Environment Variables**:
     - `REACT_APP_API_URL`: Your backend URL from previous step
4. Add redirect rule:
   - Click "Redirects/Rewrites"
   - Add: Source `/*` → Destination `/index.html` (Rewrite)
5. Click "Create Static Site"

### Post-Deployment

1. Wait for all services to be live (check status in Render dashboard)
2. Visit your frontend URL
3. Test by creating an account and using the calculators
4. Monitor logs in Render dashboard for any issues

### Important Notes for Render Deployment

- **Free Tier Limitations**: 
  - Services may spin down after 15 minutes of inactivity
  - First request after inactivity may take 30-60 seconds
  - Database limited to 90 days on free tier

- **CORS**: The backend is configured to allow all origins. For production, update the CORS settings in `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-url.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=sqlite:///./calculator.db  # For local development
DATABASE_URL=postgresql://...           # For production (Render provides this)
SECRET_KEY=your-secret-key-here         # Generate with openssl rand -hex 32
```

### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:8000           # For local development
REACT_APP_API_URL=https://your-backend.onrender.com  # For production
```

## Security Considerations

1. **Always change the SECRET_KEY in production**
2. **Use HTTPS in production** (Render provides this automatically)
3. **Never commit .env files** (they're in .gitignore)
4. **Update CORS origins** to your specific frontend domain in production
5. **Use strong passwords** for user accounts
6. **Regular security updates** for dependencies

## Troubleshooting

### Backend Issues

**Database connection error:**
- Check DATABASE_URL format
- For Render PostgreSQL, ensure it starts with `postgresql://` not `postgres://`
- The code automatically handles this conversion

**Import errors:**
- Ensure all dependencies are in requirements.txt
- Verify Python version matches runtime.txt

### Frontend Issues

**API connection failed:**
- Verify REACT_APP_API_URL is set correctly
- Check backend is running
- Verify CORS settings in backend

**Build errors:**
- Clear node_modules: `rm -rf node_modules && npm install`
- Clear cache: `npm cache clean --force`

### Render Deployment Issues

**Build failed:**
- Check build logs in Render dashboard
- Verify build commands are correct
- Ensure all files are committed to git

**Service not responding:**
- Services on free tier may take time to spin up
- Check service logs in Render dashboard
- Verify environment variables are set

## Future Enhancements

- [ ] Add password reset functionality
- [ ] Store calculation history in database
- [ ] Export calculations as PDF
- [ ] Add more calculator types
- [ ] Implement dark mode
- [ ] Add user profile management
- [ ] Enable social login (Google, GitHub)
- [ ] Add API rate limiting
- [ ] Implement caching with Redis

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
- Create an issue in the GitHub repository
- Check the troubleshooting section above
- Review Render documentation: https://render.com/docs

## Acknowledgments

- FastAPI for the excellent web framework
- React team for the frontend library
- Render for hosting platform
- All open-source contributors

---

**Built with ❤️ using React and FastAPI**
