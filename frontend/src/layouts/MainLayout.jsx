import Sidebar from './Sidebar'
import TopNav from './TopNav'

export default function MainLayout({ children, title, subtitle }) {
  return (
    <div className="flex h-screen bg-slate-950 overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col ml-64 min-w-0 overflow-hidden">
        <TopNav title={title} subtitle={subtitle} />
        <main className="flex-1 overflow-y-auto p-6 animate-fade-in">
          {children}
        </main>
      </div>
    </div>
  )
}
