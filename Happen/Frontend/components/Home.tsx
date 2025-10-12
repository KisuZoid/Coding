import { Calendar, QrCode, Ticket, Users, Shield, Bell } from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import type { User } from '../App';

interface HomeProps {
  onNavigate: (page: 'home' | 'login' | 'register' | 'dashboard') => void;
  currentUser: User | null;
}

export function Home({ onNavigate, currentUser }: HomeProps) {
  const features = [
    {
      icon: Calendar,
      title: 'Event Calendar',
      description: 'Browse and manage all campus events in one personalized calendar.'
    },
    {
      icon: QrCode,
      title: 'QR Check-in',
      description: 'Quick and secure attendance tracking with unique QR codes.'
    },
    {
      icon: Ticket,
      title: 'Smart Ticketing',
      description: 'Generate and manage event tickets with integrated QR codes.'
    },
    {
      icon: Users,
      title: 'Club Hub',
      description: 'Connect with clubs and stay updated on their activities.'
    },
    {
      icon: Shield,
      title: 'Secure Access',
      description: 'Role-based permissions ensure data security and privacy.'
    },
    {
      icon: Bell,
      title: 'Notifications',
      description: 'Stay informed with email alerts for events and updates.'
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="size-8 bg-primary rounded-lg flex items-center justify-center">
                <Calendar className="size-5 text-primary-foreground" />
              </div>
              <span className="font-semibold">Happen</span>
            </div>
            <div className="flex items-center gap-3">
              {currentUser ? (
                <Button onClick={() => onNavigate('dashboard')}>
                  Dashboard
                </Button>
              ) : (
                <>
                  <Button variant="ghost" onClick={() => onNavigate('login')}>
                    Login
                  </Button>
                  <Button onClick={() => onNavigate('register')}>
                    Get Started
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24">
        <div className="text-center max-w-3xl mx-auto">
          <h1 className="text-5xl md:text-6xl mb-6">
            Your Campus Events,
            <br />
            All in One Place
          </h1>
          <p className="text-muted-foreground text-lg mb-8">
            Discover events, connect with clubs, and manage attendance seamlessly with QR code technology. Built for students, by students.
          </p>
          <div className="flex items-center justify-center gap-4">
            {currentUser ? (
              <Button size="lg" onClick={() => onNavigate('dashboard')}>
                Go to Dashboard
              </Button>
            ) : (
              <>
                <Button size="lg" onClick={() => onNavigate('register')}>
                  Get Started Free
                </Button>
                <Button size="lg" variant="outline" onClick={() => onNavigate('login')}>
                  Sign In
                </Button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h2 className="mb-4">Everything You Need</h2>
          <p className="text-muted-foreground">
            A complete platform for campus event management and engagement
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Card key={index} className="p-6">
                <div className="size-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <Icon className="size-6 text-primary" />
                </div>
                <h3 className="mb-2">{feature.title}</h3>
                <p className="text-muted-foreground text-sm">
                  {feature.description}
                </p>
              </Card>
            );
          })}
        </div>
      </div>

      {/* CTA Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <Card className="p-12 text-center bg-primary text-primary-foreground">
          <h2 className="mb-4 text-primary-foreground">Ready to Get Started?</h2>
          <p className="text-primary-foreground/80 mb-8 max-w-2xl mx-auto">
            Join thousands of students using Happen to stay connected with campus life.
          </p>
          {!currentUser && (
            <Button 
              size="lg" 
              variant="secondary"
              onClick={() => onNavigate('register')}
            >
              Create Your Account
            </Button>
          )}
        </Card>
      </div>

      {/* Footer */}
      <footer className="border-t border-border mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-muted-foreground text-sm">
            <p>© 2025 Happen. Built for college students.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
