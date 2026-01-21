import { useState, useEffect, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { skillsService } from '../services/api'
import type { SkillsGroupedResponse, Skill } from '../types'

interface SkillsSelectorProps {
  selectedSlugs: string[]
  onChange: (slugs: string[]) => void
  maxSelections?: number
  placeholder?: string
  className?: string
}

export default function SkillsSelector({
  selectedSlugs,
  onChange,
  maxSelections = 10,
  placeholder = 'Select skills...',
  className = '',
}: SkillsSelectorProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [search, setSearch] = useState('')
  const dropdownRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const { data, isLoading } = useQuery<SkillsGroupedResponse>({
    queryKey: ['skills-grouped'],
    queryFn: () => skillsService.listGrouped(),
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  })

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Filter skills based on search
  const filterSkills = (skills: Skill[]) => {
    if (!search) return skills
    const searchLower = search.toLowerCase()
    return skills.filter(
      s => s.name.toLowerCase().includes(searchLower) ||
           s.description?.toLowerCase().includes(searchLower)
    )
  }

  // Get all skills flat list for looking up by slug
  const allSkills = data
    ? [...data.categories.flatMap(c => c.skills), ...data.uncategorized]
    : []

  // Get selected skill objects
  const selectedSkills = selectedSlugs
    .map(slug => allSkills.find(s => s.slug === slug))
    .filter((s): s is Skill => s !== undefined)

  const toggleSkill = (skill: Skill) => {
    const isSelected = selectedSlugs.includes(skill.slug)
    if (isSelected) {
      onChange(selectedSlugs.filter(s => s !== skill.slug))
    } else if (selectedSlugs.length < maxSelections) {
      onChange([...selectedSlugs, skill.slug])
    }
  }

  const removeSkill = (slug: string) => {
    onChange(selectedSlugs.filter(s => s !== slug))
  }

  const hasFilteredResults = data && (
    data.categories.some(c => filterSkills(c.skills).length > 0) ||
    filterSkills(data.uncategorized).length > 0
  )

  return (
    <div ref={dropdownRef} className={`relative ${className}`}>
      {/* Selected skills tags */}
      <div
        className="min-h-[42px] p-2 border border-gray-300 rounded-lg bg-white cursor-text flex flex-wrap gap-2"
        onClick={() => {
          setIsOpen(true)
          inputRef.current?.focus()
        }}
      >
        {selectedSkills.map(skill => (
          <span
            key={skill.id}
            className="inline-flex items-center gap-1 px-2 py-1 bg-primary-100 text-primary-700 text-sm rounded-md"
          >
            {skill.name}
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation()
                removeSkill(skill.slug)
              }}
              className="hover:text-primary-900"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </span>
        ))}
        <input
          ref={inputRef}
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onFocus={() => setIsOpen(true)}
          placeholder={selectedSkills.length === 0 ? placeholder : ''}
          className="flex-1 min-w-[120px] outline-none text-sm bg-transparent"
        />
      </div>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute z-50 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg max-h-80 overflow-y-auto">
          {isLoading ? (
            <div className="p-4 text-center text-gray-500">
              <div className="animate-spin w-5 h-5 border-2 border-gray-300 border-t-primary-500 rounded-full mx-auto"></div>
            </div>
          ) : !hasFilteredResults ? (
            <div className="p-4 text-center text-gray-500 text-sm">
              {search ? 'No skills found' : 'No skills available'}
            </div>
          ) : (
            <div className="py-2">
              {/* Categories */}
              {data?.categories.map(category => {
                const filteredSkills = filterSkills(category.skills)
                if (filteredSkills.length === 0) return null

                return (
                  <div key={category.id} className="mb-2">
                    <div
                      className="px-3 py-1.5 text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-2"
                      style={{ backgroundColor: category.color ? `${category.color}10` : undefined }}
                    >
                      {category.icon && <span>{category.icon}</span>}
                      {category.name}
                    </div>
                    {filteredSkills.map(skill => {
                      const isSelected = selectedSlugs.includes(skill.slug)
                      const isDisabled = !isSelected && selectedSlugs.length >= maxSelections

                      return (
                        <button
                          key={skill.id}
                          type="button"
                          disabled={isDisabled}
                          onClick={() => toggleSkill(skill)}
                          className={`w-full px-3 py-2 text-left text-sm flex items-center justify-between hover:bg-gray-50 transition-colors ${
                            isSelected ? 'bg-primary-50' : ''
                          } ${isDisabled ? 'opacity-50 cursor-not-allowed' : ''}`}
                        >
                          <div>
                            <div className={isSelected ? 'text-primary-700 font-medium' : 'text-gray-700'}>
                              {skill.name}
                            </div>
                            {skill.description && (
                              <div className="text-xs text-gray-500 truncate max-w-[250px]">
                                {skill.description}
                              </div>
                            )}
                          </div>
                          {isSelected && (
                            <svg className="w-4 h-4 text-primary-500" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                          )}
                        </button>
                      )
                    })}
                  </div>
                )
              })}

              {/* Uncategorized */}
              {data && filterSkills(data.uncategorized).length > 0 && (
                <div className="mb-2">
                  <div className="px-3 py-1.5 text-xs font-semibold text-gray-500 uppercase tracking-wider bg-gray-50">
                    Other Skills
                  </div>
                  {filterSkills(data.uncategorized).map(skill => {
                    const isSelected = selectedSlugs.includes(skill.slug)
                    const isDisabled = !isSelected && selectedSlugs.length >= maxSelections

                    return (
                      <button
                        key={skill.id}
                        type="button"
                        disabled={isDisabled}
                        onClick={() => toggleSkill(skill)}
                        className={`w-full px-3 py-2 text-left text-sm flex items-center justify-between hover:bg-gray-50 transition-colors ${
                          isSelected ? 'bg-primary-50' : ''
                        } ${isDisabled ? 'opacity-50 cursor-not-allowed' : ''}`}
                      >
                        <div className={isSelected ? 'text-primary-700 font-medium' : 'text-gray-700'}>
                          {skill.name}
                        </div>
                        {isSelected && (
                          <svg className="w-4 h-4 text-primary-500" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        )}
                      </button>
                    )
                  })}
                </div>
              )}
            </div>
          )}

          {/* Selection count */}
          {selectedSlugs.length > 0 && (
            <div className="px-3 py-2 border-t border-gray-100 text-xs text-gray-500 flex justify-between items-center">
              <span>{selectedSlugs.length} of {maxSelections} selected</span>
              <button
                type="button"
                onClick={() => onChange([])}
                className="text-primary-600 hover:text-primary-700"
              >
                Clear all
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
