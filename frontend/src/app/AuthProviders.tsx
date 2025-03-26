'use client';

import { AuthProvider } from '@/lib/auth/AuthContext';
import { ReactNode } from 'react';

export function AuthProviders({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      {children}
    </AuthProvider>
  );
}
