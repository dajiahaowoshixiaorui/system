import { Routes, Route, Navigate } from 'react-router-dom'
import { App as AntApp } from 'antd'
import { useAuthStore } from './stores/authStore'
import MainLayout from './components/Layout/MainLayout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import BookList from './pages/books/BookList'
import BookForm from './pages/books/BookForm'
import CategoryList from './pages/categories/CategoryList'
import UserList from './pages/users/UserList'
import BorrowList from './pages/borrows/BorrowList'
import MyBorrows from './pages/borrows/MyBorrows'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { token } = useAuthStore()
  return token ? <>{children}</> : <Navigate to="/login" />
}

function App() {
  return (
    <AntApp>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/*"
          element={
            <PrivateRoute>
              <MainLayout>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/books" element={<BookList />} />
                  <Route path="/books/new" element={<BookForm />} />
                  <Route path="/books/:id" element={<BookForm />} />
                  <Route path="/categories" element={<CategoryList />} />
                  <Route path="/users" element={<UserList />} />
                  <Route path="/borrows" element={<BorrowList />} />
                  <Route path="/my-borrows" element={<MyBorrows />} />
                </Routes>
              </MainLayout>
            </PrivateRoute>
          }
        />
      </Routes>
    </AntApp>
  )
}

export default App
