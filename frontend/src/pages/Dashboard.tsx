import { useEffect, useState } from 'react'
import { Row, Col, Card, Statistic, Table, List, Typography, Tag, Space } from 'antd'
import {
  BookOutlined,
  TeamOutlined,
  SwapOutlined,
  WarningOutlined,
} from '@ant-design/icons'
import { borrowsApi } from '../api/borrows'
import { useAuthStore } from '../stores/authStore'

const { Title, Text } = Typography

interface StatisticsData {
  total_borrow_count: number
  total_return_count: number
  total_overdue_count: number
  total_fine_amount: number
  popular_books: { id: number; title: string; borrow_count: number }[]
  active_users: { id: number; username: string; borrow_count: number }[]
}

const Dashboard = () => {
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<StatisticsData | null>(null)
  const { user } = useAuthStore()

  useEffect(() => {
    loadStatistics()
  }, [])

  const loadStatistics = async () => {
    try {
      const data = await borrowsApi.getStatistics()
      setStats(data)
    } finally {
      setLoading(false)
    }
  }

  const statCards = [
    {
      title: '当前借阅',
      value: stats?.total_borrow_count || 0,
      icon: <BookOutlined style={{ fontSize: 32, color: '#00d4ff' }} />,
      color: '#00d4ff',
    },
    {
      title: '累计归还',
      value: stats?.total_return_count || 0,
      icon: <SwapOutlined style={{ fontSize: 32, color: '#52c41a' }} />,
      color: '#52c41a',
    },
    {
      title: '逾期未还',
      value: stats?.total_overdue_count || 0,
      icon: <WarningOutlined style={{ fontSize: 32, color: '#ff4d4f' }} />,
      color: '#ff4d4f',
    },
    {
      title: '累计罚款',
      value: stats?.total_fine_amount || 0,
      suffix: '元',
      icon: <TeamOutlined style={{ fontSize: 32, color: '#faad14' }} />,
      color: '#faad14',
    },
  ]

  const popularColumns = [
    {
      title: '排名',
      key: 'rank',
      width: 60,
      render: (_: any, __: any, index: number) => (
        <Tag color={index < 3 ? '#00d4ff' : 'default'}>{index + 1}</Tag>
      ),
    },
    {
      title: '书名',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
    },
    {
      title: '借阅次数',
      dataIndex: 'borrow_count',
      key: 'borrow_count',
      width: 100,
      render: (count: number) => <span style={{ color: '#00d4ff' }}>{count}</span>,
    },
  ]

  return (
    <div className="fade-in">
      <div style={{ marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0, color: '#e0e0e0' }}>
          欢迎回来，{user?.username}
        </Title>
        <Text style={{ color: 'rgba(255, 255, 255, 0.5)' }}>
          这里是图书管理系统的数据概览
        </Text>
      </div>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        {statCards.map((card, index) => (
          <Col xs={24} sm={12} lg={6} key={index}>
            <Card
              className="card-hover"
              style={{
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid rgba(0, 212, 255, 0.1)',
                borderRadius: 12,
              }}
                variant="borderless"
                style={{
                  background: 'rgba(255, 255, 255, 0.9)',
                  borderRadius: 12,
                }}
              >
                <Statistic
                  title={<span style={{ color: '#666' }}>{card.title}</span>}
                value={card.value}
                suffix={card.suffix}
                valueStyle={{
                  color: card.color,
                  fontSize: 28,
                  fontWeight: 600,
                }}
                prefix={card.icon}
              />
            </Card>
          </Col>
        ))}
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card
            title={
              <Space>
                <BookOutlined style={{ color: '#00d4ff' }} />
                <span style={{ color: '#e0e0e0' }}>热门图书 TOP 10</span>
              </Space>
            }
            style={{
              background: 'rgba(255, 255, 255, 0.03)',
              border: '1px solid rgba(0, 212, 255, 0.1)',
              borderRadius: 12,
            }}
            variant="borderless"
            style={{
              background: 'rgba(255, 255, 255, 0.9)',
              borderRadius: 12,
            }}
          >
            <Table
              dataSource={stats?.popular_books || []}
              columns={popularColumns}
              rowKey="id"
              pagination={false}
              loading={loading}
              size="small"
              locale={{ emptyText: '暂无数据' }}
            />
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card
            title={
              <Space>
                <TeamOutlined style={{ color: '#00d4ff' }} />
                <span style={{ color: '#e0e0e0' }}>活跃用户 TOP 10</span>
              </Space>
            }
            style={{
              background: 'rgba(255, 255, 255, 0.03)',
              border: '1px solid rgba(0, 212, 255, 0.1)',
              borderRadius: 12,
            }}
            variant="borderless"
            style={{
              background: 'rgba(255, 255, 255, 0.9)',
              borderRadius: 12,
            }}
          >
            <List
              loading={loading}
              dataSource={stats?.active_users || []}
              renderItem={(item, index) => (
                <List.Item
                  style={{
                    borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
                    padding: '12px 0',
                  }}
                >
                  <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                    <Space>
                      <Tag
                        color={index < 3 ? '#00d4ff' : 'default'}
                        style={{ marginRight: 0 }}
                      >
                        {index + 1}
                      </Tag>
                      <Text style={{ color: '#e0e0e0' }}>{item.username}</Text>
                    </Space>
                    <Text style={{ color: '#00d4ff' }}>
                      借阅 {item.borrow_count} 本
                    </Text>
                  </Space>
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard
