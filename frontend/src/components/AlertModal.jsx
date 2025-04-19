export default function AlertModal({ alert, onClose }) {
  return (
    <div className="modal">
      <div className="modal-content">
        <button className="close-btn" onClick={onClose}>✕</button>
        <h2>{alert.type}</h2>
        <p>{alert.time} | {alert.location} | Severity: {alert.severity}</p>
        {alert.videoURL ? (
          <video controls>
            <source src={alert.videoURL} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        ) : (
          <p>No video available</p>
        )}
      </div>
    </div>
  );
}
