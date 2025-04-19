import { useState } from 'react';
import AlertCard from '../components/AlertCard';
import AlertModal from '../components/AlertModal';

export default function Dashboard() {
  const [selectedAlert, setSelectedAlert] = useState(null);

  const dummyAlerts = [
    { id: 1, type: 'Altercation Detected', severity: 'High', time: '10:22 PM', location: 'Hostel Main Gate', videoURL: '' },
    { id: 2, type: 'Unauthorized Access', severity: 'Medium', time: '11:05 PM', location: 'Back Entry', videoURL: '' },
  ];

  return (
    <div className="dashboard">
      <h1>Live Alerts</h1>
      <div className="alerts-container">
        {dummyAlerts.map(alert => (
          <AlertCard key={alert.id} alert={alert} onClick={() => setSelectedAlert(alert)} />
        ))}
      </div>
      {selectedAlert && (
        <AlertModal alert={selectedAlert} onClose={() => setSelectedAlert(null)} />
      )}
    </div>
  );
}
