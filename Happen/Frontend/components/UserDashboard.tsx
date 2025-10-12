import { useState } from 'react';
import { Calendar, QrCode, User, LogOut, Search, Filter, Grid, List, Ticket, Users as UsersIcon } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import type { User as UserType, Event, Club } from '../App';

interface UserDashboardProps {
  onNavigate: (page: any, id?: string) => void;
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
    organizerId: 'org-1',
    organizerName: 'Computer Science Club',
    category: 'Technology',
    image: 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800',
    attendees: 45,
    capacity: 100,
    clubId: 'club-1',
    clubName: 'Computer Science Club',
    isPaid: true,
    price: 25.00
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
    capacity: 500,
    clubId: 'club-2',
    clubName: 'Music Society',
    isPaid: true,
    price: 15.00
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
    capacity: 300,
    isPaid: false
  },
  {
    id: '4',
    title: 'Yoga & Wellness Workshop',
    description: 'Learn mindfulness techniques and yoga for stress management.',
    date: '2025-10-22',
    time: '16:00',
    location: 'Recreation Center',
    organizerId: 'org-4',
    organizerName: 'Health & Wellness Club',
    category: 'Wellness',
    image: 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800',
    attendees: 28,
    capacity: 50,
    clubId: 'club-4',
    clubName: 'Health & Wellness Club',
    isPaid: false
  }
];

const mockClubs: Club[] = [
  {
    id: 'club-1',
    name: 'Computer Science Club',
    description: 'Exploring technology and innovation together',
    category: 'Technology',
    image: 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=400',
    memberCount: 234,
    events: 12
  },
  {
    id: 'club-2',
    name: 'Music Society',
    description: 'Celebrating musical talent and creativity',
    category: 'Arts',
    image: 'https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=400',
    memberCount: 189,
    events: 8
  },
  {
    id: 'club-4',
    name: 'Health & Wellness Club',
    description: 'Promoting physical and mental wellbeing',
    category: 'Wellness',
    image: 'https://images.unsplash.com/photo-1545205597-3d9d02c29597?w=400',
    memberCount: 156,
    events: 15
  }
];

export function UserDashboard({ onNavigate, currentUser, onLogout }: UserDashboardProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  const filteredEvents = mockEvents.filter(event =>
    event.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    event.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
    event.organizerName.toLowerCase().includes(searchQuery.toLowerCase())
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
              <Button
                variant="ghost"
                onClick={() => onNavigate('my-tickets')}
              >
                <Ticket className="size-4 mr-2" />
                My Tickets
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
        <div className="mb-8">
          <h1 className="mb-2">Welcome back, {currentUser?.name}!</h1>
          <p className="text-muted-foreground">
            Discover events and connect with clubs
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
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
                <p className="text-muted-foreground text-sm mb-1">Clubs Joined</p>
                <p className="text-2xl">5</p>
              </div>
              <UsersIcon className="size-8 text-muted-foreground" />
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
        <Tabs defaultValue="events" className="w-full">
          <TabsList>
            <TabsTrigger value="events">Browse Events</TabsTrigger>
            <TabsTrigger value="clubs">Clubs</TabsTrigger>
            <TabsTrigger value="registered">My Events</TabsTrigger>
          </TabsList>

          <TabsContent value="events" className="mt-6">
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

            {/* Events Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
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
                    <div className="absolute top-3 right-3 flex gap-2">
                      <Badge className={getCategoryColor(event.category)}>
                        {event.category}
                      </Badge>
                      {event.isPaid ? (
                        <Badge className="bg-green-500/90 text-white">
                          ${event.price?.toFixed(2)}
                        </Badge>
                      ) : (
                        <Badge className="bg-blue-500/90 text-white">
                          Free
                        </Badge>
                      )}
                    </div>
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
                        <span className="text-muted-foreground">{event.organizerName}</span>
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

          <TabsContent value="clubs" className="mt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {mockClubs.map((club) => (
                <Card
                  key={club.id}
                  className="overflow-hidden cursor-pointer hover:shadow-lg transition-shadow"
                  onClick={() => onNavigate('club-details', club.id)}
                >
                  <div className="aspect-video bg-muted relative overflow-hidden">
                    <img
                      src={club.image}
                      alt={club.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="p-6">
                    <h3 className="mb-2">{club.name}</h3>
                    <p className="text-sm text-muted-foreground mb-4">
                      {club.description}
                    </p>
                    <div className="flex items-center justify-between text-sm text-muted-foreground">
                      <span>{club.memberCount} members</span>
                      <span>{club.events} events</span>
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
              <p className="text-muted-foreground mb-6">
                Browse events and register to see them here
              </p>
              <Button onClick={() => onNavigate('dashboard')}>
                Browse Events
              </Button>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}