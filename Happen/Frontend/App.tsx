import { useState, useEffect } from 'react';
import { Home } from './components/Home';
import { Login } from './components/Login';
import { Register } from './components/Register';
import { EmailVerification } from './components/EmailVerification';
import { PasswordReset } from './components/PasswordReset';
import { UserDashboard } from './components/UserDashboard';
import { OrganizerDashboard } from './components/OrganizerDashboard';
import { AdminDashboard } from './components/AdminDashboard';
import { EventDetails } from './components/EventDetails';
import { ScanQR } from './components/ScanQR';
import { Profile } from './components/Profile';
import { MyTickets } from './components/MyTickets';
import { ClubDetails } from './components/ClubDetails';
import { Toaster } from './components/ui/sonner';

type Page = 
  | 'home' 
  | 'login' 
  | 'register' 
  | 'email-verification'
  | 'password-reset'
  | 'dashboard' 
  | 'event-details' 
  | 'scan' 
  | 'profile'
  | 'my-tickets'
  | 'club-details';

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'organizer' | 'user';
  verified: boolean;
  organizationId?: string;
}

export interface Event {
  id: string;
  title: string;
  description: string;
  date: string;
  time: string;
  location: string;
  organizerId: string;
  organizerName: string;
  category: string;
  image: string;
  attendees: number;
  capacity: number;
  clubId?: string;
  clubName?: string;
  isPaid: boolean;
  price?: number;
}

export interface Club {
  id: string;
  name: string;
  description: string;
  category: string;
  image: string;
  memberCount: number;
  events: number;
}

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('home');
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);
  const [selectedClubId, setSelectedClubId] = useState<string | null>(null);

  useEffect(() => {
    // Check if user is logged in from localStorage
    const storedUser = localStorage.getItem('currentUser');
    if (storedUser) {
      setCurrentUser(JSON.parse(storedUser));
      setCurrentPage('dashboard');
    }
  }, []);

  const handleLogin = (user: User) => {
    setCurrentUser(user);
    localStorage.setItem('currentUser', JSON.stringify(user));
    setCurrentPage('dashboard');
  };

  const handleLogout = () => {
    setCurrentUser(null);
    localStorage.removeItem('currentUser');
    setCurrentPage('home');
  };

  const handleNavigate = (page: Page, id?: string) => {
    if (page === 'event-details' && id) {
      setSelectedEventId(id);
    }
    if (page === 'club-details' && id) {
      setSelectedClubId(id);
    }
    setCurrentPage(page);
  };

  const renderDashboard = () => {
    if (!currentUser) return <Home onNavigate={handleNavigate} currentUser={null} />;
    
    switch (currentUser.role) {
      case 'admin':
        return <AdminDashboard onNavigate={handleNavigate} currentUser={currentUser} onLogout={handleLogout} />;
      case 'organizer':
        return <OrganizerDashboard onNavigate={handleNavigate} currentUser={currentUser} onLogout={handleLogout} />;
      case 'user':
      default:
        return <UserDashboard onNavigate={handleNavigate} currentUser={currentUser} onLogout={handleLogout} />;
    }
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'home':
        return <Home onNavigate={handleNavigate} currentUser={currentUser} />;
      case 'login':
        return <Login onNavigate={handleNavigate} onLogin={handleLogin} />;
      case 'register':
        return <Register onNavigate={handleNavigate} />;
      case 'email-verification':
        return <EmailVerification onNavigate={handleNavigate} />;
      case 'password-reset':
        return <PasswordReset onNavigate={handleNavigate} />;
      case 'dashboard':
        return renderDashboard();
      case 'event-details':
        return <EventDetails eventId={selectedEventId} onNavigate={handleNavigate} currentUser={currentUser} />;
      case 'scan':
        return <ScanQR onNavigate={handleNavigate} currentUser={currentUser} />;
      case 'profile':
        return <Profile onNavigate={handleNavigate} currentUser={currentUser} onLogout={handleLogout} />;
      case 'my-tickets':
        return <MyTickets onNavigate={handleNavigate} currentUser={currentUser} />;
      case 'club-details':
        return <ClubDetails clubId={selectedClubId} onNavigate={handleNavigate} currentUser={currentUser} />;
      default:
        return <Home onNavigate={handleNavigate} currentUser={currentUser} />;
    }
  };

  return (
    <div className="size-full">
      {renderPage()}
      <Toaster />
    </div>
  );
}