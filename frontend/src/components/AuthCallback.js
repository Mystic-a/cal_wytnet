import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

function AuthCallback({ setToken }) {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const token = searchParams.get('token');
    const error = searchParams.get('error');

    if (token) {
      setToken(token);
      navigate('/dashboard');
    } else if (error) {
      navigate('/login?error=' + error);
    } else {
      navigate('/login');
    }
  }, [searchParams, setToken, navigate]);

  return (
    <div className="auth-container">
      <h2>Authenticating...</h2>
      <p>Please wait while we log you in with Google.</p>
    </div>
  );
}

export default AuthCallback;
