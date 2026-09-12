import React, { useState } from 'react';
import { calculateGST } from '../../api';

function GSTCalculator() {
  const [amount, setAmount] = useState('');
  const [gstRate, setGstRate] = useState('18');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleCalculate = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await calculateGST(parseFloat(amount), parseFloat(gstRate));
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Calculation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="calculator-card">
      <h3>GST Calculator</h3>
      {error && <div className="error-message">{error}</div>}
      <form onSubmit={handleCalculate}>
        <div className="form-group">
          <label>Amount (₹)</label>
          <input
            type="number"
            step="0.01"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            required
            placeholder="Enter amount"
          />
        </div>
        <div className="form-group">
          <label>GST Rate (%)</label>
          <select value={gstRate} onChange={(e) => setGstRate(e.target.value)}>
            <option value="5">5%</option>
            <option value="12">12%</option>
            <option value="18">18%</option>
            <option value="28">28%</option>
          </select>
        </div>
        <button type="submit" className="btn" disabled={loading}>
          {loading ? 'Calculating...' : 'Calculate GST'}
        </button>
      </form>

      {result && (
        <div className="result-card">
          <h4>GST Calculation</h4>
          <p><strong>Original Amount:</strong> ₹{result.original_amount}</p>
          <p><strong>GST Rate:</strong> {result.gst_rate}%</p>
          <p><strong>GST Amount:</strong> ₹{result.gst_amount}</p>
          <p><strong>Total Amount:</strong> ₹{result.total_amount}</p>
        </div>
      )}
    </div>
  );
}

export default GSTCalculator;
