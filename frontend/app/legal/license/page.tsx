import Link from 'next/link'

export const metadata = {
  title: 'Лицензия — MentorHub',
}

export default function LicensePage() {
  return (
    <div className="prose max-w-none">
      <h2>Лицензия</h2>
      <p>
        Проект распространяется по лицензии MIT. Полный текст доступен в репозитории по пути
        <code> /LICENCE</code> или по ссылке ниже.
      </p>
      <p>
        <Link className="text-indigo-600 hover:underline" href="https://github.com/QuadDarv1ne/MentorHub/blob/main/LICENCE" target="_blank">
          Прочитать лицензию MIT
        </Link>
      </p>
    </div>
  )
}
