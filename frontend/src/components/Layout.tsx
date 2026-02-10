import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Cloud, FolderGit2, HomeIcon, PlusCircle } from 'lucide-react'

interface LayoutProps {
  children: ReactNode
}

export function Layout({ children }: LayoutProps) {
  const location = useLocation()

  const navItems = [
    { path: '/', label: 'Dashboard', icon: HomeIcon },
    { path: '/resources', label: 'Resources', icon: FolderGit2 },
    { path: '/create', label: 'Create', icon: PlusCircle },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <Cloud className="h-8 w-8 text-blue-600" />
              <h1 className="text-xl font-bold text-gray-900">
                Azure Resources Tracker
              </h1>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`
                    flex items-center space-x-2 px-3 py-4 border-b-2 text-sm font-medium
                    ${
                      isActive
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }
                  `}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </Link>
              )
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500">
            Azure Resources Tracker - Automated resource provisioning via SharePoint
          </p>
        </div>
      </footer>
    </div>
  )
}
