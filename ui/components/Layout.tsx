'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ReactNode } from 'react';

const navigation = [
    { name: 'Dashboard', href: '/', icon: '📊' },
    { name: 'Signals', href: '/signals', icon: '📡' },
    { name: 'Agent', href: '/agent', icon: '🤖' },
    { name: 'Actions', href: '/actions', icon: '⚡' },
    { name: 'Explain', href: '/explain', icon: '📖' },
    { name: 'Incidents', href: '/incidents', icon: '🚨' },
    { name: 'Knowledge', href: '/knowledge', icon: '💡' },
];

export default function Layout({ children }: { children: ReactNode }) {
    const pathname = usePathname();

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow-sm border-b border-gray-200">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center py-4">
                        <div className="flex items-center space-x-3">
                            <div className="text-2xl">🛡️</div>
                            <div>
                                <h1 className="text-xl font-bold text-gray-900">
                                    Self-Healing Support Supervisor
                                </h1>
                                <p className="text-sm text-gray-600">Agentic AI System</p>
                            </div>
                        </div>
                        <div className="flex items-center space-x-2">
                            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                <span className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
                                System Active
                            </span>
                        </div>
                    </div>
                </div>
            </header>

            {/* Navigation */}
            <nav className="bg-white border-b border-gray-200">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex space-x-1">
                        {navigation.map((item) => {
                            const isActive = pathname === item.href;
                            return (
                                <Link
                                    key={item.name}
                                    href={item.href}
                                    className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${isActive
                                            ? 'border-blue-600 text-blue-600'
                                            : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
                                        }`}
                                >
                                    <span className="mr-2">{item.icon}</span>
                                    {item.name}
                                </Link>
                            );
                        })}
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {children}
            </main>

            {/* Footer */}
            <footer className="mt-12 border-t border-gray-200 bg-white">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                    <div className="flex justify-between items-center text-sm text-gray-600">
                        <div>
                            <span className="font-medium">OBSERVE</span> →{' '}
                            <span className="font-medium">REASON</span> →{' '}
                            <span className="font-medium">DECIDE</span> →{' '}
                            <span className="font-medium">ACT</span> →{' '}
                            <span className="font-medium">EXPLAIN</span>
                        </div>
                        <div>v0.1.0</div>
                    </div>
                </div>
            </footer>
        </div>
    );
}
