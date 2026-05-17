import Link from 'next/link'

export const metadata = {
  title: 'Лицензия — MentorHub',
}

export default function LicensePage() {
  return (
    <div className="prose max-w-none">
      <h2>Лицензия</h2>
      <p>
        Проект MentorHub распространяется на условиях специальной лицензии,
        основанной на MIT, с дополнительными условиями:
      </p>
      <ul>
        <li>Обязательная атрибуция автора.</li>
        <li>Требование уведомления автора перед использованием.</li>
        <li>Запрет коммерческого использования без письменного согласия.</li>
        <li>ShareALike (copyleft) — производные работы на тех же условиях.</li>
      </ul>
      <p>
        Полный текст лицензии на русском языке: <code>/LICENSE_RU</code>
      </p>
      <p>
        Полный текст лицензии на английском языке: <code>/LICENSE</code>
      </p>
      <p>
        <Link className="text-indigo-600 hover:underline" href="https://github.com/QuadDarv1ne/MentorHub/blob/main/LICENSE" target="_blank">
          Прочитать лицензию (GitHub)
        </Link>
      </p>
    </div>
  )
}
