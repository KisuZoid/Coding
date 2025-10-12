import { useState } from 'react';
import { ArrowLeft, User, Mail, Shield, Calendar, Ticket, QrCode, Edit } from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Badge } from './ui/badge';
import { toast } from 'sonner@2.0.3';
import type { User as UserType } from '../App';

interface ProfileProps {
  onNavigate: (page: 'dashboard') => void;
  currentUser: UserType | null;
  onLogout: () => void;
}

export function Profile({ onNavigate, currentUser, onLogout }: ProfileProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [profileData, setProfileData] = useState({
    name: currentUser?.name || '',
    email: currentUser?.email || ''
  });

  const handleSaveProfile = () => {
    toast.success('Profile updated successfully!');
    setIsEditing(false);
  };

  const mockTickets = [
    {
      id: '1',
      event: 'Tech Talk: AI in Education',
      date: '2025-10-15',
      time: '18:00',
      location: 'Engineering Building, Room 301',
      status: 'upcoming'
    },
    {
      id: '2',
      event: 'Annual Music Festival',
      date: '2025-10-18',
      time: '19:00',
      location: 'Campus Auditorium',
      status: 'upcoming'
    },
    {
      id: '3',
      event: 'Career Fair 2025',
      date: '2025-09-20',
      time: '10:00',
      location: 'Student Center',
      status: 'attended'
    }
  ];

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
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Sidebar */}
          <div className="space-y-6">
            <Card className="p-6">
              <div className="flex flex-col items-center text-center">
                <div className="size-24 bg-primary rounded-full flex items-center justify-center mb-4">
                  <User className="size-12 text-primary-foreground" />
                </div>
                <h3 className="mb-1">{currentUser?.name}</h3>
                <p className="text-sm text-muted-foreground mb-4">{currentUser?.email}</p>
                <div className="flex items-center gap-2 mb-4">
                  <Badge variant="outline" className="capitalize">
                    {currentUser?.role}
                  </Badge>
                  {currentUser?.verified && (
                    <Badge variant="outline" className="bg-green-500/10 text-green-700 dark:text-green-300">
                      Verified
                    </Badge>
                  )}
                </div>
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={onLogout}
                >
                  Sign Out
                </Button>
              </div>
            </Card>

            <Card className="p-6">
              <h4 className="mb-4">Account Stats</h4>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Calendar className="size-4 text-muted-foreground" />
                    <span className="text-sm">Events Registered</span>
                  </div>
                  <span className="text-sm">3</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Ticket className="size-4 text-muted-foreground" />
                    <span className="text-sm">Tickets</span>
                  </div>
                  <span className="text-sm">3</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <QrCode className="size-4 text-muted-foreground" />
                    <span className="text-sm">Events Attended</span>
                  </div>
                  <span className="text-sm">12</span>
                </div>
              </div>
            </Card>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            <Tabs defaultValue="profile" className="w-full">
              <TabsList className="w-full">
                <TabsTrigger value="profile" className="flex-1">Profile</TabsTrigger>
                <TabsTrigger value="tickets" className="flex-1">My Tickets</TabsTrigger>
                <TabsTrigger value="history" className="flex-1">History</TabsTrigger>
              </TabsList>

              <TabsContent value="profile" className="mt-6">
                <Card className="p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h3>Profile Information</h3>
                    {!isEditing && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setIsEditing(true)}
                      >
                        <Edit className="size-4 mr-2" />
                        Edit
                      </Button>
                    )}
                  </div>

                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="name">Full Name</Label>
                      <div className="relative">
                        <User className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                        <Input
                          id="name"
                          value={profileData.name}
                          onChange={(e) => setProfileData({ ...profileData, name: e.target.value })}
                          className="pl-10"
                          disabled={!isEditing}
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="email">Email Address</Label>
                      <div className="relative">
                        <Mail className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                        <Input
                          id="email"
                          type="email"
                          value={profileData.email}
                          onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
                          className="pl-10"
                          disabled={!isEditing}
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="role">Account Type</Label>
                      <div className="relative">
                        <Shield className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                        <Input
                          id="role"
                          value={currentUser?.role || ''}
                          className="pl-10 capitalize"
                          disabled
                        />
                      </div>
                    </div>

                    {isEditing && (
                      <div className="flex gap-2 pt-4">
                        <Button onClick={handleSaveProfile}>
                          Save Changes
                        </Button>
                        <Button
                          variant="outline"
                          onClick={() => setIsEditing(false)}
                        >
                          Cancel
                        </Button>
                      </div>
                    )}
                  </div>
                </Card>
              </TabsContent>

              <TabsContent value="tickets" className="mt-6">
                <div className="space-y-4">
                  {mockTickets
                    .filter(ticket => ticket.status === 'upcoming')
                    .map((ticket) => (
                      <Card key={ticket.id} className="p-6">
                        <div className="flex items-start justify-between mb-4">
                          <div>
                            <h4 className="mb-2">{ticket.event}</h4>
                            <div className="space-y-1 text-sm text-muted-foreground">
                              <div className="flex items-center gap-2">
                                <Calendar className="size-4" />
                                {new Date(ticket.date).toLocaleDateString('en-US', {
                                  month: 'long',
                                  day: 'numeric',
                                  year: 'numeric'
                                })} at {ticket.time}
                              </div>
                              <p>{ticket.location}</p>
                            </div>
                          </div>
                          <Badge className="bg-blue-500/10 text-blue-700 dark:text-blue-300">
                            Upcoming
                          </Badge>
                        </div>
                        <Button variant="outline" className="w-full">
                          <QrCode className="size-4 mr-2" />
                          View QR Code
                        </Button>
                      </Card>
                    ))}
                </div>
              </TabsContent>

              <TabsContent value="history" className="mt-6">
                <div className="space-y-4">
                  {mockTickets
                    .filter(ticket => ticket.status === 'attended')
                    .map((ticket) => (
                      <Card key={ticket.id} className="p-6">
                        <div className="flex items-start justify-between">
                          <div>
                            <h4 className="mb-2">{ticket.event}</h4>
                            <div className="space-y-1 text-sm text-muted-foreground">
                              <div className="flex items-center gap-2">
                                <Calendar className="size-4" />
                                {new Date(ticket.date).toLocaleDateString('en-US', {
                                  month: 'long',
                                  day: 'numeric',
                                  year: 'numeric'
                                })}
                              </div>
                              <p>{ticket.location}</p>
                            </div>
                          </div>
                          <Badge className="bg-green-500/10 text-green-700 dark:text-green-300">
                            Attended
                          </Badge>
                        </div>
                      </Card>
                    ))}
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>
    </div>
  );
}
