// Shared UI components for the Supervisor Dashboard

import { ReactNode } from 'react';

interface BadgeProps {
    variant?: 'low' | 'medium' | 'high' | 'success' | 'warning' | 'error' | 'info';
    children: ReactNode;
    className?: string;
}

export function Badge({ variant = 'info', children, className = '' }: BadgeProps) {
    const variants = {
        low: 'bg-green-100 text-green-800 border-green-200',
        medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
        high: 'bg-red-100 text-red-800 border-red-200',
        success: 'bg-green-100 text-green-800 border-green-200',
        warning: 'bg-yellow-100 text-yellow-800 border-yellow-200',
        error: 'bg-red-100 text-red-800 border-red-200',
        info: 'bg-blue-100 text-blue-800 border-blue-200',
    };

    return (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${variants[variant]} ${className}`}>
            {children}
        </span>
    );
}

interface CardProps {
    title?: string;
    children: ReactNode;
    className?: string;
    action?: ReactNode;
}

export function Card({ title, children, className = '', action }: CardProps) {
    return (
        <div className={`bg-white rounded-lg shadow-sm border border-gray-200 ${className}`}>
            {title && (
                <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                    <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
                    {action && <div>{action}</div>}
                </div>
            )}
            <div className="px-6 py-4">{children}</div>
        </div>
    );
}

interface ProgressBarProps {
    value: number; // 0-100
    label?: string;
    showPercentage?: boolean;
    variant?: 'low' | 'medium' | 'high';
}

export function ProgressBar({ value, label, showPercentage = true, variant }: ProgressBarProps) {
    const getColor = () => {
        if (variant) {
            return variant === 'high' ? 'bg-red-500' : variant === 'medium' ? 'bg-yellow-500' : 'bg-green-500';
        }
        if (value >= 75) return 'bg-green-500';
        if (value >= 50) return 'bg-yellow-500';
        return 'bg-red-500';
    };

    return (
        <div className="w-full">
            {label && (
                <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700">{label}</span>
                    {showPercentage && (
                        <span className="text-sm font-medium text-gray-700">{value}%</span>
                    )}
                </div>
            )}
            <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div
                    className={`h-2.5 rounded-full transition-all duration-300 ${getColor()}`}
                    style={{ width: `${value}%` }}
                />
            </div>
        </div>
    );
}

interface AlertProps {
    variant?: 'success' | 'warning' | 'error' | 'info';
    title?: string;
    children: ReactNode;
    className?: string;
}

export function Alert({ variant = 'info', title, children, className = '' }: AlertProps) {
    const variants = {
        success: 'bg-green-50 border-green-200 text-green-900',
        warning: 'bg-yellow-50 border-yellow-200 text-yellow-900',
        error: 'bg-red-50 border-red-200 text-red-900',
        info: 'bg-blue-50 border-blue-200 text-blue-900',
    };

    const icons = {
        success: '✓',
        warning: '⚠',
        error: '✕',
        info: 'ℹ',
    };

    return (
        <div className={`border rounded-lg p-4 ${variants[variant]} ${className}`}>
            <div className="flex items-start">
                <span className="text-xl mr-3">{icons[variant]}</span>
                <div className="flex-1">
                    {title && <h4 className="font-semibold mb-1">{title}</h4>}
                    <div className="text-sm">{children}</div>
                </div>
            </div>
        </div>
    );
}

interface StatCardProps {
    title: string;
    value: string | number;
    icon?: string;
    trend?: {
        value: number;
        isPositive: boolean;
    };
    className?: string;
}

export function StatCard({ title, value, icon, trend, className = '' }: StatCardProps) {
    return (
        <Card className={className}>
            <div className="flex items-start justify-between">
                <div>
                    <p className="text-sm font-medium text-gray-600">{title}</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
                    {trend && (
                        <p className={`text-sm mt-2 ${trend.isPositive ? 'text-green-600' : 'text-red-600'}`}>
                            {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
                        </p>
                    )}
                </div>
                {icon && (
                    <div className="text-4xl opacity-20">{icon}</div>
                )}
            </div>
        </Card>
    );
}

interface ButtonProps {
    children: ReactNode;
    onClick?: () => void;
    variant?: 'primary' | 'secondary' | 'danger' | 'success';
    size?: 'sm' | 'md' | 'lg';
    disabled?: boolean;
    loading?: boolean;
    className?: string;
    type?: 'button' | 'submit';
}

export function Button({
    children,
    onClick,
    variant = 'primary',
    size = 'md',
    disabled = false,
    loading = false,
    className = '',
    type = 'button',
}: ButtonProps) {
    const variants = {
        primary: 'bg-blue-600 hover:bg-blue-700 text-white',
        secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-900',
        danger: 'bg-red-600 hover:bg-red-700 text-white',
        success: 'bg-green-600 hover:bg-green-700 text-white',
    };

    const sizes = {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-4 py-2 text-base',
        lg: 'px-6 py-3 text-lg',
    };

    return (
        <button
            type={type}
            onClick={onClick}
            disabled={disabled || loading}
            className={`font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center justify-center ${variants[variant]} ${sizes[size]} ${className}`}
        >
            {loading && (
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
            )}
            {children}
        </button>
    );
}

export function LoadingSpinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
    const sizes = {
        sm: 'h-4 w-4',
        md: 'h-8 w-8',
        lg: 'h-12 w-12',
    };

    return (
        <div className="flex justify-center items-center p-8">
            <svg className={`animate-spin text-blue-600 ${sizes[size]}`} fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
        </div>
    );
}
