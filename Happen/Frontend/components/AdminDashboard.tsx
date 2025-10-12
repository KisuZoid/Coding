import { useState } from 'react';
import { Calendar, Plus, Users, QrCode, Ticket, Edit, Trash2, User, LogOut, Shield, Search, UserCog } from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Badge } from './ui/badge';
import { toast } from 'sonner@2.0.3';
import type { User as UserType, Event } from '../App';

interface AdminDashboardProps {
  onNavigate: (page: any, id?: string) => void;
  currentUser: UserType | null;
  onLogout: () => void;
}

const mockAllEvents: Event[] = [
  {
    id: '1',
    title: 'Tech Talk: AI in Education',
    description: 'Join us for an insightful discussion on how AI is transforming education.',
    date: '2025-10-15',
    time: '18:00',
    location: 'Engineering Building, Room 301',
    organizerId: 'org-1',
    organizerName: 'Computer Science Club',
    category: 'Technology',
    image: 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800',
    attendees: 45,
    capacity: 100
  },
  {
    id: '2',
    title: 'Annual Music Festival',
    description: 'Experience live performances from talented student musicians.',
    date: '2025-10-18',
    time: '19:00',
    location: 'Campus Auditorium',
    organizerId: 'org-2',
    organizerName: 'Music Society',
    category: 'Entertainment',
    image: 'https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=800',
    attendees: 230,
    capacity: 500
  },
  {
    id: '3',
    title: 'Career Fair 2025',
    description: 'Connect with top employers and explore internship opportunities.',
    date: '2025-10-20',
    time: '10:00',
    location: 'Student Center',
    organizerId: 'org-3',
    organizerName: 'Career Services',
    category: 'Career',
    image: 'https://images.unsplash.com/photo-1511578314322-379afb476865?w=800',
    attendees: 156,
    capacity: 300
  }
];

const mockUsers = [
  { id: '1', name: 'John Doe', email: 'john.doe@college.edu', role: 'user', verified: true, eventsAttended: 12 },
  { id: '2', name: 'Jane Smith', email: 'jane.smith@college.edu', role: 'organizer', verified: true, eventsAttended: 8 },
  { id: '3', name: 'Mike Johnson', email: 'mike.j@college.edu', role: 'user', verified: true, eventsAttended: 5 },
  { id: '4', name: 'Sarah Williams', email: 'sarah.w@college.edu', role: 'organizer', verified: true, eventsAttended: 15 },
  { id: '5', name: 'Tom Brown', email: 'tom.brown@college.edu', role: 'user', verified: false, eventsAttended: 0 }
];

