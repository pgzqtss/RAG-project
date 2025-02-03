export const metadata = {
  title: 'Rag-n-Bones',
  description: 'Generate systematic reviews.',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
