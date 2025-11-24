'use client'

import { useState } from 'react'
import Card from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'
import Button from '@/components/ui/Button'
import Tabs from '@/components/ui/Tabs'
import { ChevronDown, CheckCircle, Code } from 'lucide-react'

const sqlQuestions = [
  {
    id: 1,
    level: 'intermediate',
    title: 'Разница между INNER JOIN и LEFT JOIN',
    question: 'Объясните разницу между INNER JOIN и LEFT JOIN. Когда использовать каждый?',
    answer: 'INNER JOIN возвращает только записи, которые совпадают в обеих таблицах. LEFT JOIN возвращает все записи из левой таблицы и совпадающие из правой. Если совпадения нет, значения из правой таблицы будут NULL.',
    example: `SELECT u.id, u.name, o.order_id
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;`
  },
  {
    id: 2,
    level: 'intermediate',
    title: 'Использование GROUP BY и HAVING',
    question: 'Чему равно количество заказов по каждому пользователю? Покажите только пользователей с более чем 5 заказами.',
    answer: 'Используйте GROUP BY для группировки по пользователю и HAVING для фильтрации групп. HAVING работает с сгруппированными данными, в отличие от WHERE.',
    example: `SELECT user_id, COUNT(*) as order_count
FROM orders
GROUP BY user_id
HAVING COUNT(*) > 5;`
  },
  {
    id: 3,
    level: 'intermediate',
    title: 'Подзапросы vs JOIN',
    question: 'Когда использовать подзапросы вместо JOIN?',
    answer: 'Подзапросы удобны для простых случаев и повышают читаемость. JOIN обычно быстрее и эффективнее для производительности при работе с большими объёмами данных.',
    example: `-- С подзапросом
SELECT name FROM users WHERE id IN (SELECT user_id FROM orders);

-- С JOIN (более эффективно)
SELECT DISTINCT u.name FROM users u JOIN orders o ON u.id = o.user_id;`
  },
  {
    id: 4,
    level: 'advanced',
    title: 'Окно функции (Window Functions)',
    question: 'Что такое окно функции? Напишите запрос для получения ранга продаж по каждому продавцу.',
    answer: 'Окно функции позволяют выполнять вычисления над набором строк, связанных с текущей строкой. ROW_NUMBER() даёт порядковый номер, RANK() - ранг с одинаковыми значениями.',
    example: `SELECT 
  seller_id,
  sale_amount,
  ROW_NUMBER() OVER (PARTITION BY seller_id ORDER BY sale_amount DESC) as rank
FROM sales;`
  },
  {
    id: 5,
    level: 'advanced',
    title: 'CTE (Common Table Expression)',
    question: 'Объясните использование CTE (WITH clause) и покажите пример рекурсивного CTE.',
    answer: 'CTE позволяет определить временную таблицу, которая может быть использована в том же запросе. Рекурсивные CTE полезны для иерархических данных.',
    example: `WITH RECURSIVE hierarchy AS (
  SELECT id, parent_id, name, 1 as level FROM categories WHERE parent_id IS NULL
  UNION ALL
  SELECT c.id, c.parent_id, c.name, h.level + 1 
  FROM categories c
  JOIN hierarchy h ON c.parent_id = h.id
)
SELECT * FROM hierarchy;`
  },
  {
    id: 6,
    level: 'intermediate',
    title: 'DISTINCT vs GROUP BY',
    question: 'В чём разница между DISTINCT и GROUP BY? Какой быстрее?',
    answer: 'DISTINCT просто удаляет дубликаты, GROUP BY может агрегировать данные. GROUP BY может быть медленнее, если нужна сортировка. DISTINCT часто быстрее для простого удаления дубликатов.',
    example: `-- DISTINCT
SELECT DISTINCT city FROM users;

-- GROUP BY
SELECT city FROM users GROUP BY city;`
  },
  {
    id: 7,
    level: 'intermediate',
    title: 'NULL в SQL запросах',
    question: 'Почему "column = NULL" не работает? Как правильно проверить NULL?',
    answer: 'NULL - это отсутствие значения, а не значение. Используйте IS NULL и IS NOT NULL для проверки. "= NULL" всегда вернёт неопределённый результат.',
    example: `-- Неправильно
SELECT * FROM users WHERE age = NULL; -- Вернёт 0 строк!

-- Правильно
SELECT * FROM users WHERE age IS NULL;`
  },
  {
    id: 8,
    level: 'intermediate',
    title: 'UNION vs UNION ALL',
    question: 'В чём разница между UNION и UNION ALL?',
    answer: 'UNION удаляет дубликаты и требует SORT. UNION ALL оставляет все строки и быстрее. Используйте UNION ALL, если дубликаты недопустимы.',
    example: `-- UNION (медленнее, с удалением дубликатов)
SELECT name FROM users1 UNION SELECT name FROM users2;

-- UNION ALL (быстрее)
SELECT name FROM users1 UNION ALL SELECT name FROM users2;`
  },
  {
    id: 9,
    level: 'advanced',
    title: 'Транзакции и ACID свойства',
    question: 'Объясните ACID свойства и как их гарантировать в SQL?',
    answer: 'A - Atomicity (все или ничего), C - Consistency (непротиворечивость), I - Isolation (изоляция), D - Durability (долговечность). Используйте BEGIN, COMMIT, ROLLBACK.',
    example: `BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT; -- Или ROLLBACK если ошибка`
  },
  {
    id: 10,
    level: 'intermediate',
    title: 'Индексы и производительность',
    question: 'Когда создавать индексы? Как они влияют на производительность?',
    answer: 'Индексы ускоряют SELECT и WHERE, но замедляют INSERT, UPDATE, DELETE. Создавайте индексы на часто используемых колонках для фильтрации.',
    example: `-- Создание индекса
CREATE INDEX idx_user_email ON users(email);

-- Выполняется быстро благодаря индексу
SELECT * FROM users WHERE email = 'test@example.com';`
  },
  {
    id: 11,
    level: 'advanced',
    title: 'Денормализация и нормализация',
    question: 'Когда нормализация БД ухудшает производительность? Когда нужна денормализация?',
    answer: 'Денормализация используется когда много JOIN замедляют запросы. Применяйте осторожно - это может привести к несогласованности данных.',
    example: `-- Вместо JOIN можно хранить некоторые данные дважды
-- Таблица orders может содержать user_name, хотя он в таблице users`
  },
  {
    id: 12,
    level: 'intermediate',
    title: 'Функции для дат',
    question: 'Как получить все заказы за последние 30 дней? Покажите функции работы с датами.',
    answer: 'Используйте DATE, DATEDIFF, DATEADD в зависимости от БД. В PostgreSQL используйте INTERVAL, в MySQL - DATE_SUB().',
    example: `-- PostgreSQL
SELECT * FROM orders WHERE created_at > NOW() - INTERVAL '30 days';

-- MySQL
SELECT * FROM orders WHERE created_at > DATE_SUB(NOW(), INTERVAL 30 DAY);`
  },
  {
    id: 13,
    level: 'intermediate',
    title: 'Агрегатные функции',
    question: 'Различие между MAX, MIN, AVG, SUM, COUNT. Как они работают с NULL?',
    answer: 'Все агрегатные функции игнорируют NULL значения, кроме COUNT(*). COUNT(column) не считает NULL.',
    example: `SELECT 
  COUNT(*) as total,           -- Все строки
  COUNT(age) as non_null_age,  -- Только непустые age
  AVG(age) as avg_age,         -- Среднее (без NULL)
  MAX(salary) as max_salary
FROM employees;`
  },
  {
    id: 14,
    level: 'advanced',
    title: 'Оптимизация запросов',
    question: 'Как найти узкие места в SQL запросах? Какие инструменты использовать?',
    answer: 'Используйте EXPLAIN PLAN для анализа плана выполнения. Ищите полные сканирования таблиц, отсутствие индексов, неоптимальные JOIN.',
    example: `-- Посмотреть план выполнения
EXPLAIN SELECT * FROM orders WHERE user_id = 1;

-- В MySQL
EXPLAIN ANALYZE SELECT ...;`
  },
  {
    id: 15,
    level: 'intermediate',
    title: 'CASE выражение в SQL',
    question: 'Как использовать условную логику в SQL запросах?',
    answer: 'CASE WHEN/THEN/ELSE позволяет добавить условную логику. Обычно используется для категоризации или логики бизнеса.',
    example: `SELECT 
  name,
  CASE 
    WHEN age < 18 THEN 'Minor'
    WHEN age >= 18 AND age < 65 THEN 'Adult'
    ELSE 'Senior'
  END as age_group
FROM users;`
  },
  {
    id: 16,
    level: 'advanced',
    title: 'Partitioning и Sharding',
    question: 'Что такое партиционирование и sharding? Как выбрать между ними?',
    answer: 'Партиционирование - разделение большой таблицы на части на одном сервере. Sharding - распределение данных между несколькими серверами.',
    example: `-- Партиционирование по дате
CREATE TABLE orders_2024 PARTITION OF orders
  FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');`
  },
  {
    id: 17,
    level: 'intermediate',
    title: 'Self Join',
    question: 'Что такое Self Join? Покажите пример.',
    answer: 'Self Join - это JOIN таблицы с самой собой. Используется для иерархических отношений или сравнения строк в одной таблице.',
    example: `-- Найти всех сотрудников и их руководителей
SELECT e.name as employee, m.name as manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;`
  },
  {
    id: 18,
    level: 'advanced',
    title: 'Полнотекстовый поиск',
    question: 'Как реализовать полнотекстовый поиск в SQL?',
    answer: 'Используйте FULLTEXT индексы (MySQL) или TSVECTOR (PostgreSQL). Это быстрее, чем LIKE %text%.',
    example: `-- MySQL
SELECT * FROM articles WHERE MATCH(title, content) AGAINST('sql' IN BOOLEAN MODE);

-- PostgreSQL
SELECT * FROM articles WHERE to_tsvector(content) @@ plainto_tsquery('sql');`
  },
  {
    id: 19,
    level: 'intermediate',
    title: 'Каскадное удаление',
    question: 'Как работает ON DELETE CASCADE? Когда его использовать?',
    answer: 'ON DELETE CASCADE автоматически удаляет записи в зависимых таблицах. Используйте осторожно - может привести к потере данных.',
    example: `CREATE TABLE orders (
  id INT PRIMARY KEY,
  user_id INT REFERENCES users(id) ON DELETE CASCADE
);
-- При удалении пользователя все его заказы тоже удалятся`
  },
  {
    id: 20,
    level: 'advanced',
    title: 'NoSQL vs SQL',
    question: 'Когда выбрать SQL, а когда NoSQL? Какие гибридные решения существуют?',
    answer: 'SQL для структурированных данных и сложных запросов. NoSQL для неструктурированных, масштабируемых данных. JSON в SQL - гибридный подход.',
    example: `-- JSON в SQL (PostgeSQL)
SELECT data->\'name\' as name FROM users WHERE data->>\'type\' = \'premium\';`
  }
]

