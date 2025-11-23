/**
 * RBAC Utility Tests
 */

import { RBAC } from '@/lib/permissions/rbac';
import { Role, Permission } from '@/lib/permissions';

describe('RBAC', () => {
  describe('hasPermission', () => {
    it('admin has all permissions', () => {
      expect(RBAC.hasPermission(Role.ADMIN, Permission.VIEW_ADMIN)).toBe(true);
      expect(RBAC.hasPermission(Role.ADMIN, Permission.MANAGE_USERS)).toBe(true);
      expect(RBAC.hasPermission(Role.ADMIN, Permission.VIEW_ANALYTICS)).toBe(true);
    });

    it('user has limited permissions', () => {
      expect(RBAC.hasPermission(Role.USER, Permission.VIEW_ANALYTICS)).toBe(true);
      expect(RBAC.hasPermission(Role.USER, Permission.MANAGE_USERS)).toBe(false);
      expect(RBAC.hasPermission(Role.USER, Permission.VIEW_ADMIN)).toBe(false);
    });

    it('viewer has minimal permissions', () => {
      expect(RBAC.hasPermission(Role.VIEWER, Permission.VIEW_ANALYTICS)).toBe(true);
      expect(RBAC.hasPermission(Role.VIEWER, Permission.CREATE_REPORTS)).toBe(false);
      expect(RBAC.hasPermission(Role.VIEWER, Permission.MANAGE_USERS)).toBe(false);
    });
  });

  describe('hasAnyPermission', () => {
    it('returns true if user has at least one permission', () => {
      expect(
        RBAC.hasAnyPermission(Role.USER, [
          Permission.VIEW_ANALYTICS,
          Permission.MANAGE_USERS,
        ])
      ).toBe(true);
    });

    it('returns false if user has none of the permissions', () => {
      expect(
        RBAC.hasAnyPermission(Role.VIEWER, [
          Permission.MANAGE_USERS,
          Permission.DELETE_REPORTS,
        ])
      ).toBe(false);
    });
  });

  describe('hasAllPermissions', () => {
    it('returns true if user has all permissions', () => {
      expect(
        RBAC.hasAllPermissions(Role.ADMIN, [
          Permission.VIEW_ADMIN,
          Permission.MANAGE_USERS,
        ])
      ).toBe(true);
    });

    it('returns false if user lacks any permission', () => {
      expect(
        RBAC.hasAllPermissions(Role.USER, [
          Permission.VIEW_ANALYTICS,
          Permission.MANAGE_USERS,
        ])
      ).toBe(false);
    });
  });
});
