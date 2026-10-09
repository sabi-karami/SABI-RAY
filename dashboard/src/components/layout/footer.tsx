import { FC } from 'react'
export const Footer: FC = () => (
  <footer className="flex w-full flex-wrap items-center justify-center gap-x-4 gap-y-2 px-4 py-4 text-xs text-muted-foreground">
    <a className="font-semibold tracking-widest text-primary" href="https://github.com/sabi-karami/SABI-RAY" target="_blank" rel="noopener noreferrer">SABI-RAY · ALPHA</a>
    <a className="hover:underline" href="https://t.me/SAHEBKARAMI" target="_blank" rel="noopener noreferrer">@SAHEBKARAMI</a>
    <a className="hover:underline" href="https://github.com/sabi-karami/SABI-RAY/blob/main/docs/fa/README.md" target="_blank" rel="noopener noreferrer">آموزش کامل فارسی</a>
    <a className="hover:underline" href="/statics/sabi-ray/protocols.html" target="_blank" rel="noopener noreferrer">پروتکل‌ها / Protocols</a>
    <a className="hover:underline" href="https://github.com/sabi-karami/SABI-RAY/blob/main/NOTICE.md" target="_blank" rel="noopener noreferrer">Based on PasarGuard · AGPL-3.0 · Source & notices</a>
  </footer>
)
