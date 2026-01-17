import { useAuthStore } from '../auth/store'

export const useRBAC = (requiredRoles: string[]) => {
  const { user } = useAuthStore()
  const hasAccess = !!user && requiredRoles.includes(user.cargo)
  return { hasAccess }
}

