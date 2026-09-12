import React, { useState, useEffect } from 'react';
import { getCurrentUser } from '../api';
import BMICalculator from './calculators/BMICalculator';
import AgeCalculator from './calculators/AgeCalculator';
import GSTCalculator from './calculators/GSTCalculator';
import EBBillCalculator from './calculators/EBBillCalculator';

function Dashboard({ token, onLogout }) {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('bmi');

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const userData = await getCurrentUser();
        setUser(userData);
      } catch (err) {
        console.error('Failed to fetch user data:', err);
        onLogout();
      }
    };
    fetchUser();
  }, [token, onLogout]);

  const renderCalculator = () => {
    switch (activeTab) {
      case 'bmi':
        return <BMICalculator />;
      case 'age':
        return <AgeCalculator />;
      case 'gst':
        return <GSTCalculator />;
      case 'eb':
        return <EBBillCalculator />;
      default:
        return <BMICalculator />;
    }
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Calculator Dashboard</h1>
        <div className="user-info">
          {user && <span>Welcome, {user.username}!</span>}
          <button className="logout-btn" onClick={onLogout}>
            Logout
          </button>
        </div>
      </div>

      <div className="calculator-tabs">
        <button
          className={`tab-btn ${activeTab === 'bmi' ? 'active' : ''}`}
          onClick={() => setActiveTab('bmi')}
        >
          BMI Calculator
        </button>
        <button
          className={`tab-btn ${activeTab === 'age' ? 'active' : ''}`}
          onClick={() => setActiveTab('age')}
        >
          Age Calculator
        </button>
        <button
          className={`tab-btn ${activeTab === 'gst' ? 'active' : ''}`}
          onClick={() => setActiveTab('gst')}
        >
          GST Calculator
        </button>
        <button
          className={`tab-btn ${activeTab === 'eb' ? 'active' : ''}`}
          onClick={() => setActiveTab('eb')}
        >
          EB Bill Calculator
        </button>
      </div>

      <div className="calculator-content">
        {renderCalculator()}
      </div>
    </div>
  );
}

export default Dashboard;
