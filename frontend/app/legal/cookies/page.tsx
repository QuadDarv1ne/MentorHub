export const metadata = {
  title: 'Политика использования файлов cookie — MentorHub',
}

export default function CookiesPage() {
  return (
    <div className="prose max-w-none">
      <h2>Файлы cookie</h2>
      <p>Мы используем cookie для работы сайта, аналитики и персонализации.</p>
      <h3>Типы cookie</h3>
      <ul>
        <li>Необходимые — для авторизации и сессий.</li>
        <li>Аналитические — для улучшения качества сервиса.</li>
        <li>Маркетинговые — только с вашим согласием.</li>
      </ul>
      <p>Вы можете изменить настройки на странице «Настройки cookie».</p>
    </div>
  )
}
