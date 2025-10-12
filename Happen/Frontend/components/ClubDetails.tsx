import { ArrowLeft, Users, Calendar, Heart, Bell } from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { toast } from 'sonner@2.0.3';
import { useState } from 'react';
import type { User, Event } from '../App';

interface ClubDetailsProps {
  clubId: string | null;
  onNavigate: (page: any, id?: string) => void;
  currentUser: User | null;
}

const mockClub = {
  id: 'club-1',
  name: 'Computer Science Club',
  description: 'We are a community of students passionate about technology, coding, and innovation. Join us for workshops, hackathons, tech talks, and networking events with industry professionals.',
  category: 'Technology',
  image: 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=800',
  coverImage: 'https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=1200',
  memberCount: 234,
  foundedYear: 2018,
  email: 'csclub@college.edu',
  website: 'https://csclub.college.edu',
  socials: {
    instagram: '@csclub',
    discord: 'discord.gg/csclub'
  }
};

const mockClubEvents: Event[] = [
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
    clubName: 'Computer Science Club'
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
    capacity: 150,
    clubId: 'club-1',
    clubName: 'Computer Science Club'
  }
];

const mockPosts = [
  {
    id: '1',
    content: 'Excited to announce our upcoming Hackathon 2025! 🎉 Register now to secure your spot. Limited seats available!',
    date: '2025-10-10',
    likes: 45,
    image: 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=600'
  },
  {
    id: '2',
    content: 'Great turnout at yesterday\'s AI workshop! Thank you to everyone who attended. Stay tuned for more sessions.',
    date: '2025-10-08',
    likes: 32
  },
  {
    id: '3',
    content: 'New members welcome! Join us every Wednesday at 5 PM for our weekly meetups. All skill levels are welcome! 💻',
    date: '2025-10-05',
    likes: 28
  }
];

export function ClubDetails({ clubId, onNavigate, currentUser }: ClubDetailsProps) {
  const [isMember, setIsMember] = useState(false);
  const [notificationsEnabled, setNotificationsEnabled] = useState(false);

  const handleJoinClub = () => {
    setIsMember(!isMember);
    toast.success(isMember ? 'Left club successfully' : 'Joined club successfully!');
  };

  const handleToggleNotifications = () => {
    setNotificationsEnabled(!notificationsEnabled);
    toast.success(notificationsEnabled ? 'Notifications disabled' : 'Notifications enabled');
  };

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

      {/* Cover Image */}
      <div className="h-64 bg-muted relative overflow-hidden">
        <img
          src={mockClub.coverImage}
          alt={mockClub.name}
          className="w-full h-full object-cover"
        />
      </div>

      {/* Main Content */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Club Header */}
        <div className="flex items-start gap-6 mb-8 -mt-24 relative">
          <div className="size-40 bg-white dark:bg-gray-900 rounded-2xl border-4 border-background overflow-hidden flex-shrink-0">
            <img
              src={mockClub.image}
              alt={mockClub.name}
              className="w-full h-full object-cover"
            />
          </div>
          <div className="flex-1 pt-20">
            <div className="flex items-start justify-between gap-4 mb-4">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <h1>{mockClub.name}</h1>
                  <Badge className={getCategoryColor(mockClub.category)}>
                    {mockClub.category}
                  </Badge>
                </div>
                <div className="flex items-center gap-4 text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <Users className="size-4" />
                    {mockClub.memberCount} members
                  </span>
                  <span>Founded {mockClub.foundedYear}</span>
                </div>
              </div>
              <div className="flex gap-2">
                <Button
                  variant={notificationsEnabled ? 'default' : 'outline'}
                  size="icon"
                  onClick={handleToggleNotifications}
                  title={notificationsEnabled ? 'Disable notifications' : 'Enable notifications'}
                >
                  <Bell className="size-4" />
                </Button>
                <Button
                  variant={isMember ? 'outline' : 'default'}
                  onClick={handleJoinClub}
                >
                  {isMember ? (
                    <>
                      <Heart className="size-4 mr-2 fill-current" />
                      Joined
                    </>
                  ) : (
                    <>
                      <Heart className="size-4 mr-2" />
                      Join Club
                    </>
                  )}
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="about" className="w-full">
          <TabsList>
            <TabsTrigger value="about">About</TabsTrigger>
            <TabsTrigger value="events">Events</TabsTrigger>
            <TabsTrigger value="posts">Posts</TabsTrigger>
          </TabsList>

          <TabsContent value="about" className="mt-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-6">
                <Card className="p-6">
                  <h3 className="mb-4">About the Club</h3>
                  <p className="text-muted-foreground">
                    {mockClub.description}
                  </p>
                </Card>

                <Card className="p-6">
                  <h3 className="mb-4">What We Do</h3>
                  <ul className="space-y-3">
                    <li className="flex items-start gap-2">
                      <span className="size-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                      <span className="text-muted-foreground">Weekly coding workshops and tutorials</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="size-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                      <span className="text-muted-foreground">Hackathons and coding competitions</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="size-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                      <span className="text-muted-foreground">Tech talks with industry professionals</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="size-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                      <span className="text-muted-foreground">Networking and career development events</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="size-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                      <span className="text-muted-foreground">Open source project collaborations</span>
                    </li>
                  </ul>
                </Card>
              </div>

              <div className="space-y-6">
                <Card className="p-6">
                  <h4 className="mb-4">Contact</h4>
                  <div className="space-y-3 text-sm">
                    <div>
                      <p className="text-muted-foreground mb-1">Email</p>
                      <p>{mockClub.email}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground mb-1">Website</p>
                      <a href={mockClub.website} className="text-primary hover:underline">
                        {mockClub.website}
                      </a>
                    </div>
                    <div>
                      <p className="text-muted-foreground mb-1">Instagram</p>
                      <p>{mockClub.socials.instagram}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground mb-1">Discord</p>
                      <p>{mockClub.socials.discord}</p>
                    </div>
                  </div>
                </Card>

                <Card className="p-6">
                  <h4 className="mb-4">Stats</h4>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-muted-foreground text-sm">Total Members</span>
                      <span>{mockClub.memberCount}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-muted-foreground text-sm">Events Hosted</span>
                      <span>42</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-muted-foreground text-sm">Upcoming Events</span>
                      <span>{mockClubEvents.length}</span>
                    </div>
                  </div>
                </Card>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="events" className="mt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {mockClubEvents.map((event) => (
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
                        <span className="text-muted-foreground">{event.location}</span>
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

          <TabsContent value="posts" className="mt-6">
            <div className="space-y-4">
              {mockPosts.map((post) => (
                <Card key={post.id} className="p-6">
                  <div className="flex items-start gap-4 mb-4">
                    <div className="size-12 bg-muted rounded-full overflow-hidden flex-shrink-0">
                      <img
                        src={mockClub.image}
                        alt={mockClub.name}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <div className="flex-1">
                      <h4 className="mb-1">{mockClub.name}</h4>
                      <p className="text-sm text-muted-foreground">
                        {new Date(post.date).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric'
                        })}
                      </p>
                    </div>
                  </div>
                  <p className="text-muted-foreground mb-4">{post.content}</p>
                  {post.image && (
                    <div className="aspect-video bg-muted rounded-lg overflow-hidden mb-4">
                      <img
                        src={post.image}
                        alt="Post"
                        className="w-full h-full object-cover"
                      />
                    </div>
                  )}
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <button className="flex items-center gap-2 hover:text-foreground transition-colors">
                      <Heart className="size-4" />
                      {post.likes}
                    </button>
                  </div>
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
