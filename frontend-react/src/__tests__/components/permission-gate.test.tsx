/**
 * PermissionGate Component Tests
 */

import { render, screen } from '@testing-library/react';
import { PermissionGate } from '@/components/permissions/PermissionGate';
import { Permission } from '@/lib/permissions';
import { useAuthStore } from '@/store/auth.store';

// Mock the auth store
jest.mock('@/store/auth.store');

describe('PermissionGate', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders children when user has permission', () => {
    (useAuthStore as unknown as jest.Mock).mockReturnValue({
      user: { role: 'admin' },
    });

    render(
      <PermissionGate permission={Permission.VIEW_ADMIN}>
        <div>Admin Content</div>
      </PermissionGate>
    );

    expect(screen.getByText('Admin Content')).toBeInTheDocument();
  });

  it('renders fallback when user lacks permission', () => {
    (useAuthStore as unknown as jest.Mock).mockReturnValue({
      user: { role: 'viewer' },
    });

    render(
      <PermissionGate 
        permission={Permission.MANAGE_USERS}
        fallback={<div>Access Denied</div>}
      >
        <div>Admin Content</div>
      </PermissionGate>
    );

    expect(screen.queryByText('Admin Content')).not.toBeInTheDocument();
    expect(screen.getByText('Access Denied')).toBeInTheDocument();
  });

  it('handles multiple permissions with requireAll', () => {
    (useAuthStore as unknown as jest.Mock).mockReturnValue({
      user: { role: 'admin' },
    });

    render(
      <PermissionGate 
        permission={[Permission.VIEW_ADMIN, Permission.MANAGE_USERS]}
        requireAll
      >
        <div>Admin Content</div>
      </PermissionGate>
    );

    expect(screen.getByText('Admin Content')).toBeInTheDocument();
  });
});
