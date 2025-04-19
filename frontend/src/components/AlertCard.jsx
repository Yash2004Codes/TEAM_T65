export default function AlertCard({ alert, onClick }) {
  const getColor = (severity) => {
    switch (severity) {
      case 'High': return 'red';
      case 'Medium': return 'orange';
      default: return 'green';
    }
  };

  return (
    <div className="alert-card" onClick={onClick}>
      <div className="alert-header">
        <h2>{alert.type}</h2>
        <span style={{ backgroundColor: getColor(alert.severity) }}>{alert.severity}</span>
      </div>
      <p>{alert.time} | {alert.location}</p>
    </div>
  );
}
