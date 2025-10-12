import { useState, useEffect } from 'react';
import { Calendar, Mail, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';

interface EmailVerificationProps {
  onNavigate: (page: 'login' | 'home') => void;
}

export function EmailVerification({ onNavigate }: EmailVerificationProps) {
  const [verificationStatus, setVerificationStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    // Simulate email verification API call
    const verifyEmail = async () => {
      // In real app, extract token from URL and send to backend
      // const token = new URLSearchParams(window.location.search).get('token');
      
      setTimeout(() => {
        // Simulate successful verification
        setVerificationStatus('success');
        setMessage('Your email has been verified successfully!');
      }, 2000);
    };

    verifyEmail();
  }, []);

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <div className="border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <button 
              onClick={() => onNavigate('home')}
              className="flex items-center gap-2 hover:opacity-80 transition-opacity"
            >
              <div className="size-8 bg-primary rounded-lg flex items-center justify-center">
                <Calendar className="size-5 text-primary-foreground" />
              </div>
              <span className="font-semibold">Happen</span>
            </button>
          </div>
        </div>
      </div>

      {/* Verification Content */}
      <div className="flex-1 flex items-center justify-center px-4 py-12">
        <Card className="w-full max-w-md p-8">
          <div className="text-center">
            {verificationStatus === 'loading' && (
              <>
                <div className="size-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
                  <Loader2 className="size-8 text-primary animate-spin" />
                </div>
                <h2 className="mb-2">Verifying Your Email</h2>
                <p className="text-muted-foreground">
                  Please wait while we verify your email address...
                </p>
              </>
            )}

            {verificationStatus === 'success' && (
              <>
                <div className="size-16 bg-green-500/10 rounded-full flex items-center justify-center mx-auto mb-6">
                  <CheckCircle className="size-8 text-green-500" />
                </div>
                <h2 className="mb-2">Email Verified!</h2>
                <p className="text-muted-foreground mb-8">
                  {message}
                </p>
                <Button onClick={() => onNavigate('login')} className="w-full">
                  Continue to Login
                </Button>
              </>
            )}

            {verificationStatus === 'error' && (
              <>
                <div className="size-16 bg-destructive/10 rounded-full flex items-center justify-center mx-auto mb-6">
                  <XCircle className="size-8 text-destructive" />
                </div>
                <h2 className="mb-2">Verification Failed</h2>
                <p className="text-muted-foreground mb-8">
                  The verification link is invalid or has expired.
                </p>
                <Button onClick={() => onNavigate('login')} className="w-full">
                  Back to Login
                </Button>
              </>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
