import Link from 'next/link'
import { LEGAL_ENTITY, LEGAL_DOCS_UPDATED } from '@/lib/legal-info'

export const metadata = {
  title: 'Политика использования файлов cookie — MentorHub',
}

export default function CookiesPage() {
  return (
    <div className="prose max-w-none">
      <h2>Политика использования файлов cookie</h2>
      <p>Последнее обновление: {LEGAL_DOCS_UPDATED}</p>

      <h3>1. Общие сведения</h3>
      <p>
        Настоящая Политика определяет порядок использования файлов cookie на сайте MentorHub.
        Файлы cookie относятся к персональным данным в соответствии с Федеральным законом
        от 27.07.2006 № 152-ФЗ (Позиция Роскомнадзора, Определение Конституционного Суда РФ).
      </p>
      <p>
        Используя сайт, пользователь соглашается с данной политикой.
      </p>

      <h3>2. Что такое cookie</h3>
      <p>
        Cookie — небольшие текстовые файлы, сохраняемые на устройстве пользователя при посещении сайта.
        Они используются для корректной работы сайта, аналитики и персонализации.
      </p>

      <h3>3. Используемые cookie</h3>
      <table>
        <thead>
          <tr>
            <th>Название</th>
            <th>Тип</th>
            <th>Провайдер</th>
            <th>Срок хранения</th>
            <th>Назначение</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>session</code></td>
            <td>Необходимые</td>
            <td>MentorHub</td>
            <td>До конца сессии</td>
            <td>Авторизация, поддержание сессии</td>
          </tr>
          <tr>
            <td><code>csrf_token</code></td>
            <td>Необходимые</td>
            <td>MentorHub</td>
            <td>24 часа</td>
            <td>Защита от CSRF-атак</td>
          </tr>
          <tr>
            <td><code>cookie_consent</code></td>
            <td>Необходимые</td>
            <td>MentorHub</td>
            <td>12 месяцев</td>
            <td>Сохранение настроек cookie</td>
          </tr>
          <tr>
            <td><code>theme</code></td>
            <td>Функциональные</td>
            <td>MentorHub</td>
            <td>12 месяцев</td>
            <td>Настройки темы оформления</td>
          </tr>
          <tr>
            <td><code>locale</code></td>
            <td>Функциональные</td>
            <td>MentorHub</td>
            <td>12 месяцев</td>
            <td>Языковые предпочтения</td>
          </tr>
        </tbody>
      </table>

      <h3>4. Категории cookie</h3>
      <ul>
        <li>
          <strong>Необходимые:</strong> всегда активны, не требуют согласия — обеспечивают
          работоспособность сайта (авторизация, безопасность, сохранение настроек).
        </li>
        <li>
          <strong>Функциональные:</strong> сохраняют предпочтения пользователя (тема, язык).
        </li>
        <li>
          <strong>Аналитические:</strong> помогают улучшать сайт; активируются с согласия пользователя.
        </li>
        <li>
          <strong>Маркетинговые:</strong> используются для рекламы и отслеживания; только с прямого
          согласия пользователя.
        </li>
      </ul>

      <h3>5. Cookie третьих сторон</h3>
      <p>
        На сайте могут использоваться cookie третьих сторон. Данные третьих сторон обрабатываются
        согласно их собственным политикам конфиденциальности:
      </p>
      <ul>
        <li>
          <strong>Google Analytics</strong> (Google LLC): сбор статистики посещений.
          Политика конфиденциальности:{' '}
          <a className="text-indigo-600 hover:underline" href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">
            Google Privacy Policy
          </a>.
        </li>
        <li>
          <strong>Яндекс.Метрика</strong> (ООО «Яндекс»): сбор статистики посещений.
          Политика конфиденциальности:{' '}
          <a className="text-indigo-600 hover:underline" href="https://yandex.ru/legal/confidential/" target="_blank" rel="noopener noreferrer">
            Политика конфиденциальности Яндекса
          </a>.
        </li>
      </ul>

      <h3>6. Правовое основание</h3>
      <ul>
        <li>
          Необходимые cookie: исполнение договора (ст. 6(1)(2) 152-ФЗ).
        </li>
        <li>
          Аналитические и маркетинговые: согласие субъекта (ст. 9 152-ФЗ).
        </li>
      </ul>

      <h3>7. Управление cookie</h3>
      <ul>
        <li>Настройки: страница <Link href="/legal/consent" className="text-indigo-600 hover:underline">«Настройки cookie»</Link> или всплывающий баннер cookie.</li>
        <li>Браузер: пользователь может отключить cookie в настройках браузера.</li>
        <li>Отключение необходимых cookie может привести к неработоспособности отдельных функций сайта.</li>
      </ul>

      <h3>8. Изменение политики</h3>
      <p>
        Политика может быть изменена. Новая версия публикуется на сайте.
        Текущая версия всегда доступна по адресу <Link href="/legal/cookies" className="text-indigo-600 hover:underline">/legal/cookies</Link>.
      </p>

      <h3>9. Контакты</h3>
      <p>
        Email: <a className="text-indigo-600 hover:underline" href={`mailto:${LEGAL_ENTITY.email}`}>{LEGAL_ENTITY.email}</a>
      </p>
    </div>
  )
}
