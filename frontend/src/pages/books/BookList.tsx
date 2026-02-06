import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Table,
  Button,
  Input,
  Select,
  Space,
  Tag,
  message,
  Popconfirm,
  Card,
  Row,
  Col,
} from 'antd'
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
} from '@ant-design/icons'
import { booksApi } from '../../api/books'
import { categoriesApi } from '../../api/categories'
import { Book, Category } from '../../types'
import { useAuthStore } from '../../stores/authStore'

const { Search } = Input

const BookList = () => {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<Book[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 })
  const [filters, setFilters] = useState({ keyword: '', category_id: undefined, status: '' })

  const navigate = useNavigate()
  const { user } = useAuthStore()

  useEffect(() => {
    loadCategories()
  }, [])

  useEffect(() => {
    loadData()
  }, [pagination.current, filters])

  const loadCategories = async () => {
    try {
      const res = await categoriesApi.getAll()
      setCategories(res || [])
    } catch (e) {
      // 错误已在拦截器处理
    }
  }

  const loadData = async () => {
    setLoading(true)
    try {
      const res = await booksApi.getList({
        page: pagination.current,
        page_size: pagination.pageSize,
        ...filters,
      })
      setData(res.items)
      setPagination(prev => ({ ...prev, total: res.total }))
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (value: string) => {
    setFilters({ ...filters, keyword: value })
    setPagination(prev => ({ ...prev, current: 1 }))
  }

  const handleDelete = async (id: number) => {
    try {
      await booksApi.delete(id)
      message.success('删除成功')
      loadData()
    } catch (e) {
      // 错误已在拦截器处理
    }
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      available: 'success',
      borrowed: 'processing',
      maintenance: 'warning',
    }
    return colors[status] || 'default'
  }

  const getStatusText = (status: string) => {
    const texts: Record<string, string> = {
      available: '可借',
      borrowed: '已借出',
      maintenance: '维护中',
    }
    return texts[status] || status
  }

  const columns = [
    {
      title: 'ISBN',
      dataIndex: 'isbn',
      key: 'isbn',
      width: 150,
      fixed: 'left' as const,
      render: (text: string) => <span style={{ color: '#00d4ff' }}>{text}</span>,
    },
    {
      title: '书名',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      fixed: 'left' as const,
      render: (text: string) => <span style={{ color: '#e0e0e0ff' }}>{text}</span>,
    },
    {
      title: '作者',
      dataIndex: 'author',
      key: 'author',
      width: 120,
    },
    {
      title: '分类',
      dataIndex: 'category_name',
      key: 'category_name',
      width: 100,
      render: (text: string) => text ? <Tag color="cyan">{text}</Tag> : '-',
    },
    {
      title: '库存',
      key: 'stock',
      width: 120,
      render: (_: any, record: Book) => (
        <Space>
          <span style={{ color: '#52c41a' }}>{record.available_stock}</span>
          <span style={{ color: 'rgba(255,255,255,0.3)' }}>/ {record.total_stock}</span>
        </Space>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>{getStatusText(status)}</Tag>
      ),
    },
    {
      title: '借阅次数',
      dataIndex: 'borrow_count',
      key: 'borrow_count',
      width: 100,
      render: (count: number) => <span style={{ color: '#faad14' }}>{count}</span>,
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      fixed: 'right' as const,
      render: (_: any, record: Book) => (
        <Space>
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => navigate(`/books/${record.id}`)}
            style={{ color: '#00d4ff' }}
          />
          {user?.role === 'admin' && (
            <Popconfirm
              title="确定要删除这本书吗？"
              onConfirm={() => handleDelete(record.id)}
              okText="确定"
              cancelText="取消"
            >
              <Button
                type="text"
                danger
                icon={<DeleteOutlined />}
              />
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div className="fade-in">
      <Card
        style={{
          background: 'transparent',
          border: 'none',
          marginBottom: 16,
        }}
        styles={{ body: { padding: 0 } }}
      >
        <Row gutter={16} align="middle">
          <Col flex="auto">
            <Search
              placeholder="搜索书名、作者、ISBN"
              allowClear
              enterButton={<SearchOutlined />}
              size="large"
              style={{ maxWidth: 400 }}
              onSearch={handleSearch}
            />
          </Col>
          <Col>
            <Space wrap>
              <Select
                placeholder="分类"
                allowClear
                style={{ width: 120 }}
                options={categories.map(c => ({ label: c.name, value: c.id }))}
                onChange={(value) => {
                  setFilters({ ...filters, category_id: value })
                  setPagination(prev => ({ ...prev, current: 1 }))
                }}
              />
              <Select
                placeholder="状态"
                allowClear
                style={{ width: 100 }}
                options={[
                  { label: '可借', value: 'available' },
                  { label: '已借出', value: 'borrowed' },
                  { label: '维护中', value: 'maintenance' },
                ]}
                onChange={(value) => {
                  setFilters({ ...filters, status: value })
                  setPagination(prev => ({ ...prev, current: 1 }))
                }}
              />
              <Button
                icon={<ReloadOutlined />}
                onClick={loadData}
              >
                刷新
              </Button>
              {user?.role !== 'user' && (
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={() => navigate('/books/new')}
                  style={{
                    background: 'linear-gradient(135deg, #00d4ff 0%, #0099cc 100%)',
                    border: 'none',
                  }}
                >
                  添加图书
                </Button>
              )}
            </Space>
          </Col>
        </Row>
      </Card>

      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        pagination={{
          current: pagination.current,
          pageSize: pagination.pageSize,
          total: pagination.total,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条`,
        }}
        onChange={(paginationConfig) => {
          setPagination(prev => ({
            ...prev,
            current: paginationConfig.current || 1,
            pageSize: paginationConfig.pageSize || 10,
          }))
        }}
        scroll={{ x: 1100 }}
      />
    </div>
  )
}

export default BookList
