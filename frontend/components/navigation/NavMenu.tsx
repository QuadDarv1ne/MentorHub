'use client'

import Link from 'next/link'
import { useState, useRef, useEffect, useCallback } from 'react'
import { ChevronDown, Grid, BookOpen, Users, Clock, MessageSquare, Search, Layers, Settings, Trophy, BarChart2, CreditCard, HelpCircle, Info, FileText } from 'lucide-react'

interface NavItem {
  title: string
  href: string
  icon?: JSX.Element
  description?: string
}

interface NavCategory {
  title: string
  icon?: JSX.Element
  items: NavItem[]
}

// Конфигурация многоуровневой навигации
const NAV_CATEGORIES: NavCategory[] = [
  {
    title: 'Основное',
    icon: <Grid className="w-5 h-5 text-indigo-600" />,
    items: [
      { title: 'Поиск', href: '/search', icon: <Search className="w-4 h-4" />, description: 'Найдите ментора или курс' },
      { title: 'Менторы', href: '/mentors', icon: <Users className="w-4 h-4" />, description: 'Каталог проверенных менторов' },
      { title: 'Курсы', href: '/courses', icon: <BookOpen className="w-4 h-4" />, description: 'Обучающие программы и треки' },
      { title: 'Сессии', href: '/sessions', icon: <Clock className="w-4 h-4" />, description: 'Запланированные встречи' },
      { title: 'Сообщения', href: '/messages', icon: <MessageSquare className="w-4 h-4" />, description: 'Ваши диалоги и общение' },
    ],
  },
  {
    title: 'Обучение',
    icon: <Layers className="w-5 h-5 text-blue-600" />,
    items: [
      { title: 'Мое обучение', href: '/learning', icon: <Layers className="w-4 h-4" />, description: 'Прогресс по трекам' },
      { title: 'Достижения', href: '/achievements', icon: <Trophy className="w-4 h-4" />, description: 'Полученные награды' },
      { title: 'Статистика', href: '/stats', icon: <BarChart2 className="w-4 h-4" />, description: 'Аналитика прогресса' },
      { title: 'Роадмапы', href: '/roadmap', icon: <FileText className="w-4 h-4" />, description: 'Пути развития навыков' },
    ],
  },
  {
    title: 'Оплата',
    icon: <CreditCard className="w-5 h-5 text-green-600" />,
    items: [
      { title: 'Оплата', href: '/payment', icon: <CreditCard className="w-4 h-4" />, description: 'Разовые платежи' },
      { title: 'Подписка', href: '/pricing', icon: <CreditCard className="w-4 h-4" />, description: 'Тарифные планы' },
      { title: 'Биллинг', href: '/billing', icon: <CreditCard className="w-4 h-4" />, description: 'История транзакций' },
    ],
  },
  {
    title: 'Помощь',
    icon: <HelpCircle className="w-5 h-5 text-yellow-600" />,
    items: [
      { title: 'FAQ', href: '/faq', icon: <HelpCircle className="w-4 h-4" />, description: 'Популярные вопросы' },
      { title: 'Поддержка', href: '/support', icon: <HelpCircle className="w-4 h-4" />, description: 'Связь со службой поддержки' },
      { title: 'О нас', href: '/about', icon: <Info className="w-4 h-4" />, description: 'Информация о платформе' },
      { title: 'Контакты', href: '/contact', icon: <Info className="w-4 h-4" />, description: 'Как с нами связаться' },
    ],
  },
  {
    title: 'Администрирование',
    icon: <Settings className="w-5 h-5 text-gray-600" />,
    items: [
      { title: 'Профиль', href: '/profile', icon: <Users className="w-4 h-4" />, description: 'Личные данные' },
      { title: 'Настройки', href: '/settings', icon: <Settings className="w-4 h-4" />, description: 'Персональные настройки' },
      { title: 'Админка', href: '/admin', icon: <Settings className="w-4 h-4" />, description: 'Панель администратора' },
    ],
  },
]

