import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { exchangeWytPassCode } from '../api';

function AuthCallback({ setToken }) {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [error, setError] = useState('');

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code');
      const errorParam = searchParams.get('error');

      if (errorParam) {
        setError('Authentication failed');
        setTimeout(() => navigate('/login?error=' + errorParam), 2000);
        return;
      }

      if (code) {
        try {
          const data = await exchangeWytPassCode(code);
          setToken(data.access_token);
          navigate('/dashboard');
        } catch (err) {
          console.error('WytPass callback error:', err);
          setError('Failed to complete authentication');
          setTimeout(() => navigate('/login?error=oauth_failed'), 2000);
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
        <div className="error-message">{error}</div>
      ) : (
        <p>Please wait while we log you in with WytPass.</p>
      )}
    </div>
  );
}

export default AuthCallback;
