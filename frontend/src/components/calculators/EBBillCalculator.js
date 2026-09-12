import React, { useState } from 'react';
import { calculateEBBill } from '../../api';

function EBBillCalculator() {
  const [units, setUnits] = useState('');
  const [ratePerUnit, setRatePerUnit] = useState('6.5');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleCalculate = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await calculateEBBill(parseFloat(units), parseFloat(ratePerUnit));
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Calculation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="calculator-card">
      <h3>EB Bill Calculator</h3>
      {error && <div className="error-message">{error}</div>}
      <form onSubmit={handleCalculate}>
        <div className="form-group">
          <label>Units Consumed (kWh)</label>
          <input
            type="number"
            step="0.1"
            value={units}
            onChange={(e) => setUnits(e.target.value)}
            required
            placeholder="Enter units consumed"
          />
        </div>
        <div className="form-group">
          <label>Rate per Unit (₹)</label>
          <input
            type="number"
            step="0.01"
            value={ratePerUnit}
            onChange={(e) => setRatePerUnit(e.target.value)}
            required
            placeholder="Enter rate per unit"
          />
        </div>
        <button type="submit" className="btn" disabled={loading}>
          {loading ? 'Calculating...' : 'Calculate Bill'}
        </button>
      </form>

      {result && (
        <div className="result-card">
          <h4>Electricity Bill</h4>
          <p><strong>Units Consumed:</strong> {result.units} kWh</p>
          <p><strong>Rate per Unit:</strong> ₹{result.rate_per_unit}</p>
          <p><strong>Energy Charges:</strong> ₹{result.energy_charges}</p>
          <p><strong>Fixed Charges (5%):</strong> ₹{result.fixed_charges}</p>
          <p><strong>Total Amount:</strong> ₹{result.total_amount}</p>
        </div>
      )}
    </div>
  );
}

export default EBBillCalculator;
