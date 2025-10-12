import { useState } from 'react';
import { Calendar, Plus, Users, QrCode, Ticket, Edit, Trash2, BarChart3, User, LogOut, Eye } from 'lucide-react';
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

interface OrganizerDashboardProps {
  onNavigate: (page: any, id?: string) => void;
  currentUser: UserType | null;
  onLogout: () => void;
}

const mockOrganizerEvents: Event[] = [
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
    id: '5',
    title: 'Hackathon 2025',
    description: '24-hour coding competition with amazing prizes.',
    date: '2025-11-01',
    time: '09:00',
    location: 'Tech Hub',
    organizerId: 'org-1',
    organizerName: 'Computer Science Club',
    category: 'Technology',
    image: 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=800',
    attendees: 78,
    capacity: 150
  }
];

export function OrganizerDashboard({ onNavigate, currentUser, onLogout }: OrganizerDashboardProps) {
  const [showCreateDialog, setShowCreateDialog] = useState(false);
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

  const totalAttendees = mockOrganizerEvents.reduce((sum, event) => sum + event.attendees, 0);
  const totalCapacity = mockOrganizerEvents.reduce((sum, event) => sum + event.capacity, 0);

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
              <Badge variant="outline" className="bg-purple-500/10 text-purple-700 dark:text-purple-300">
                Organizer
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
            <h1 className="mb-2">Organizer Dashboard</h1>
            <p className="text-muted-foreground">
              Manage your events and track attendance
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
                <p className="text-muted-foreground text-sm mb-1">My Events</p>
                <p className="text-2xl">{mockOrganizerEvents.length}</p>
              </div>
              <Calendar className="size-8 text-muted-foreground" />
            </div>
          </Card>
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-muted-foreground text-sm mb-1">Total Attendees</p>
                <p className="text-2xl">{totalAttendees}</p>
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
                <p className="text-muted-foreground text-sm mb-1">Avg. Attendance</p>
                <p className="text-2xl">{Math.round((totalAttendees / totalCapacity) * 100)}%</p>
              </div>
              <BarChart3 className="size-8 text-muted-foreground" />
            </div>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="events" className="w-full">
          <TabsList>
            <TabsTrigger value="events">My Events</TabsTrigger>
            <TabsTrigger value="attendance">Attendance</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="events" className="mt-6">
            <div className="space-y-4">
              {mockOrganizerEvents.map((event) => (
                <Card key={event.id} className="p-6">
                  <div className="flex items-start gap-4">
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
                          <h3 className="mb-1">{event.title}</h3>
                          <p className="text-sm text-muted-foreground line-clamp-2">
                            {event.description}
                          </p>
                        </div>
                        <Badge className="bg-blue-500/10 text-blue-700 dark:text-blue-300">
                          {event.category}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                        <div>
                          <p className="text-sm text-muted-foreground">Date & Time</p>
                          <p className="text-sm">
                            {new Date(event.date).toLocaleDateString()} at {event.time}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Location</p>
                          <p className="text-sm">{event.location}</p>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Attendance</p>
                          <p className="text-sm">{event.attendees}/{event.capacity} registered</p>
                          <div className="w-full bg-muted rounded-full h-1.5 mt-1">
                            <div
                              className="bg-primary h-1.5 rounded-full"
                              style={{ width: `${(event.attendees / event.capacity) * 100}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="flex flex-col gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onNavigate('event-details', event.id)}
                      >
                        <Eye className="size-4 mr-2" />
                        View
                      </Button>
                      <Button variant="outline" size="sm">
                        <Edit className="size-4 mr-2" />
                        Edit
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDeleteEvent(event.id)}
                      >
                        <Trash2 className="size-4 mr-2 text-destructive" />
                        Delete
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="attendance" className="mt-6">
            <div className="space-y-4">
              {mockOrganizerEvents.map((event) => (
                <Card key={event.id} className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h4 className="mb-1">{event.title}</h4>
                      <p className="text-sm text-muted-foreground">
                        {event.attendees} attendees checked in
                      </p>
                    </div>
                    <Button variant="outline" size="sm">
                      <QrCode className="size-4 mr-2" />
                      Scan Tickets
                    </Button>
                  </div>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="p-4 bg-muted rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">Registered</p>
                      <p className="text-2xl">{event.attendees}</p>
                    </div>
                    <div className="p-4 bg-muted rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">Checked In</p>
                      <p className="text-2xl">{Math.floor(event.attendees * 0.8)}</p>
                    </div>
                    <div className="p-4 bg-muted rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">No Show</p>
                      <p className="text-2xl">{Math.floor(event.attendees * 0.2)}</p>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="analytics" className="mt-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="p-6">
                <h3 className="mb-4">Event Performance</h3>
                <div className="space-y-4">
                  {mockOrganizerEvents.map((event) => (
                    <div key={event.id}>
                      <div className="flex items-center justify-between text-sm mb-2">
                        <span>{event.title}</span>
                        <span className="text-muted-foreground">
                          {Math.round((event.attendees / event.capacity) * 100)}%
                        </span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-2">
                        <div
                          className="bg-primary h-2 rounded-full"
                          style={{ width: `${(event.attendees / event.capacity) * 100}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </Card>

              <Card className="p-6">
                <h3 className="mb-4">Quick Stats</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
                    <span className="text-muted-foreground">Most Popular Event</span>
                    <span>{mockOrganizerEvents[1]?.title}</span>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
                    <span className="text-muted-foreground">Avg. Registration Rate</span>
                    <span>62%</span>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
                    <span className="text-muted-foreground">Total Reach</span>
                    <span>{totalAttendees} students</span>
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
              Fill in the details to create a new event for your organization
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
                      You receive: ${(parseFloat(newEvent.price) * 0.95).toFixed(2)}
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