import type { Metadata } from 'next';
import '../styles/globals.css';
import { ToastProvider } from '@/components/Toast';

export const metadata: Metadata = {
  title: '法护星 - 专业法律助手',
  description: '智能法律咨询服务平台 - 合同审查、文书生成、法律咨询',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body className="bg-[#f8f9fa]">
        <ToastProvider>
          {children}
        </ToastProvider>
      </body>
    </html>
  );
}