export function AdminDashboard({ onNavigate, currentUser, onLogout }: AdminDashboardProps) {
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [newEvent, setNewEvent] = useState({
    title: '',
    description: '',
    date: '',
    time: '',
    location: '',
    category: '',
    capacity: '',
    isPaid: false,
    price: ''
  });

  const handleCreateEvent = () => {
    if (!newEvent.title || !newEvent.date || !newEvent.time || !newEvent.location) {
      toast.error('Please fill in all required fields');
      return;
    }

    toast.success('Event created successfully!');
    setShowCreateDialog(false);
    setNewEvent({
      title: '',
      description: '',
      date: '',
      time: '',
      location: '',
      category: '',
      capacity: '',
      isPaid: false,
      price: ''
    });
  };

  const handleDeleteEvent = (eventId: string) => {
    toast.success('Event deleted successfully');
  };

  const handleToggleUserRole = (userId: string, currentRole: string) => {
    const newRole = currentRole === 'user' ? 'organizer' : 'user';
    toast.success(`User role updated to ${newRole}`);
  };

  const handleDeleteUser = (userId: string) => {
    toast.success('User deleted successfully');
  };

  const totalAttendees = mockAllEvents.reduce((sum, event) => sum + event.attendees, 0);
  const filteredUsers = mockUsers.filter(user => 
    user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    user.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b border-border sticky top-0 bg-background z-10">
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
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="bg-red-500/10 text-red-700 dark:text-red-300">
                <Shield className="size-3 mr-1" />
                Admin
              </Badge>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => onNavigate('scan')}
                title="Scan QR Code"
              >
                <QrCode className="size-5" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => onNavigate('profile')}
                title="Profile"
              >
                <User className="size-5" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={onLogout}
                title="Logout"
              >
                <LogOut className="size-5" />
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="mb-2">Admin Dashboard</h1>
            <p className="text-muted-foreground">
              Manage all events, users, and system settings
            </p>
          </div>
          <Button onClick={() => setShowCreateDialog(true)}>
            <Plus className="size-4 mr-2" />
            Create Event
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-muted-foreground text-sm mb-1">Total Events</p>
                <p className="text-2xl">{mockAllEvents.length}</p>
              </div>
              <Calendar className="size-8 text-muted-foreground" />
            </div>
          </Card>
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-muted-foreground text-sm mb-1">Total Users</p>
                <p className="text-2xl">{mockUsers.length}</p>
              </div>
              <Users className="size-8 text-muted-foreground" />
            </div>
          </Card>
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-muted-foreground text-sm mb-1">Tickets Issued</p>
                <p className="text-2xl">{totalAttendees}</p>
              </div>
              <Ticket className="size-8 text-muted-foreground" />
            </div>
          </Card>
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-muted-foreground text-sm mb-1">QR Scans</p>
                <p className="text-2xl">{Math.floor(totalAttendees * 0.85)}</p>
              </div>
              <QrCode className="size-8 text-muted-foreground" />
            </div>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="events" className="w-full">
          <TabsList>
            <TabsTrigger value="events">All Events</TabsTrigger>
            <TabsTrigger value="users">User Management</TabsTrigger>
            <TabsTrigger value="attendance">Attendance Logs</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          <TabsContent value="events" className="mt-6">
            <div className="space-y-4">
              {mockAllEvents.map((event) => (
                <Card key={event.id} className="p-6">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-start gap-4 flex-1">
                      <div className="size-20 bg-muted rounded-lg overflow-hidden flex-shrink-0">
                        <img
                          src={event.image}
                          alt={event.title}
                          className="w-full h-full object-cover"
                        />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-4 mb-2">
                          <div>
                            <h4 className="mb-1">{event.title}</h4>
                            <p className="text-sm text-muted-foreground">
                              Organized by {event.organizerName}
                            </p>
                          </div>
                          <Badge className="bg-blue-500/10 text-blue-700 dark:text-blue-300">
                            {event.category}
                          </Badge>
                        </div>
                        <div className="grid grid-cols-3 gap-4 mt-3">
                          <div>
                            <p className="text-sm text-muted-foreground">Date & Time</p>
                            <p className="text-sm">
                              {new Date(event.date).toLocaleDateString()} • {event.time}
                            </p>
                          </div>
                          <div>
                            <p className="text-sm text-muted-foreground">Location</p>
                            <p className="text-sm">{event.location}</p>
                          </div>
                          <div>
                            <p className="text-sm text-muted-foreground">Attendance</p>
                            <p className="text-sm">{event.attendees}/{event.capacity}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="icon">
                        <Edit className="size-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="icon"
                        onClick={() => handleDeleteEvent(event.id)}
                      >
                        <Trash2 className="size-4 text-destructive" />
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="users" className="mt-6">
            <div className="mb-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                <Input
                  placeholder="Search users..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="space-y-3">
              {filteredUsers.map((user) => (
                <Card key={user.id} className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="size-12 bg-muted rounded-full flex items-center justify-center">
                        <User className="size-6 text-muted-foreground" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <h4>{user.name}</h4>
                          {user.verified ? (
                            <Badge variant="outline" className="bg-green-500/10 text-green-700 dark:text-green-300">
                              Verified
                            </Badge>
                          ) : (
                            <Badge variant="outline" className="bg-yellow-500/10 text-yellow-700 dark:text-yellow-300">
                              Unverified
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground">{user.email}</p>
                        <p className="text-sm text-muted-foreground">{user.eventsAttended} events attended</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="capitalize">
                        {user.role}
                      </Badge>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleToggleUserRole(user.id, user.role)}
                      >
                        <UserCog className="size-4 mr-2" />
                        Change Role
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDeleteUser(user.id)}
                      >
                        <Trash2 className="size-4 text-destructive" />
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="attendance" className="mt-6">
            <div className="space-y-4">
              {mockAllEvents.map((event) => (
                <Card key={event.id} className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h4 className="mb-1">{event.title}</h4>
                      <p className="text-sm text-muted-foreground">
                        {Math.floor(event.attendees * 0.85)} attendees checked in • {event.attendees} registered
                      </p>
                    </div>
                    <Button variant="outline" size="sm">
                      View Details
                    </Button>
                  </div>
                  <div className="grid grid-cols-4 gap-4">
                    <div className="p-4 bg-muted rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">Registered</p>
                      <p className="text-xl">{event.attendees}</p>
                    </div>
                    <div className="p-4 bg-muted rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">Checked In</p>
                      <p className="text-xl">{Math.floor(event.attendees * 0.85)}</p>
                    </div>
                    <div className="p-4 bg-muted rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">No Show</p>
                      <p className="text-xl">{Math.floor(event.attendees * 0.15)}</p>
                    </div>
                    <div className="p-4 bg-muted rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">Attendance Rate</p>
                      <p className="text-xl">85%</p>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="settings" className="mt-6">
            <div className="space-y-6">
              <Card className="p-6">
                <h3 className="mb-4">System Settings</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Email Notifications</p>
                      <p className="text-sm text-muted-foreground">
                        Send email notifications for new events
                      </p>
                    </div>
                    <Button variant="outline">Configure</Button>
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">QR Code Settings</p>
                      <p className="text-sm text-muted-foreground">
                        Configure QR code generation and validation
                      </p>
                    </div>
                    <Button variant="outline">Configure</Button>
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">User Registration</p>
                      <p className="text-sm text-muted-foreground">
                        Manage registration settings and email verification
                      </p>
                    </div>
                    <Button variant="outline">Configure</Button>
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <h3 className="mb-4">Database Statistics</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-muted rounded-lg">
                    <p className="text-sm text-muted-foreground mb-1">Total Database Size</p>
                    <p className="text-xl">124 MB</p>
                  </div>
                  <div className="p-4 bg-muted rounded-lg">
                    <p className="text-sm text-muted-foreground mb-1">Active Sessions</p>
                    <p className="text-xl">847</p>
                  </div>
                </div>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>

      {/* Create Event Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="sm:max-w-xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create New Event</DialogTitle>
            <DialogDescription>
              Create a new event on behalf of an organizer
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="title">Event Title *</Label>
              <Input
                id="title"
                placeholder="Enter event title"
                value={newEvent.title}
                onChange={(e) => setNewEvent({ ...newEvent, title: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                placeholder="Enter event description"
                value={newEvent.description}
                onChange={(e) => setNewEvent({ ...newEvent, description: e.target.value })}
                rows={4}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="date">Date *</Label>
                <Input
                  id="date"
                  type="date"
                  value={newEvent.date}
                  onChange={(e) => setNewEvent({ ...newEvent, date: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="time">Time *</Label>
                <Input
                  id="time"
                  type="time"
                  value={newEvent.time}
                  onChange={(e) => setNewEvent({ ...newEvent, time: e.target.value })}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="location">Location *</Label>
              <Input
                id="location"
                placeholder="Enter event location"
                value={newEvent.location}
                onChange={(e) => setNewEvent({ ...newEvent, location: e.target.value })}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="category">Category</Label>
                <Select
                  value={newEvent.category}
                  onValueChange={(value) => setNewEvent({ ...newEvent, category: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Technology">Technology</SelectItem>
                    <SelectItem value="Entertainment">Entertainment</SelectItem>
                    <SelectItem value="Career">Career</SelectItem>
                    <SelectItem value="Wellness">Wellness</SelectItem>
                    <SelectItem value="Business">Business</SelectItem>
                    <SelectItem value="Arts">Arts</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="capacity">Capacity</Label>
                <Input
                  id="capacity"
                  type="number"
                  placeholder="100"
                  value={newEvent.capacity}
                  onChange={(e) => setNewEvent({ ...newEvent, capacity: e.target.value })}
                />
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Paid Event</Label>
                  <p className="text-sm text-muted-foreground">
                    Charge attendees for this event (5% platform fee applies)
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={newEvent.isPaid}
                  onChange={(e) => setNewEvent({ ...newEvent, isPaid: e.target.checked, price: e.target.checked ? newEvent.price : '' })}
                  className="size-4"
                />
              </div>

              {newEvent.isPaid && (
                <div className="space-y-2">
                  <Label htmlFor="price">Ticket Price ($)</Label>
                  <Input
                    id="price"
                    type="number"
                    step="0.01"
                    min="0"
                    placeholder="25.00"
                    value={newEvent.price}
                    onChange={(e) => setNewEvent({ ...newEvent, price: e.target.value })}
                    required={newEvent.isPaid}
                  />
                  {newEvent.price && (
                    <p className="text-sm text-muted-foreground">
                      Platform fee: ${(parseFloat(newEvent.price) * 0.05).toFixed(2)} • 
                      Organizer receives: ${(parseFloat(newEvent.price) * 0.95).toFixed(2)}
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
          <div className="flex justify-end gap-3">
            <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreateEvent}>
              Create Event
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}