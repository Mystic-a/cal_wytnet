import React, { useState } from 'react';
import { calculateAge } from '../../api';

function AgeCalculator() {
  const [birthDate, setBirthDate] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleCalculate = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await calculateAge(birthDate);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Calculation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="calculator-card">
      <h3>Age Calculator</h3>
      {error && <div className="error-message">{error}</div>}
      <form onSubmit={handleCalculate}>
        <div className="form-group">
          <label>Birth Date</label>
          <input
            type="date"
            value={birthDate}
            onChange={(e) => setBirthDate(e.target.value)}
            required
            max={new Date().toISOString().split('T')[0]}
          />
        </div>
        <button type="submit" className="btn" disabled={loading}>
          {loading ? 'Calculating...' : 'Calculate Age'}
        </button>
      </form>

      {result && (
        <div className="result-card">
          <h4>Your Age</h4>
          <p><strong>Years:</strong> {result.years}</p>
          <p><strong>Months:</strong> {result.months}</p>
          <p><strong>Days:</strong> {result.days}</p>
          <p><strong>Total Days:</strong> {result.total_days}</p>
          <p><strong>Birth Date:</strong> {result.birth_date}</p>
        </div>
      )}
    </div>
  );
}

export default AgeCalculator;