const levels = {
  intermediate: { label: 'Средний уровень', color: 'warning' },
  advanced: { label: 'Продвинутый', color: 'danger' }
}

export default function SQLQuestionsPage() {
  const [expandedId, setExpandedId] = useState<number | null>(null)
  const [filterLevel, setFilterLevel] = useState<'all' | 'intermediate' | 'advanced'>('all')

  const filteredQuestions = filterLevel === 'all' 
    ? sqlQuestions 
    : sqlQuestions.filter(q => q.level === filterLevel)

  return (
    <main className="container mx-auto max-w-4xl px-4 py-10">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">SQL вопросы для собеседования</h1>
        <p className="text-xl text-gray-600">
          20 хитрых вопросов по SQL с ответами и примерами
        </p>
      </div>

      {/* Фильтры */}
      <div className="mb-6 flex gap-2">
        <Button 
          variant={filterLevel === 'all' ? 'primary' : 'outline'}
          onClick={() => setFilterLevel('all')}
          size="sm"
        >
          Все ({sqlQuestions.length})
        </Button>
        <Button 
          variant={filterLevel === 'intermediate' ? 'primary' : 'outline'}
          onClick={() => setFilterLevel('intermediate')}
          size="sm"
        >
          Средний ({sqlQuestions.filter(q => q.level === 'intermediate').length})
        </Button>
        <Button 
          variant={filterLevel === 'advanced' ? 'primary' : 'outline'}
          onClick={() => setFilterLevel('advanced')}
          size="sm"
        >
          Продвинутый ({sqlQuestions.filter(q => q.level === 'advanced').length})
        </Button>
      </div>

      {/* Список вопросов */}
      <div className="space-y-4">
        {filteredQuestions.map((q) => (
          <Card 
            key={q.id} 
            hover 
            padding="md"
            onClick={() => setExpandedId(expandedId === q.id ? null : q.id)}
            className="cursor-pointer"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <span className="font-bold text-indigo-600 text-lg">#{q.id}</span>
                  <h3 className="text-lg font-semibold text-gray-900">{q.title}</h3>
                  <Badge 
                    variant={levels[q.level as keyof typeof levels].color as 'default' | 'success' | 'warning' | 'danger'}
                    size="sm"
                  >
                    {levels[q.level as keyof typeof levels].label}
                  </Badge>
                </div>
                <p className="text-gray-700 mb-3">{q.question}</p>
              </div>
              <ChevronDown 
                className={`h-6 w-6 text-gray-400 transition-transform flex-shrink-0 ${
                  expandedId === q.id ? 'rotate-180' : ''
                }`}
              />
            </div>

            {/* Раскрытый ответ */}
            {expandedId === q.id && (
              <div className="mt-4 pt-4 border-t space-y-3">
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Ответ:</h4>
                  <p className="text-gray-700 leading-relaxed">{q.answer}</p>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                    <Code className="h-4 w-4 mr-2" />
                    Пример:
                  </h4>
                  <pre className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-sm">
                    <code>{q.example}</code>
                  </pre>
                </div>
              </div>
            )}
          </Card>
        ))}
      </div>

      {/* Дополнительные ресурсы */}
      <Card padding="lg" className="mt-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Дополнительные ресурсы</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-start gap-3">
            <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0 mt-1" />
            <div>
              <h4 className="font-semibold text-gray-900">Практика</h4>
              <p className="text-gray-600 text-sm">Используйте сайты типа LeetCode, HackerRank для практики</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0 mt-1" />
            <div>
              <h4 className="font-semibold text-gray-900">Документация</h4>
              <p className="text-gray-600 text-sm">Изучите документацию вашей СУБД (PostgreSQL, MySQL)</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0 mt-1" />
            <div>
              <h4 className="font-semibold text-gray-900">Оптимизация</h4>
              <p className="text-gray-600 text-sm">Учитесь читать EXPLAIN PLAN и оптимизировать запросы</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0 mt-1" />
            <div>
              <h4 className="font-semibold text-gray-900">Реальные проекты</h4>
              <p className="text-gray-600 text-sm">Работайте с реальными БД и данными в своих проектах</p>
            </div>
          </div>
        </div>
      </Card>
    </main>
  )
}
