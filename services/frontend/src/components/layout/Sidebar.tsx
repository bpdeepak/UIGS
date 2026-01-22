'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Network, Upload, AlertTriangle, Home, Settings } from 'lucide-react';
import clsx from 'clsx';

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: Home },
  { href: '/dashboard/graph', label: 'Identity Graph', icon: Network },
  { href: '/dashboard/upload', label: 'Upload VC', icon: Upload },
  { href: '/dashboard/conflicts', label: 'Conflicts', icon: AlertTriangle },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-gray-900 text-white min-h-screen p-4">
      <div className="mb-8">
        <h1 className="text-xl font-bold text-blue-400">UIGS</h1>
        <p className="text-xs text-gray-400">Unified Identity Graph</p>
      </div>

      <nav className="space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                'flex items-center gap-3 px-4 py-2 rounded-lg transition-colors',
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              )}
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="absolute bottom-4 left-4 right-4">
        <Link
          href="/dashboard/settings"
          className="flex items-center gap-3 px-4 py-2 text-gray-400 hover:text-white transition-colors"
        >
          <Settings size={20} />
          <span>Settings</span>
        </Link>
      </div>
    </aside>
  );
}