export function NavMenu() {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const menuRef = useRef<HTMLDivElement | null>(null)
  const itemsRef = useRef<HTMLAnchorElement[]>([])
  const [focusIndex, setFocusIndex] = useState(-1)

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    function handleEsc(e: KeyboardEvent) {
      if (e.key === 'Escape') setOpen(false)
    }
    document.addEventListener('mousedown', handleClickOutside)
    document.addEventListener('keyup', handleEsc)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      document.removeEventListener('keyup', handleEsc)
    }
  }, [])

  // Сброс фокуса при закрытии
  useEffect(() => {
    if (!open) {
      setFocusIndex(-1)
      setQuery('')
    } else {
      // Фокус на поле поиска при открытии
      const searchInput = menuRef.current?.querySelector<HTMLInputElement>('input[data-nav-search]')
      searchInput?.focus()
    }
  }, [open])

  const filteredCategories = NAV_CATEGORIES.map(cat => ({
    ...cat,
    items: cat.items.filter(i => {
      if (!query.trim()) return true
      const q = query.toLowerCase()
      return i.title.toLowerCase().includes(q) || (i.description?.toLowerCase().includes(q) ?? false)
    })
  })).filter(cat => cat.items.length > 0)

  const flatItems = filteredCategories.flatMap(c => c.items)

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (!open) return
    if (['ArrowDown','ArrowUp','Home','End','Enter','Escape'].includes(e.key)) {
      e.preventDefault()
    }
    if (e.key === 'ArrowDown') {
      setFocusIndex(prev => {
        const next = prev + 1 >= flatItems.length ? 0 : prev + 1
        itemsRef.current[next]?.focus()
        return next
      })
    } else if (e.key === 'ArrowUp') {
      setFocusIndex(prev => {
        const next = prev - 1 < 0 ? flatItems.length - 1 : prev - 1
        itemsRef.current[next]?.focus()
        return next
      })
    } else if (e.key === 'Home') {
      itemsRef.current[0]?.focus()
      setFocusIndex(0)
    } else if (e.key === 'End') {
      itemsRef.current[flatItems.length - 1]?.focus()
      setFocusIndex(flatItems.length - 1)
    } else if (e.key === 'Enter') {
      if (focusIndex >= 0) {
        itemsRef.current[focusIndex]?.click()
      }
    } else if (e.key === 'Escape') {
      setOpen(false)
    }
  }, [open, flatItems.length, focusIndex])

  return (
    <div ref={menuRef} className="relative">
      <button
        onClick={() => setOpen(o => !o)}
        aria-haspopup="true"
        aria-controls="nav-popover"
        className="inline-flex items-center gap-1 px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
      >
        <ChevronDown className={`w-4 h-4 transition-transform ${open ? 'rotate-180' : ''}`} />
        <span>Навигация</span>
      </button>
      {open && (
        <div
          id="nav-popover"
          onKeyDown={handleKeyDown}
          className="absolute left-0 mt-2 w-[760px] max-w-[95vw] bg-white rounded-lg shadow-xl border border-gray-200 p-5 z-50"
          aria-label="Навигационные категории"
        >
          {/* Поиск */}
          <div className="mb-4 flex items-center gap-2">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-gray-400 absolute left-2 top-1/2 -translate-y-1/2" />
              <input
                data-nav-search
                type="text"
                value={query}
                onChange={(e) => { setQuery(e.target.value); setFocusIndex(-1); }}
                placeholder="Быстрый поиск..."
                className="w-full pl-8 pr-3 py-2 text-sm border border-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                aria-label="Поиск по меню"
              />
            </div>
            {query && (
              <button
                onClick={() => { setQuery(''); setFocusIndex(-1); }}
                className="text-xs px-2 py-1 rounded-md bg-gray-100 hover:bg-gray-200 text-gray-600"
                aria-label="Очистить поиск"
              >Очистить</button>
            )}
          </div>
          <div className="grid grid-cols-3 gap-6 max-h-[420px] overflow-y-auto pr-2">
            {filteredCategories.length === 0 && (
              <div className="col-span-3 text-sm text-gray-500">Нет совпадений по запросу "{query}"</div>
            )}
            {filteredCategories.map(category => (
              <div key={category.title} className="space-y-3" aria-labelledby={`cat-${category.title}`}>
                <div className="flex items-center gap-2">
                  {category.icon}
                  <h3 id={`cat-${category.title}`} className="text-sm font-semibold text-gray-900">
                    {category.title}
                  </h3>
                </div>
                <div className="space-y-1" role="list">
                  {category.items.map(item => {
                    const globalIndex = flatItems.findIndex(fi => fi.href === item.href)
                    const titleHighlighted = query && item.title.toLowerCase().includes(query.toLowerCase())
                    const descHighlighted = query && (item.description?.toLowerCase().includes(query.toLowerCase()) ?? false)
                    // Безопасное выделение совпадений без dangerouslySetInnerHTML
                    function highlight(text: string): (string | JSX.Element)[] {
                      if (!query) return [text]
                      const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
                      const parts = text.split(new RegExp(`(${escaped})`, 'gi'))
                      return parts.map((part, i) => part.toLowerCase() === query.toLowerCase() ? <span key={i} className="bg-yellow-200 rounded px-0.5">{part}</span> : part)
                    }
                    return (
                      <div key={item.href} role="listitem">
                        <Link
                          href={item.href}
                          ref={(el) => { if (el) itemsRef.current[globalIndex] = el }}
                          tabIndex={0}
                          className={`group flex items-start gap-2 rounded-md px-2 py-1.5 focus:outline-none ${focusIndex === globalIndex ? 'bg-indigo-50 ring-2 ring-indigo-200' : 'hover:bg-indigo-50 focus:bg-indigo-100'}`}
                          onClick={() => setOpen(false)}
                          onFocus={() => setFocusIndex(globalIndex)}
                        >
                          <span className="mt-0.5 text-gray-500 group-hover:text-indigo-600">{item.icon}</span>
                          <span className="flex flex-col">
                            <span className={`text-xs font-medium ${focusIndex === globalIndex ? 'text-indigo-700' : 'text-gray-800'} group-hover:text-indigo-700`}>{highlight(item.title).map((node,i)=>(typeof node === 'string'? <span key={i}>{node}</span>: node))}</span>
                            {item.description && (
                              <span className="text-[11px] text-gray-400 leading-tight">{descHighlighted ? highlight(item.description) : item.description}</span>
                            )}
                          </span>
                        </Link>
                      </div>
                    )
                  })}
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 flex justify-between items-center border-t pt-3">
            <p className="text-[11px] text-gray-400">Всего пунктов: {flatItems.length}</p>
            <p className="text-[11px] text-gray-400">Навигация: ↑ ↓ Enter Esc</p>
          </div>
        </div>
      )}
    </div>
  )
}

export function MobileNavMenu() {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')

  const filtered = NAV_CATEGORIES.map(cat => ({
    ...cat,
    items: cat.items.filter(i => {
      if (!query.trim()) return true
      const q = query.toLowerCase()
      return i.title.toLowerCase().includes(q) || (i.description?.toLowerCase().includes(q) ?? false)
    })
  })).filter(cat => cat.items.length > 0)

  function highlight(text: string): (string | JSX.Element)[] {
    if (!query) return [text]
    const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    const parts = text.split(new RegExp(`(${escaped})`, 'gi'))
    return parts.map((part, i) => part.toLowerCase() === query.toLowerCase() ? <span key={i} className="bg-yellow-200 rounded px-0.5">{part}</span> : part)
  }

  return (
    <div className="md:hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className="flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium text-gray-700 bg-gray-100"
        aria-haspopup="true"
        aria-controls="mobile-nav"
      >
        <ChevronDown className={`w-4 h-4 transition-transform ${open ? 'rotate-180' : ''}`} />
        Меню
      </button>
      {open && (
        <div id="mobile-nav" className="mt-2 border border-gray-200 rounded-lg bg-white shadow-sm p-3 space-y-4" aria-label="Мобильная навигация">
          {/* Поиск */}
          <div className="relative">
            <Search className="w-4 h-4 text-gray-400 absolute left-2 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Поиск..."
              className="w-full pl-8 pr-3 py-2 text-xs border border-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              aria-label="Поиск по мобильному меню"
            />
            {query && (
              <button
                onClick={() => setQuery('')}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-[10px] px-1.5 py-0.5 rounded bg-gray-100 hover:bg-gray-200 text-gray-600"
                aria-label="Очистить поиск"
              >×</button>
            )}
          </div>
          {filtered.length === 0 && (
            <p className="text-xs text-gray-500">Нет совпадений по запросу "{query}"</p>
          )}
          {filtered.map(category => (
            <div key={category.title}>
              <div className="flex items-center gap-2 mb-2">
                {category.icon}
                <h4 className="text-sm font-semibold text-gray-800">{category.title}</h4>
              </div>
              <div className="space-y-1" role="list">
                {category.items.map(item => (
                  <div key={item.href} role="listitem">
                    <Link
                      href={item.href}
                      className="flex items-start gap-2 rounded-md px-2 py-1.5 text-xs hover:bg-indigo-50"
                      onClick={() => { setOpen(false); setQuery(''); }}
                    >
                      {item.icon}
                      <span className="flex flex-col">
                        <span>{highlight(item.title).map((node,i)=>(typeof node === 'string'? <span key={i}>{node}</span>: node))}</span>
                        {item.description && (
                          <span className="text-[10px] text-gray-400 leading-tight">{highlight(item.description)}</span>
                        )}
                      </span>
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          ))}
          <div className="pt-2 border-t flex justify-between items-center">
            <span className="text-[10px] text-gray-400">Всего: {filtered.reduce((a,c)=>a+c.items.length,0)}</span>
            {query && <span className="text-[10px] text-gray-400">Фильтр активен</span>}
          </div>
        </div>
      )}
    </div>
  )
}
