import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "Open Music",
  description: "Baixe músicas em alta qualidade - WAV 48kHz PCM 24-bit Stereo",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  )
}
