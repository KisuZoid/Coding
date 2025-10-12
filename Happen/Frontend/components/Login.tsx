import { useState } from 'react';
import { Calendar, Mail, Lock, ArrowLeft, UserCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card } from './ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { toast } from 'sonner@2.0.3';
import type { User } from '../App';

interface LoginProps {
  onNavigate: (page: 'home' | 'register' | 'dashboard' | 'password-reset') => void;
  onLogin: (user: User) => void;
}

export function Login({ onNavigate, onLogin }: LoginProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [selectedRole, setSelectedRole] = useState<'auto' | 'admin' | 'organizer' | 'user'>('auto');
  const [loading, setLoading] = useState(false);

  // Auto-detect role from email
  const detectRoleFromEmail = (emailValue: string): 'admin' | 'organizer' | 'user' => {
    const lowerEmail = emailValue.toLowerCase();
    if (lowerEmail.includes('admin')) {
      return 'admin';
    } else if (lowerEmail.includes('organizer') || lowerEmail.includes('org')) {
      return 'organizer';
    }
    return 'user';
  };

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newEmail = e.target.value;
    setEmail(newEmail);
    
    // Auto-detect role if in auto mode
    if (selectedRole === 'auto') {
      // This will trigger visual feedback in the UI
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    // Simulate API call
    setTimeout(() => {
      // Determine final role
      let role: 'admin' | 'organizer' | 'user';
      
      if (selectedRole === 'auto') {
        role = detectRoleFromEmail(email);
      } else {
        role = selectedRole;
      }

      const mockUser: User = {
        id: '1',
        email: email,
        name: email.split('@')[0],
        role: role,
        verified: true,
        organizationId: role === 'organizer' ? 'org-1' : undefined
      };

      onLogin(mockUser);
      toast.success(`Welcome back as ${role}!`);
      setLoading(false);
    }, 1000);
  };

  const detectedRole = selectedRole === 'auto' ? detectRoleFromEmail(email) : selectedRole;

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <div className="border-b border-border">
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
          </div>
        </div>
      </div>

      {/* Login Form */}
      <div className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">
          <button
            onClick={() => onNavigate('home')}
            className="flex items-center gap-2 text-muted-foreground hover:text-foreground mb-8 transition-colors"
          >
            <ArrowLeft className="size-4" />
            Back to home
          </button>

          <Card className="p-8">
            <div className="mb-8">
              <h1 className="mb-2">Welcome Back</h1>
              <p className="text-muted-foreground">
                Sign in to your account to continue
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="you@college.edu"
                    value={email}
                    onChange={handleEmailChange}
                    className="pl-10"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="role">Login As</Label>
                <Select value={selectedRole} onValueChange={(value: any) => setSelectedRole(value)}>
                  <SelectTrigger>
                    <div className="flex items-center gap-2">
                      <UserCircle className="size-4" />
                      <SelectValue />
                    </div>
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="auto">
                      Auto-detect from email {email && `(${detectedRole})`}
                    </SelectItem>
                    <SelectItem value="user">Student / User</SelectItem>
                    <SelectItem value="organizer">Club Organizer</SelectItem>
                    <SelectItem value="admin">Administrator</SelectItem>
                  </SelectContent>
                </Select>
                {selectedRole === 'auto' && email && (
                  <p className="text-sm text-muted-foreground">
                    Detected role: <span className="capitalize font-medium text-foreground">{detectedRole}</span>
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="password">Password</Label>
                  <button
                    type="button"
                    className="text-sm text-primary hover:underline"
                    onClick={() => onNavigate('password-reset')}
                  >
                    Forgot password?
                  </button>
                </div>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                  <Input
                    id="password"
                    type="password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="pl-10"
                    required
                  />
                </div>
              </div>

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? 'Signing in...' : 'Sign In'}
              </Button>
            </form>

            <div className="mt-6 text-center text-sm">
              <span className="text-muted-foreground">Don't have an account? </span>
              <button
                onClick={() => onNavigate('register')}
                className="text-primary hover:underline"
              >
                Sign up
              </button>
            </div>
          </Card>

          <div className="mt-6 p-4 bg-muted rounded-lg">
            <p className="text-sm text-muted-foreground mb-2">Quick Tip:</p>
            <p className="text-sm">
              Email with "admin" → Admin access<br/>
              Email with "organizer" → Organizer access<br/>
              Other emails → User access
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}