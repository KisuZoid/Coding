import { useState } from 'react';
import { ArrowLeft, Calendar, MapPin, Users, Clock, QrCode, Share2, Ticket, DollarSign, CreditCard } from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Separator } from './ui/separator';
import { toast } from 'sonner@2.0.3';
import type { User, Event } from '../App';

interface EventDetailsProps {
  eventId: string | null;
  onNavigate: (page: 'dashboard') => void;
  currentUser: User | null;
}

const mockEvent: Event = {
  id: '1',
  title: 'Tech Talk: AI in Education',
  description: 'Join us for an insightful discussion on how AI is transforming education. Our panel of experts will share their perspectives on the future of learning, ethical considerations, and practical applications of AI in the classroom. This event is perfect for students, educators, and anyone interested in the intersection of technology and education.',
  date: '2025-10-15',
  time: '18:00',
  location: 'Engineering Building, Room 301',
  organizerId: 'Computer Science Club',
  organizerName: 'Computer Science Club',
  category: 'Technology',
  image: 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800',
  attendees: 45,
  capacity: 100,
  isPaid: true,
  price: 25.00
};

export function EventDetails({ eventId, onNavigate, currentUser }: EventDetailsProps) {
  const [showQRDialog, setShowQRDialog] = useState(false);
  const [showPaymentDialog, setShowPaymentDialog] = useState(false);
  const [registered, setRegistered] = useState(false);
  const [cardNumber, setCardNumber] = useState('');
  const [cardExpiry, setCardExpiry] = useState('');
  const [cardCvv, setCardCvv] = useState('');
  const [cardName, setCardName] = useState('');
  const [processingPayment, setProcessingPayment] = useState(false);

  const platformFee = mockEvent.isPaid && mockEvent.price ? mockEvent.price * 0.05 : 0;
  const totalAmount = mockEvent.isPaid && mockEvent.price ? mockEvent.price + platformFee : 0;

  const handleRegister = () => {
    if (mockEvent.isPaid) {
      setShowPaymentDialog(true);
    } else {
      setRegistered(true);
      toast.success('Successfully registered for event!');
      setShowQRDialog(true);
    }
  };

  const handlePayment = async (e: React.FormEvent) => {
    e.preventDefault();
    setProcessingPayment(true);

    // Simulate payment processing
    setTimeout(() => {
      setProcessingPayment(false);
      setShowPaymentDialog(false);
      setRegistered(true);
      toast.success('Payment successful! Event registered.');
      setShowQRDialog(true);
    }, 2000);
  };

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href);
    toast.success('Event link copied to clipboard!');
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
            <Button
              variant="ghost"
              size="icon"
              onClick={handleShare}
            >
              <Share2 className="size-5" />
            </Button>
          </div>
        </div>
      </nav>

      {/* Event Details */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Image */}
        <div className="aspect-video bg-muted rounded-xl overflow-hidden mb-8 relative">
          <img
            src={mockEvent.image}
            alt={mockEvent.title}
            className="w-full h-full object-cover"
          />
          <Badge className={`absolute top-4 right-4 ${getCategoryColor(mockEvent.category)}`}>
            {mockEvent.category}
          </Badge>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            <div>
              <h1 className="mb-4">{mockEvent.title}</h1>
              <p className="text-muted-foreground">
                {mockEvent.description}
              </p>
            </div>

            <Card className="p-6">
              <h3 className="mb-4">Event Details</h3>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <Calendar className="size-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm text-muted-foreground">Date & Time</p>
                    <p>
                      {new Date(mockEvent.date).toLocaleDateString('en-US', {
                        weekday: 'long',
                        month: 'long',
                        day: 'numeric',
                        year: 'numeric'
                      })}
                    </p>
                    <p className="text-muted-foreground">{mockEvent.time}</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <MapPin className="size-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm text-muted-foreground">Location</p>
                    <p>{mockEvent.location}</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Users className="size-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm text-muted-foreground">Organizer</p>
                    <p>{mockEvent.organizer}</p>
                  </div>
                </div>
              </div>
            </Card>

            <Card className="p-6">
              <h3 className="mb-4">About the Event</h3>
              <p className="text-muted-foreground mb-4">
                This event will feature:
              </p>
              <ul className="space-y-2 text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="size-1.5 rounded-full bg-primary mt-2" />
                  <span>Panel discussion with industry experts</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="size-1.5 rounded-full bg-primary mt-2" />
                  <span>Interactive Q&A session</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="size-1.5 rounded-full bg-primary mt-2" />
                  <span>Networking opportunities</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="size-1.5 rounded-full bg-primary mt-2" />
                  <span>Light refreshments provided</span>
                </li>
              </ul>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <Card className="p-6">
              <div className="mb-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-muted-foreground">Attendees</span>
                  <span>{mockEvent.attendees}/{mockEvent.capacity}</span>
                </div>
                <div className="w-full bg-muted rounded-full h-2">
                  <div
                    className="bg-primary h-2 rounded-full"
                    style={{ width: `${(mockEvent.attendees / mockEvent.capacity) * 100}%` }}
                  />
                </div>
              </div>

              {registered ? (
                <div className="space-y-3">
                  <Button
                    className="w-full"
                    onClick={() => setShowQRDialog(true)}
                  >
                    <Ticket className="size-4 mr-2" />
                    View My Ticket
                  </Button>
                  <p className="text-center text-sm text-muted-foreground">
                    You're registered for this event
                  </p>
                </div>
              ) : (
                <Button className="flex-1" onClick={handleRegister}>
                  {mockEvent.isPaid ? (
                    <>
                      <DollarSign className="size-4 mr-2" />
                      Register (${mockEvent.price?.toFixed(2)})
                    </>
                  ) : (
                    <>
                      <Ticket className="size-4 mr-2" />
                      Register for Free
                    </>
                  )}
                </Button>
              )}
            </Card>

            <Card className="p-6">
              <h4 className="mb-4">Event Stats</h4>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Category</span>
                  <Badge className={getCategoryColor(mockEvent.category)}>
                    {mockEvent.category}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Spots Left</span>
                  <span>{mockEvent.capacity - mockEvent.attendees}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Status</span>
                  <Badge variant="outline" className="bg-green-500/10 text-green-700 dark:text-green-300">
                    Open
                  </Badge>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>

      {/* QR Code Dialog */}
      <Dialog open={showQRDialog} onOpenChange={setShowQRDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Your Event Ticket</DialogTitle>
            <DialogDescription>
              Show this QR code at the event entrance for check-in
            </DialogDescription>
          </DialogHeader>
          <div className="flex flex-col items-center py-6">
            <div className="size-64 bg-white p-6 rounded-xl mb-4">
              <div className="size-full bg-gradient-to-br from-primary/20 to-primary/5 rounded-lg flex items-center justify-center">
                <QrCode className="size-32 text-primary" />
              </div>
            </div>
            <h3 className="mb-2">{mockEvent.title}</h3>
            <p className="text-muted-foreground text-center mb-1">
              {new Date(mockEvent.date).toLocaleDateString('en-US', {
                month: 'long',
                day: 'numeric',
                year: 'numeric'
              })}
            </p>
            <p className="text-muted-foreground mb-6">{mockEvent.time} • {mockEvent.location}</p>
            {mockEvent.isPaid && (
              <div className="w-full p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
                <p className="text-sm text-center text-green-700 dark:text-green-300">
                  ✓ Paid ${mockEvent.price?.toFixed(2)}
                </p>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Payment Dialog */}
      <Dialog open={showPaymentDialog} onOpenChange={setShowPaymentDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Complete Payment</DialogTitle>
            <DialogDescription>
              Secure payment for {mockEvent.title}
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handlePayment} className="space-y-6">
            {/* Price Breakdown */}
            <div className="p-4 bg-muted rounded-lg space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>Event Price</span>
                <span>${mockEvent.price?.toFixed(2)}</span>
              </div>
              <div className="flex items-center justify-between text-sm text-muted-foreground">
                <span>Platform Fee (5%)</span>
                <span>${platformFee.toFixed(2)}</span>
              </div>
              <Separator className="my-2" />
              <div className="flex items-center justify-between font-medium">
                <span>Total</span>
                <span>${totalAmount.toFixed(2)}</span>
              </div>
            </div>

            {/* Payment Form */}
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="cardName">Cardholder Name</Label>
                <Input
                  id="cardName"
                  placeholder="John Doe"
                  value={cardName}
                  onChange={(e) => setCardName(e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="cardNumber">Card Number</Label>
                <div className="relative">
                  <CreditCard className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                  <Input
                    id="cardNumber"
                    placeholder="1234 5678 9012 3456"
                    value={cardNumber}
                    onChange={(e) => setCardNumber(e.target.value)}
                    className="pl-10"
                    maxLength={19}
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="cardExpiry">Expiry Date</Label>
                  <Input
                    id="cardExpiry"
                    placeholder="MM/YY"
                    value={cardExpiry}
                    onChange={(e) => setCardExpiry(e.target.value)}
                    maxLength={5}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="cardCvv">CVV</Label>
                  <Input
                    id="cardCvv"
                    placeholder="123"
                    value={cardCvv}
                    onChange={(e) => setCardCvv(e.target.value)}
                    maxLength={3}
                    type="password"
                    required
                  />
                </div>
              </div>
            </div>

            <div className="flex gap-3">
              <Button 
                type="button" 
                variant="outline" 
                className="flex-1"
                onClick={() => setShowPaymentDialog(false)}
                disabled={processingPayment}
              >
                Cancel
              </Button>
              <Button 
                type="submit" 
                className="flex-1"
                disabled={processingPayment}
              >
                {processingPayment ? 'Processing...' : `Pay $${totalAmount.toFixed(2)}`}
              </Button>
            </div>

            <p className="text-xs text-center text-muted-foreground">
              Payment secured by Stripe. Your card details are encrypted.
            </p>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}