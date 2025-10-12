import { useState } from 'react';
import { ArrowLeft, QrCode, CheckCircle, XCircle, Camera } from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Input } from './ui/input';
import { toast } from 'sonner@2.0.3';
import type { User } from '../App';

interface ScanQRProps {
  onNavigate: (page: 'dashboard') => void;
  currentUser: User | null;
}

export function ScanQR({ onNavigate, currentUser }: ScanQRProps) {
  const [scanning, setScanning] = useState(false);
  const [qrCode, setQrCode] = useState('');
  const [scanResult, setScanResult] = useState<{
    success: boolean;
    event: string;
    user: string;
    message: string;
  } | null>(null);

  const handleManualScan = () => {
    if (!qrCode) {
      toast.error('Please enter a QR code');
      return;
    }

    // Simulate QR code validation
    setScanResult({
      success: true,
      event: 'Tech Talk: AI in Education',
      user: 'John Doe',
      message: 'Attendance marked successfully!'
    });

    toast.success('Attendance marked!');
    setQrCode('');
  };

  const handleCameraScan = () => {
    setScanning(true);
    // Simulate camera scan
    setTimeout(() => {
      setScanResult({
        success: true,
        event: 'Annual Music Festival',
        user: 'Jane Smith',
        message: 'Check-in successful!'
      });
      setScanning(false);
      toast.success('QR code scanned successfully!');
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <button
              onClick={() => onNavigate('dashboard')}
              className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
            >
              <ArrowLeft className="size-4" />
              Back to Dashboard
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center mb-8">
          <h1 className="mb-2">Scan QR Code</h1>
          <p className="text-muted-foreground">
            Scan event tickets to mark attendance
          </p>
        </div>

        {/* Camera Scanner */}
        <Card className="p-8 mb-6">
          <div className="aspect-square bg-muted rounded-xl mb-6 flex items-center justify-center relative overflow-hidden">
            {scanning ? (
              <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center">
                <div className="animate-pulse">
                  <Camera className="size-24 text-primary" />
                </div>
              </div>
            ) : (
              <QrCode className="size-32 text-muted-foreground" />
            )}
          </div>
          <Button
            className="w-full"
            onClick={handleCameraScan}
            disabled={scanning}
          >
            <Camera className="size-4 mr-2" />
            {scanning ? 'Scanning...' : 'Start Camera Scan'}
          </Button>
        </Card>

        {/* Manual Entry */}
        <Card className="p-6 mb-6">
          <h3 className="mb-4">Manual Entry</h3>
          <p className="text-sm text-muted-foreground mb-4">
            Enter the QR code manually if camera scanning is not available
          </p>
          <div className="flex gap-2">
            <Input
              placeholder="Enter QR code"
              value={qrCode}
              onChange={(e) => setQrCode(e.target.value)}
            />
            <Button onClick={handleManualScan}>
              Validate
            </Button>
          </div>
        </Card>

        {/* Scan Result */}
        {scanResult && (
          <Card className={`p-6 ${scanResult.success ? 'border-green-500' : 'border-destructive'}`}>
            <div className="flex items-start gap-4">
              {scanResult.success ? (
                <CheckCircle className="size-6 text-green-500 mt-1" />
              ) : (
                <XCircle className="size-6 text-destructive mt-1" />
              )}
              <div className="flex-1">
                <h3 className="mb-2">{scanResult.message}</h3>
                <div className="space-y-1 text-sm text-muted-foreground">
                  <p>Event: {scanResult.event}</p>
                  <p>Attendee: {scanResult.user}</p>
                  <p>Time: {new Date().toLocaleTimeString()}</p>
                </div>
              </div>
            </div>
          </Card>
        )}

        {/* Recent Scans */}
        <Card className="p-6 mt-6">
          <h3 className="mb-4">Recent Scans</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
              <div>
                <p className="text-sm">John Doe</p>
                <p className="text-xs text-muted-foreground">Tech Talk: AI in Education</p>
              </div>
              <CheckCircle className="size-5 text-green-500" />
            </div>
            <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
              <div>
                <p className="text-sm">Jane Smith</p>
                <p className="text-xs text-muted-foreground">Annual Music Festival</p>
              </div>
              <CheckCircle className="size-5 text-green-500" />
            </div>
            <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
              <div>
                <p className="text-sm">Mike Johnson</p>
                <p className="text-xs text-muted-foreground">Career Fair 2025</p>
              </div>
              <CheckCircle className="size-5 text-green-500" />
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
