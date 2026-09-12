import React, { useState } from 'react';
import { calculateBMI } from '../../api';

function BMICalculator() {
  const [weight, setWeight] = useState('');
  const [height, setHeight] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleCalculate = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await calculateBMI(parseFloat(weight), parseFloat(height));
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Calculation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="calculator-card">
      <h3>BMI Calculator</h3>
      {error && <div className="error-message">{error}</div>}
      <form onSubmit={handleCalculate}>
        <div className="form-group">
          <label>Weight (kg)</label>
          <input
            type="number"
            step="0.1"
            value={weight}
            onChange={(e) => setWeight(e.target.value)}
            required
            placeholder="Enter weight in kilograms"
          />
        </div>
        <div className="form-group">
          <label>Height (cm)</label>
          <input
            type="number"
            step="0.1"
            value={height}
            onChange={(e) => setHeight(e.target.value)}
            required
            placeholder="Enter height in centimeters"
          />
        </div>
        <button type="submit" className="btn" disabled={loading}>
          {loading ? 'Calculating...' : 'Calculate BMI'}
        </button>
      </form>

      {result && (
        <div className="result-card">
          <h4>Your BMI Result</h4>
          <p><strong>BMI:</strong> {result.bmi}</p>
          <p><strong>Category:</strong> {result.category}</p>
          <p><strong>Weight:</strong> {result.weight} kg</p>
          <p><strong>Height:</strong> {result.height} cm</p>
        </div>
      )}
    </div>
  );
}

export default BMICalculator;
