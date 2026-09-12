import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { exchangeWytpassToken } from '../api';

function AuthCallback({ setToken }) {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [error, setError] = useState(null);

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code');
      const errorParam = searchParams.get('error');

      if (errorParam) {
        navigate('/login?error=' + errorParam);
        return;
      }

      if (code) {
        try {
          // Get the PKCE verifier from localStorage
          const verifier = localStorage.getItem('pkce_verifier');
          
          if (!verifier) {
            throw new Error('PKCE verifier not found');
          }

          // Exchange code for token
          const data = await exchangeWytpassToken(code, verifier);
          
          // Clean up
          localStorage.removeItem('pkce_verifier');
          
          // Save token and navigate
          setToken(data.access_token);
          navigate('/dashboard');
        } catch (err) {
          console.error('Auth error:', err);
          setError(err.response?.data?.detail || err.message || 'Authentication failed');
        }
      } else {
        navigate('/login');
      }
    };

    handleCallback();
  }, [searchParams, setToken, navigate]);

  return (
    <div className="auth-container">
      <h2>Authenticating...</h2>
      {error ? (
        <div className="error-message">
          {error}
          <br />
          <button onClick={() => navigate('/login')} className="btn" style={{ marginTop: '20px' }}>
            Back to Login
          </button>
        </div>
      ) : (
        <p>Please wait while we log you in with WytPass SSO.</p>
      )}
    </div>
  );
}

export default AuthCallback;
