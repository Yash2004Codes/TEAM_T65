import { useState, useEffect } from "react";
import { cameras as initialCameras, alerts as initialAlerts, eventLogs as initialEventLogs } from "@/data/mockData";
import { useSurveillanceSimulation } from "@/hooks/useSurveillanceSimulation";
import { SurveillanceHeader } from "@/components/surveillance/SurveillanceHeader";
import { CameraSidebar } from "@/components/surveillance/CameraSidebar";
import { AlertsSidebar } from "@/components/surveillance/AlertsSidebar";
import { EventTimeline } from "@/components/surveillance/EventTimeline";
import { MainCameraView } from "@/components/surveillance/MainCameraView";
import { CameraGrid } from "@/components/surveillance/CameraGrid";
import { LoadingScreen } from "@/components/surveillance/LoadingScreen";

const Index = () => {
  const [selectedCameraId, setSelectedCameraId] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'single' | 'grid'>('single');
  const [loading, setLoading] = useState(true);
  
  // Use our simulation hook
  const { cameras, alerts, eventLogs, acknowledgeAlert } = useSurveillanceSimulation({
    initialCameras,
    initialAlerts,
    initialEventLogs,
    alertInterval: 15000, // Generate possible alerts every 15 seconds
    maxAlerts: 10 // Cap at 10 alerts for demo
  });
  
  // Select the first camera with an alert, or the first camera if none have alerts
  useEffect(() => {
    const alertCamera = cameras.find(camera => camera.status === 'alert');
    setSelectedCameraId(alertCamera?.id || cameras[0]?.id || null);
  }, [cameras]);
  
  // Simulate loading the system
  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(false);
    }, 2500);
    
    return () => clearTimeout(timer);
  }, []);
  
  const selectedCamera = cameras.find(camera => camera.id === selectedCameraId);

  const handleSelectCamera = (cameraId: string) => {
    setSelectedCameraId(cameraId);
    setViewMode('single');
  };

  const handleFightDetection = async () => {
    try {
      const res = await fetch("http://10.10.115.78:5000/fight");  // Replace with your friend's PC IP
      const data = await res.json();
      alert(data.status);
    } catch (err) {
      console.error("Fight detection error:", err);
      alert("Failed to start fight detection.");
    }
  };
  
  const handleDrowsyDetection = async () => {
    try {
      const res = await fetch("http://10.10.115.78:5000/drowsy");  // Replace with your friend's PC IP
      const data = await res.json();
      alert(data.status);
    } catch (err) {
      console.error("Drowsy detection error:", err);
      alert("Failed to start drowsy detection.");
    }
  };
  

  return (
    <div className="min-h-screen bg-surveillance-bg text-surveillance-text p-4">
      {loading && <LoadingScreen />}
      <div className="container mx-auto">
        <SurveillanceHeader />
        
        <div className="mt-4 grid grid-cols-1 lg:grid-cols-12 gap-4">
          {/* Left sidebar */}
          <div className="lg:col-span-2">
            <CameraSidebar 
              cameras={cameras} 
              onSelectCamera={handleSelectCamera}
              selectedCameraId={selectedCameraId || undefined}
            />
          </div>
          
          {/* Main content */}
          <div className="lg:col-span-7 flex flex-col gap-4">
            <div className="bg-surveillance-panel p-2 rounded-lg flex gap-2">
              <button 
                className={`px-3 py-1 rounded-full text-sm ${viewMode === 'single' ? 'bg-surveillance-accent text-surveillance-panel' : 'bg-black/20 hover:bg-black/30'}`}
                onClick={() => setViewMode('single')}
              >
                Single View
              </button>
              <button 
                className={`px-3 py-1 rounded-full text-sm ${viewMode === 'grid' ? 'bg-surveillance-accent text-surveillance-panel' : 'bg-black/20 hover:bg-black/30'}`}
                onClick={() => setViewMode('grid')}
              >
                Grid View
              </button>
            </div>

            {/* Fight and Drowsy Detection Buttons */}
            <div className="mt-4 flex gap-4">
              <button 
                className="px-4 py-2 bg-red-500 text-white rounded-lg"
                onClick={handleFightDetection}
              >
                Fight Detection
              </button>
              <button 
                className="px-4 py-2 bg-yellow-500 text-white rounded-lg"
                onClick={handleDrowsyDetection}
              >
                Drowsy Detection
              </button>
            </div>
            
            {viewMode === 'single' && selectedCamera ? (
              <MainCameraView 
                camera={selectedCamera} 
                alerts={alerts.filter(alert => alert.cameraId === selectedCamera.id)}
              />
            ) : (
              <CameraGrid 
                cameras={cameras} 
                onSelectCamera={handleSelectCamera}
              />
            )}
            
            <EventTimeline events={eventLogs} cameras={cameras} />
          </div>
          
          {/* Right sidebar */}
          <div className="lg:col-span-3">
            <AlertsSidebar 
              alerts={alerts} 
              cameras={cameras} 
              onAcknowledgeAlert={acknowledgeAlert} 
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
