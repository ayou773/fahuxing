'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

type MarkdownContentProps = {
  content: string;
  className?: string;
};

function preprocessContent(content: string): string {
  return content
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<br>/gi, '\n');
}

export default function MarkdownContent({ content, className }: MarkdownContentProps) {
  const processedContent = preprocessContent(content);
  return (
    <div className={className}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => <h1 className="mt-4 mb-3 text-xl font-bold text-slate-800">{children}</h1>,
          h2: ({ children }) => <h2 className="mt-4 mb-2 text-lg font-semibold text-slate-800">{children}</h2>,
          h3: ({ children }) => <h3 className="mt-3 mb-2 text-base font-semibold text-slate-800">{children}</h3>,
          p: ({ children }) => <p className="mb-2 leading-7 text-slate-700">{children}</p>,
          ul: ({ children }) => <ul className="mb-3 list-disc space-y-1 pl-5 text-slate-700">{children}</ul>,
          ol: ({ children }) => <ol className="mb-3 list-decimal space-y-1 pl-5 text-slate-700">{children}</ol>,
          li: ({ children }) => <li>{children}</li>,
          table: ({ children }) => (
            <div className="my-4 overflow-x-auto rounded-lg border border-slate-200">
              <table className="min-w-full border-collapse text-sm">{children}</table>
            </div>
          ),
          thead: ({ children }) => <thead className="bg-slate-100 text-slate-700">{children}</thead>,
          tbody: ({ children }) => <tbody className="bg-white">{children}</tbody>,
          tr: ({ children }) => <tr className="odd:bg-white even:bg-slate-50">{children}</tr>,
          th: ({ children }) => (
            <th className="border border-slate-200 px-3 py-2 text-left font-semibold whitespace-nowrap">{children}</th>
          ),
          td: ({ children }) => <td className="border border-slate-200 px-3 py-2 align-top">{children}</td>,
          blockquote: ({ children }) => (
            <blockquote className="my-3 border-l-4 border-slate-300 bg-slate-50 px-4 py-2 text-slate-600">
              {children}
            </blockquote>
          ),
          code: ({ children }) => (
            <code className="rounded bg-slate-100 px-1.5 py-0.5 text-[13px] text-slate-800">{children}</code>
          ),
        }}
      >
        {processedContent}
      </ReactMarkdown>
    </div>
  );
}
