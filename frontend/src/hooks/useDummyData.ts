import { useEffect, useCallback } from 'react'
import toast from 'react-hot-toast'

/**
 * Hook to handle keyboard shortcut for dummy data.
 * 
 * Usage:
 * ```tsx
 * // In component with form state
 * useDummyData(
 *   'taskCreation',
 *   () => ({ title: '...', description: '...' }),
 *   (data) => {
 *     setTitle(data.title)
 *     setDescription(data.description)
 *   },
 *   isOpen
 * )
 * ```
 */
export function useDummyData<T>(
  _contextKey: string,
  getDummyData: () => T,
  onFill: (data: T) => void,
  isEnabled: boolean = true
) {
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (!isEnabled) return
    
    if ((e.metaKey || e.ctrlKey) && e.key === 'd') {
      e.preventDefault()
      const data = getDummyData()
      onFill(data)
      toast.success('✨ Dummy data loaded! (Cmd/Ctrl+D)', {
        duration: 2000,
        icon: '🎭',
      })
    }
  }, [getDummyData, onFill, isEnabled])

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])
}

/**
 * Pre-configured dummy data templates for common forms.
 */
export const dummyDataTemplates = {
  /**
   * Dummy data for task creation
   */
  taskCreation: () => ({
    title: 'Systematic Review of AI in Healthcare',
    description: 'We are conducting a comprehensive systematic review to understand how artificial intelligence is transforming healthcare delivery in Nigeria. This research will analyze current implementations, effectiveness, challenges, and future opportunities for AI-powered healthcare solutions.',
    research_question: 'How does Artificial Intelligence impact Healthcare in Nigeria, and what are the key implementation barriers?',
    budget: '150000',
    skills: ['data-collection', 'surveys', 'local-knowledge', 'interviews'],
    deadline: '2026-06-30',
    background_context: 'There is a growing need for evidence-based research on AI adoption in African healthcare systems. Previous studies have shown promising results in diagnostic accuracy and patient monitoring, but implementation barriers remain poorly understood.',
    methodology_notes: 'Use mixed-methods approach combining quantitative surveys with qualitative interviews. Ensure IRB approval before data collection. Document all participant consent procedures.',
  }),

  /**
   * Dummy data for work submission
   */
  workSubmission: () => ({
    content_summary: 'I have completed the data collection for Lagos Market Price Survey. I visited all 15 markets as specified and collected price data for 50 commodity items. The dataset includes both retail and wholesale prices with proper documentation of collection timestamps.',
    artifacts: [
      { 
        title: 'Market Price Dataset - Week 1', 
        description: 'Complete price data for 50 commodities across 15 markets',
        type: 'file'
      },
      { 
        title: 'Market Photos Documentation', 
        description: '45 photos (3 per market) showing market layout and vendor operations',
        type: 'dataset'
      }
    ],
  }),

  /**
   * Dummy data for work review
   */
  workReview: () => ({
    review_notes: 'The submitted work is comprehensive and meets all acceptance criteria. The price dataset is well-structured and complete. Photos provide good visual documentation of market visits. Minor suggestion: Add a metadata column for vendor verification timestamps in future submissions.',
    rating: 5,
  }),
}
