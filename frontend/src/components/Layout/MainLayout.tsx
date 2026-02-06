import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  Layout,
  Menu,
  Avatar,
  Dropdown,
  Badge,
  Space,
} from 'antd'
import {
  DashboardOutlined,
  BookOutlined,
  TagsOutlined,
  TeamOutlined,
  SwapOutlined,
  UserOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons'
import { useAuthStore } from '../../stores/authStore'

const { Header, Sider, Content } = Layout

interface MainLayoutProps {
  children: React.ReactNode
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: '仪表盘',
    },
    {
      key: '/books',
      icon: <BookOutlined />,
      label: '图书管理',
    },
    {
      key: '/categories',
      icon: <TagsOutlined />,
      label: '分类管理',
    },
    {
      key: '/users',
      icon: <TeamOutlined />,
      label: '用户管理',
      roles: ['admin', 'librarian'],
    },
    {
      key: '/borrows',
      icon: <SwapOutlined />,
      label: '借阅管理',
      roles: ['admin', 'librarian'],
    },
    {
      key: '/my-borrows',
      icon: <UserOutlined />,
      label: '我的借阅',
    },
  ]

  const filteredItems = menuItems.filter(item => {
    if (!item.roles) return true
    return user && item.roles.includes(user.role)
  })

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人中心',
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      danger: true,
    },
  ]

  const handleMenuClick = (key: string) => {
    navigate(key)
  }

  const handleUserMenuClick = ({ key }: { key: string }) => {
    if (key === 'logout') {
      logout()
      navigate('/login')
    }
  }

  const getRoleLabel = (role: string) => {
    const labels: Record<string, string> = {
      admin: '管理员',
      librarian: '图书管理员',
      user: '普通用户',
    }
    return labels[role] || role
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        width={240}
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
          borderRight: '1px solid rgba(0, 212, 255, 0.1)',
        }}
      >
        <div
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderBottom: '1px solid rgba(0, 212, 255, 0.1)',
          }}
        >
          <h1
            style={{
              color: '#00d4ff',
              fontSize: collapsed ? 16 : 20,
              fontWeight: 700,
              margin: 0,
              whiteSpace: 'nowrap',
              textShadow: '0 0 20px rgba(0, 212, 255, 0.5)',
            }}
          >
            {collapsed ? 'LIB' : '图书管理系统'}
          </h1>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={filteredItems}
          onClick={({ key }) => handleMenuClick(key)}
          style={{ background: 'transparent', borderRight: 'none' }}
        />
      </Sider>
      <Layout style={{ marginLeft: collapsed ? 80 : 240, transition: 'margin-left 0.2s' }}>
        <Header
          style={{
            padding: '0 24px',
            background: 'rgba(26, 26, 46, 0.8)',
            backdropFilter: 'blur(10px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: '1px solid rgba(0, 212, 255, 0.1)',
            position: 'sticky',
            top: 0,
            zIndex: 100,
          }}
        >
          <div
            onClick={() => setCollapsed(!collapsed)}
            style={{
              color: '#00d4ff',
              cursor: 'pointer',
              fontSize: 18,
            }}
          >
            {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          </div>
          <Space size="large">
            <Dropdown
              menu={{ items: userMenuItems, onClick: handleUserMenuClick }}
              placement="bottomRight"
            >
              <Space style={{ cursor: 'pointer' }}>
                <Avatar
                  style={{ backgroundColor: '#00d4ff' }}
                  icon={<UserOutlined />}
                />
                <span style={{ color: '#e0e0e0' }}>
                  {user?.username} ({getRoleLabel(user?.role || 'user')})
                </span>
              </Space>
            </Dropdown>
          </Space>
        </Header>
        <Content
          style={{
            margin: 24,
            padding: 24,
            background: 'rgba(255, 255, 255, 0.02)',
            borderRadius: 12,
            minHeight: 280,
            border: '1px solid rgba(0, 212, 255, 0.1)',
          }}
        >
          {children}
        </Content>
      </Layout>
    </Layout>
  )
}

export default MainLayout
