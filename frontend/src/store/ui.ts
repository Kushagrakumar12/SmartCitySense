import { create } from 'zustand';

interface UIState {
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
  notificationsPanelOpen: boolean;
  reportFormOpen: boolean;
  subscriptionsPanelOpen: boolean;
  toggleTheme: () => void;
  toggleSidebar: () => void;
  toggleNotificationsPanel: () => void;
  toggleReportForm: () => void;
  toggleSubscriptionsPanel: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  theme: 'light',
  sidebarOpen: true,
  notificationsPanelOpen: false,
  reportFormOpen: false,
  subscriptionsPanelOpen: false,
  toggleTheme: () =>
    set((state) => {
      const newTheme = state.theme === 'light' ? 'dark' : 'light';
      if (typeof window !== 'undefined') {
        document.documentElement.classList.toggle('dark', newTheme === 'dark');
        localStorage.setItem('theme', newTheme);
      }
      return { theme: newTheme };
    }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  toggleNotificationsPanel: () =>
    set((state) => ({ notificationsPanelOpen: !state.notificationsPanelOpen })),
  toggleReportForm: () => set((state) => ({ reportFormOpen: !state.reportFormOpen })),
  toggleSubscriptionsPanel: () =>
    set((state) => ({ subscriptionsPanelOpen: !state.subscriptionsPanelOpen })),
}));
