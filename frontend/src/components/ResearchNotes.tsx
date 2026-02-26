'use client'

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface Props {
  content: string
}

export default function ResearchNotes({ content }: Props) {
  return (
    <div className="bg-[#111] border border-gray-800 rounded-xl p-6">
      <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-5">Research Notes</h3>
      <div className="text-sm text-gray-400 leading-relaxed space-y-4 [&_h1]:text-xl [&_h1]:font-bold [&_h1]:text-gray-200 [&_h1]:mb-3 [&_h1]:mt-6 [&_h2]:text-lg [&_h2]:font-bold [&_h2]:text-gray-200 [&_h2]:mb-2 [&_h2]:mt-5 [&_h3]:text-base [&_h3]:font-bold [&_h3]:text-gray-300 [&_h3]:mb-2 [&_h3]:mt-4 [&_p]:mb-3 [&_ul]:list-disc [&_ul]:pl-5 [&_ul]:space-y-1 [&_ol]:list-decimal [&_ol]:pl-5 [&_ol]:space-y-1 [&_li]:text-gray-400 [&_strong]:text-gray-300 [&_strong]:font-semibold [&_code]:text-green-400 [&_code]:bg-gray-900 [&_code]:px-1.5 [&_code]:py-0.5 [&_code]:rounded [&_code]:text-xs [&_code]:font-mono [&_pre]:bg-gray-900 [&_pre]:border [&_pre]:border-gray-800 [&_pre]:rounded-lg [&_pre]:p-4 [&_pre]:overflow-x-auto [&_pre_code]:bg-transparent [&_pre_code]:p-0 [&_blockquote]:border-l-2 [&_blockquote]:border-gray-700 [&_blockquote]:pl-4 [&_blockquote]:text-gray-500 [&_blockquote]:italic [&_hr]:border-gray-800 [&_hr]:my-4 [&_a]:text-blue-400 [&_table]:w-full [&_table]:text-xs [&_table]:border-collapse [&_th]:text-left [&_th]:text-gray-500 [&_th]:font-bold [&_th]:uppercase [&_th]:tracking-wider [&_th]:py-2 [&_th]:px-3 [&_th]:border-b [&_th]:border-gray-800 [&_td]:py-2 [&_td]:px-3 [&_td]:border-b [&_td]:border-gray-900 [&_tr:hover_td]:bg-white/[0.02]">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
      </div>
    </div>
  )
}
