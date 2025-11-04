'use client';

import { Sidebar } from '@/components/dashboard/sidebar';
import { Header } from '@/components/dashboard/header';
import { ReportForm } from '@/components/reports/report-form';
import { usePathname } from 'next/navigation';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const isMapPage = pathname === '/dashboard/map' || pathname === '/dashboard/mood';
  
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header />
        <main className={`flex-1 bg-background ${isMapPage ? 'overflow-hidden flex flex-col' : 'overflow-auto'}`}>
          {children}
        </main>
      </div>
      <ReportForm />
    </div>
  );
}
