import { useState } from 'react';
import { Calendar, QrCode, User, LogOut, Search, Filter, Grid, List, Ticket } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import type { User as UserType, Event } from '../App';

interface DashboardProps {
  onNavigate: (page: 'home' | 'event-details' | 'admin' | 'scan' | 'profile', eventId?: string) => void;
  currentUser: UserType | null;
  onLogout: () => void;
}

const mockEvents: Event[] = [
  {
    id: '1',
    title: 'Tech Talk: AI in Education',
    description: 'Join us for an insightful discussion on how AI is transforming education.',
    date: '2025-10-15',
    time: '18:00',
    location: 'Engineering Building, Room 301',
    organizer: 'Computer Science Club',
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
    organizer: 'Music Society',
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
    organizer: 'Career Services',
    category: 'Career',
    image: 'https://images.unsplash.com/photo-1511578314322-379afb476865?w=800',
    attendees: 156,
    capacity: 300
  },
  {
    id: '4',
    title: 'Yoga & Wellness Workshop',
    description: 'Learn mindfulness techniques and yoga for stress management.',
    date: '2025-10-22',
    time: '16:00',
    location: 'Recreation Center',
    organizer: 'Health & Wellness Club',
    category: 'Wellness',
    image: 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800',
    attendees: 28,
    capacity: 50
  },
  {
    id: '5',
    title: 'Startup Pitch Competition',
    description: 'Watch student entrepreneurs pitch their innovative business ideas.',
    date: '2025-10-25',
    time: '14:00',
    location: 'Business School Auditorium',
    organizer: 'Entrepreneurship Club',
    category: 'Business',
    image: 'https://images.unsplash.com/photo-1431540015161-0bf868a2d407?w=800',
    attendees: 89,
    capacity: 150
  },
  {
    id: '6',
    title: 'Art Exhibition Opening',
    description: 'Explore creative works by talented student artists.',
    date: '2025-10-28',
    time: '17:00',
    location: 'Art Gallery',
    organizer: 'Art Department',
    category: 'Arts',
    image: 'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=800',
    attendees: 62,
    capacity: 120
  }
];

export function Dashboard({ onNavigate, currentUser, onLogout }: DashboardProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  const filteredEvents = mockEvents.filter(event =>
    event.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    event.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
    event.organizer.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      'Technology': 'bg-blue-500/10 text-blue-700 dark:text-blue-300',
      'Entertainment': 'bg-purple-500/10 text-purple-700 dark:text-purple-300',
      'Career': 'bg-green-500/10 text-green-700 dark:text-green-300',
      'Wellness': 'bg-pink-500/10 text-pink-700 dark:text-pink-300',
      'Business': 'bg-orange-500/10 text-orange-700 dark:text-orange-300',
      'Arts': 'bg-indigo-500/10 text-indigo-700 dark:text-indigo-300'
    };
    return colors[category] || 'bg-gray-500/10 text-gray-700';
  };

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
              <Button
                variant="ghost"
                size="icon"
                onClick={() => onNavigate('scan')}
                title="Scan QR Code"
              >
                <QrCode className="size-5" />
              </Button>
              {currentUser?.role === 'admin' && (
                <Button
                  variant="ghost"
                  onClick={() => onNavigate('admin')}
                >
                  Admin Panel
                </Button>
              )}
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
        <div className="mb-8">
          <h1 className="mb-2">Welcome back, {currentUser?.name}!</h1>
          <p className="text-muted-foreground">
            Discover and manage your campus events
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-muted-foreground text-sm mb-1">Upcoming Events</p>
                <p className="text-2xl">{mockEvents.length}</p>
              </div>
              <Calendar className="size-8 text-muted-foreground" />
            </div>
          </Card>
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-muted-foreground text-sm mb-1">My Tickets</p>
                <p className="text-2xl">3</p>
              </div>
              <Ticket className="size-8 text-muted-foreground" />
            </div>
          </Card>
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-muted-foreground text-sm mb-1">Events Attended</p>
                <p className="text-2xl">12</p>
              </div>
              <QrCode className="size-8 text-muted-foreground" />
            </div>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="all" className="w-full">
          <TabsList>
            <TabsTrigger value="all">All Events</TabsTrigger>
            <TabsTrigger value="registered">My Events</TabsTrigger>
            <TabsTrigger value="past">Past Events</TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="mt-6">
            {/* Search and Filters */}
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                <Input
                  placeholder="Search events..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Button variant="outline" size="icon">
                <Filter className="size-4" />
              </Button>
              <div className="flex border border-border rounded-lg">
                <Button
                  variant={viewMode === 'grid' ? 'secondary' : 'ghost'}
                  size="icon"
                  onClick={() => setViewMode('grid')}
                  className="rounded-r-none"
                >
                  <Grid className="size-4" />
                </Button>
                <Button
                  variant={viewMode === 'list' ? 'secondary' : 'ghost'}
                  size="icon"
                  onClick={() => setViewMode('list')}
                  className="rounded-l-none"
                >
                  <List className="size-4" />
                </Button>
              </div>
            </div>

            {/* Events Grid/List */}
            <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' : 'space-y-4'}>
              {filteredEvents.map((event) => (
                <Card
                  key={event.id}
                  className="overflow-hidden cursor-pointer hover:shadow-lg transition-shadow"
                  onClick={() => onNavigate('event-details', event.id)}
                >
                  <div className="aspect-video bg-muted relative overflow-hidden">
                    <img
                      src={event.image}
                      alt={event.title}
                      className="w-full h-full object-cover"
                    />
                    <Badge className={`absolute top-3 right-3 ${getCategoryColor(event.category)}`}>
                      {event.category}
                    </Badge>
                  </div>
                  <div className="p-6">
                    <h3 className="mb-2">{event.title}</h3>
                    <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                      {event.description}
                    </p>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <Calendar className="size-4" />
                        {new Date(event.date).toLocaleDateString('en-US', { 
                          month: 'short', 
                          day: 'numeric',
                          year: 'numeric'
                        })} at {event.time}
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">{event.organizer}</span>
                        <span className="text-muted-foreground">
                          {event.attendees}/{event.capacity} attending
                        </span>
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="registered" className="mt-6">
            <div className="text-center py-12">
              <Ticket className="size-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="mb-2">No Registered Events</h3>
              <p className="text-muted-foreground">
                Browse events and register to see them here
              </p>
            </div>
          </TabsContent>

          <TabsContent value="past" className="mt-6">
            <div className="text-center py-12">
              <Calendar className="size-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="mb-2">No Past Events</h3>
              <p className="text-muted-foreground">
                Events you've attended will appear here
              </p>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
