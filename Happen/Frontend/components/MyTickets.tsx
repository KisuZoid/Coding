import { ArrowLeft, QrCode, Calendar, MapPin, Download } from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { useState } from 'react';
import type { User } from '../App';

interface MyTicketsProps {
  onNavigate: (page: 'dashboard') => void;
  currentUser: User | null;
}

const mockTickets = [
  {
    id: 'ticket-1',
    eventId: '1',
    eventTitle: 'Tech Talk: AI in Education',
    date: '2025-10-15',
    time: '18:00',
    location: 'Engineering Building, Room 301',
    organizer: 'Computer Science Club',
    qrCode: 'QR-001-ABC123',
    status: 'active' as const,
    image: 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800'
  },
  {
    id: 'ticket-2',
    eventId: '2',
    eventTitle: 'Annual Music Festival',
    date: '2025-10-18',
    time: '19:00',
    location: 'Campus Auditorium',
    organizer: 'Music Society',
    qrCode: 'QR-002-DEF456',
    status: 'active' as const,
    image: 'https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=800'
  },
  {
    id: 'ticket-3',
    eventId: '3',
    eventTitle: 'Career Fair 2025',
    date: '2025-09-20',
    time: '10:00',
    location: 'Student Center',
    organizer: 'Career Services',
    qrCode: 'QR-003-GHI789',
    status: 'used' as const,
    image: 'https://images.unsplash.com/photo-1511578314322-379afb476865?w=800'
  }
];

export function MyTickets({ onNavigate, currentUser }: MyTicketsProps) {
  const [selectedTicket, setSelectedTicket] = useState<typeof mockTickets[0] | null>(null);
  const [showQRDialog, setShowQRDialog] = useState(false);

  const handleViewTicket = (ticket: typeof mockTickets[0]) => {
    setSelectedTicket(ticket);
    setShowQRDialog(true);
  };

  const activeTickets = mockTickets.filter(t => t.status === 'active');
  const usedTickets = mockTickets.filter(t => t.status === 'used');

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
        <div className="mb-8">
          <h1 className="mb-2">My Tickets</h1>
          <p className="text-muted-foreground">
            View and manage your event tickets
          </p>
        </div>

        {/* Active Tickets */}
        <div className="mb-8">
          <h2 className="mb-4">Upcoming Events</h2>
          {activeTickets.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {activeTickets.map((ticket) => (
                <Card key={ticket.id} className="overflow-hidden">
                  <div className="aspect-video bg-muted relative overflow-hidden">
                    <img
                      src={ticket.image}
                      alt={ticket.eventTitle}
                      className="w-full h-full object-cover"
                    />
                    <Badge className="absolute top-3 right-3 bg-green-500/90 text-white">
                      Active
                    </Badge>
                  </div>
                  <div className="p-6">
                    <h3 className="mb-3">{ticket.eventTitle}</h3>
                    <div className="space-y-2 mb-4">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Calendar className="size-4" />
                        {new Date(ticket.date).toLocaleDateString('en-US', {
                          weekday: 'short',
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric'
                        })} at {ticket.time}
                      </div>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <MapPin className="size-4" />
                        {ticket.location}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        className="flex-1"
                        onClick={() => handleViewTicket(ticket)}
                      >
                        <QrCode className="size-4 mr-2" />
                        View QR Code
                      </Button>
                      <Button variant="outline" size="icon">
                        <Download className="size-4" />
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="p-12">
              <div className="text-center">
                <QrCode className="size-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="mb-2">No Upcoming Tickets</h3>
                <p className="text-muted-foreground mb-6">
                  Register for events to get tickets
                </p>
                <Button onClick={() => onNavigate('dashboard')}>
                  Browse Events
                </Button>
              </div>
            </Card>
          )}
        </div>

        {/* Past Tickets */}
        <div>
          <h2 className="mb-4">Past Events</h2>
          {usedTickets.length > 0 ? (
            <div className="space-y-3">
              {usedTickets.map((ticket) => (
                <Card key={ticket.id} className="p-4">
                  <div className="flex items-center gap-4">
                    <div className="size-16 bg-muted rounded-lg overflow-hidden flex-shrink-0">
                      <img
                        src={ticket.image}
                        alt={ticket.eventTitle}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4 mb-1">
                        <h4>{ticket.eventTitle}</h4>
                        <Badge variant="outline" className="bg-gray-500/10 text-gray-700 dark:text-gray-300">
                          Used
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {new Date(ticket.date).toLocaleDateString()} • {ticket.location}
                      </p>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="p-8">
              <p className="text-center text-muted-foreground">
                No past events
              </p>
            </Card>
          )}
        </div>
      </div>

      {/* QR Code Dialog */}
      <Dialog open={showQRDialog} onOpenChange={setShowQRDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Event Ticket</DialogTitle>
            <DialogDescription>
              Present this QR code at the event entrance
            </DialogDescription>
          </DialogHeader>
          {selectedTicket && (
            <div className="flex flex-col items-center py-6">
              <div className="size-64 bg-white p-6 rounded-xl mb-4">
                <div className="size-full bg-gradient-to-br from-primary/20 to-primary/5 rounded-lg flex items-center justify-center">
                  <QrCode className="size-32 text-primary" />
                </div>
              </div>
              <h3 className="mb-2 text-center">{selectedTicket.eventTitle}</h3>
              <p className="text-muted-foreground text-center mb-1">
                {new Date(selectedTicket.date).toLocaleDateString('en-US', {
                  month: 'long',
                  day: 'numeric',
                  year: 'numeric'
                })}
              </p>
              <p className="text-muted-foreground text-center mb-4">
                {selectedTicket.time} • {selectedTicket.location}
              </p>
              <div className="w-full p-4 bg-muted rounded-lg mb-4">
                <p className="text-sm text-muted-foreground mb-1">Ticket ID</p>
                <p className="font-mono text-sm">{selectedTicket.qrCode}</p>
              </div>
              <Button variant="outline" className="w-full mt-4">
                <Download className="size-4 mr-2" />
                Download Ticket
              </Button>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}