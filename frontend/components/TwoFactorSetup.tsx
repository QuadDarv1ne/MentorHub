"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { QRCodeSVG } from 'qrcode.react'
import { Shield, CheckCircle, AlertCircle, Copy, RefreshCw } from 'lucide-react'

interface TwoFactorSetupProps {
  onSuccess?: () => void
  onCancel?: () => void
}

export default function TwoFactorSetup({ onSuccess, onCancel }: TwoFactorSetupProps) {
  const [step, setStep] = useState<'setup' | 'verify'>('setup')
  const [qrCode, setQrCode] = useState<string>('')
  const [secret, setSecret] = useState<string>('')
  const [backupCodes, setBackupCodes] = useState<string[]>([])
  const [code, setCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)
  const [setupComplete, setSetupComplete] = useState(false)

  const setup2FA = async () => {
    try {
      setLoading(true)
      setError('')
      
      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/v1/auth/2fa/setup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ enabled: true }),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Ошибка настройки 2FA')
      }

      const data = await response.json()
      setQrCode(data.qr_code)
      setSecret(data.secret)
      setBackupCodes(data.backup_codes || [])
      setSetupComplete(true)
      setStep('verify')
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const verify2FA = async () => {
    try {
      setLoading(true)
      setError('')

      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/v1/auth/2fa/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ code }),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Неверный код 2FA')
      }

      onSuccess?.()
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const copySecret = async () => {
    await navigator.clipboard.writeText(secret)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const copyBackupCodes = async () => {
    await navigator.clipboard.writeText(backupCodes.join('\n'))
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="max-w-md mx-auto p-6">
      <div className="text-center mb-6">
        <Shield className="w-12 h-12 mx-auto text-indigo-600 mb-2" />
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          Двухфакторная аутентификация
        </h2>
        <p className="text-gray-600 dark:text-gray-400 text-sm mt-2">
          Защитите свой аккаунт с помощью 2FA
        </p>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start space-x-3">
          <AlertCircle className="text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" size={20} />
          <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
        </div>
      )}

      {step === 'setup' ? (
        <div className="space-y-6">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-4">
              1. Отсканируйте QR код
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Используйте приложение аутентификации (Google Authenticator, Authy, Microsoft Authenticator)
            </p>
            
            {qrCode ? (
              <div className="flex justify-center mb-4">
                <div className="bg-white p-4 rounded-lg">
                  <QRCodeSVG value={qrCode.replace('data:image/png;base64,', '')} size={200} />
                </div>
              </div>
            ) : (
              <button
                onClick={setup2FA}
                disabled={loading}
                className="w-full py-3 px-4 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50"
              >
                {loading ? 'Генерация...' : 'Сгенерировать QR код'}
              </button>
            )}

            {secret && (
              <div className="mt-4">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
                  Или введите секрет вручную:
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={secret}
                    readOnly
                    className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-gray-50 dark:bg-gray-700 text-sm font-mono"
                  />
                  <button
                    onClick={copySecret}
                    className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100"
                    title="Копировать секрет"
                  >
                    {copied ? <CheckCircle size={20} className="text-green-600" /> : <Copy size={20} />}
                  </button>
                </div>
              </div>
            )}
          </div>

          {setupComplete && (
            <>
              <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
                <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  2. Введите код из приложения
                </h3>
                <input
                  type="text"
                  value={code}
                  onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  placeholder="000000"
                  maxLength={6}
                  className="w-full px-4 py-3 text-center text-2xl font-mono border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700"
                />
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-2 text-center">
                  Код обновляется каждые 30 секунд
                </p>
              </div>

              <div className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg border border-yellow-200 dark:border-yellow-800">
                <h3 className="font-semibold text-yellow-800 dark:text-yellow-200 mb-2 flex items-center">
                  <AlertCircle size={18} className="mr-2" />
                  Сохраните backup коды
                </h3>
                <p className="text-sm text-yellow-700 dark:text-yellow-300 mb-2">
                  Эти коды можно использовать если у вас нет доступа к приложению аутентификации:
                </p>
                <div className="bg-white dark:bg-gray-700 p-3 rounded font-mono text-sm grid grid-cols-2 gap-2">
                  {backupCodes.map((code, i) => (
                    <div key={i} className="text-gray-800 dark:text-gray-200">{code}</div>
                  ))}
                </div>
                <button
                  onClick={copyBackupCodes}
                  className="mt-3 text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 flex items-center"
                >
                  <Copy size={14} className="mr-1" />
                  Копировать все коды
                </button>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={onCancel}
                  className="flex-1 py-3 px-4 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  Отмена
                </button>
                <button
                  onClick={verify2FA}
                  disabled={loading || code.length !== 6}
                  className="flex-1 py-3 px-4 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Проверка...' : 'Подтвердить'}
                </button>
              </div>
            </>
          )}

          {!setupComplete && qrCode && (
            <button
              onClick={() => { setSetupComplete(true); setStep('verify'); }}
              className="w-full py-3 px-4 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              Продолжить
            </button>
          )}
        </div>
      ) : null}
    </div>
  )
}
