import { useEffect, useState } from 'react'
import {
  Table,
  Button,
  Select,
  Space,
  Tag,
  message,
  Card,
  Row,
  Col,
  Modal,
  Form,
  InputNumber,
  Input,
  Popconfirm,
} from 'antd'
import {
  ReloadOutlined,
  SwapOutlined,
  ReloadOutlined as RenewOutlined,
} from '@ant-design/icons'
import { borrowsApi } from '../../api/borrows'
import { booksApi } from '../../api/books'
import { usersApi } from '../../api/users'
import { BorrowRecord, Book, User } from '../../types'

const BorrowList = () => {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<BorrowRecord[]>([])
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 })
  const [filters, setFilters] = useState({ status: '', user_id: undefined, book_id: undefined })
  const [borrowModalVisible, setBorrowModalVisible] = useState(false)
  const [returnModalVisible, setReturnModalVisible] = useState(false)
  const [renewModalVisible, setRenewModalVisible] = useState(false)
  const [selectedRecord, setSelectedRecord] = useState<BorrowRecord | null>(null)
  const [users, setUsers] = useState<User[]>([])
  const [books, setBooks] = useState<Book[]>([])
  const [form] = Form.useForm()
  const [returnForm] = Form.useForm()

  useEffect(() => {
    loadUsers()
    loadData()
  }, [pagination.current, filters])

  const loadUsers = async () => {
    try {
      const res = await usersApi.getList({ page: 1, page_size: 100 })
      setUsers(res.items)
    } catch (e) {
      // 错误已在拦截器处理
    }
  }

  const loadBooks = async () => {
    try {
      const res = await booksApi.getList({ page: 1, page_size: 100, status: 'available' })
      setBooks(res.items)
    } catch (e) {
      // 错误已在拦截器处理
    }
  }

  const loadData = async () => {
    setLoading(true)
    try {
      const res = await borrowsApi.getList({
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

  const handleBorrow = async () => {
    const values = await form.validateFields()
    try {
      await borrowsApi.borrow(values)
      message.success('借书成功')
      setBorrowModalVisible(false)
      form.resetFields()
      loadData()
    } catch (e) {
      // 错误已在拦截器处理
    }
  }

  const handleReturn = async () => {
    const values = await returnForm.validateFields()
    try {
      await borrowsApi.return({ record_id: selectedRecord!.id, remark: values.remark })
      message.success('还书成功')
      setReturnModalVisible(false)
      returnForm.resetFields()
      loadData()
    } catch (e) {
      // 错误已在拦截器处理
    }
  }

  const handleRenew = async (record: BorrowRecord) => {
    try {
      await borrowsApi.renew(record.id)
      message.success('续借成功')
      loadData()
    } catch (e) {
      // 错误已在拦截器处理
    }
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      borrowed: 'processing',
      returned: 'success',
      overdue: 'error',
      lost: 'warning',
    }
    return colors[status] || 'default'
  }

  const getStatusText = (status: string) => {
    const texts: Record<string, string> = {
      borrowed: '借出中',
      returned: '已归还',
      overdue: '逾期',
      lost: '丢失',
    }
    return texts[status] || status
  }

  const columns = [
    {
      title: '用户',
      dataIndex: 'user_name',
      key: 'user_name',
      width: 120,
      render: (text: string) => <span style={{ color: '#00d4ff' }}>{text}</span>,
    },
    {
      title: '图书',
      dataIndex: 'book_title',
      key: 'book_title',
      ellipsis: true,
    },
    {
      title: 'ISBN',
      dataIndex: 'book_isbn',
      key: 'book_isbn',
      width: 150,
    },
    {
      title: '借出日期',
      dataIndex: 'borrow_date',
      key: 'borrow_date',
      width: 110,
      render: (date: string) => date?.split('T')[0],
    },
    {
      title: '应还日期',
      dataIndex: 'due_date',
      key: 'due_date',
      width: 110,
      render: (date: string) => date?.split('T')[0],
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
      title: '续借次数',
      dataIndex: 'renew_count',
      key: 'renew_count',
      width: 90,
      render: (count: number, record: BorrowRecord) => (
        <span>
          {count} / {record.max_renew_count}
        </span>
      ),
    },
    {
      title: '逾期天数',
      dataIndex: 'overdue_days',
      key: 'overdue_days',
      width: 90,
      render: (days: number) => (
        <span style={{ color: days > 0 ? '#ff4d4f' : '#e0e0e0' }}>
          {days > 0 ? `${days}天` : '-'}
        </span>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_: any, record: BorrowRecord) => (
        <Space>
          {record.status === 'borrowed' && (
            <>
              <Button
                type="text"
                icon={<SwapOutlined />}
                onClick={() => {
                  setSelectedRecord(record)
                  setReturnModalVisible(true)
                }}
                style={{ color: '#52c41a' }}
              >
                还书
              </Button>
              {record.can_renew && (
                <Popconfirm
                  title="确定要续借吗？"
                  onConfirm={() => handleRenew(record)}
                  okText="确定"
                  cancelText="取消"
                >
                  <Button
                    type="text"
                    icon={<RenewOutlined />}
                    style={{ color: '#faad14' }}
                  >
                    续借
                  </Button>
                </Popconfirm>
              )}
            </>
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
            <Space wrap>
              <Select
                placeholder="状态"
                allowClear
                style={{ width: 100 }}
                options={[
                  { label: '借出中', value: 'borrowed' },
                  { label: '已归还', value: 'returned' },
                  { label: '逾期', value: 'overdue' },
                ]}
                onChange={(value) => {
                  setFilters({ ...filters, status: value || '' })
                  setPagination(prev => ({ ...prev, current: 1 }))
                }}
              />
              <Button icon={<ReloadOutlined />} onClick={loadData}>
                刷新
              </Button>
            </Space>
          </Col>
          <Col>
            <Button
              type="primary"
              icon={<SwapOutlined />}
              onClick={() => {
                loadBooks()
                setBorrowModalVisible(true)
              }}
              style={{
                background: 'linear-gradient(135deg, #00d4ff 0%, #0099cc 100%)',
                border: 'none',
              }}
            >
              借书
            </Button>
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
          showTotal: (total) => `共 ${total} 条`,
        }}
        onChange={(paginationConfig) => {
          setPagination(prev => ({
            ...prev,
            current: paginationConfig.current || 1,
            pageSize: paginationConfig.pageSize || 10,
          }))
        }}
      />

      {/* 借书模态框 */}
      <Modal
        title="借书"
        open={borrowModalVisible}
        onOk={handleBorrow}
        onCancel={() => setBorrowModalVisible(false)}
        okText="确认借出"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="user_id"
            label="选择用户"
            rules={[{ required: true, message: '请选择用户' }]}
          >
            <Select
              placeholder="请选择用户"
              showSearch
              optionFilterProp="children"
              options={users.map(u => ({ label: `${u.username} (${u.full_name || u.email})`, value: u.id }))}
            />
          </Form.Item>
          <Form.Item
            name="book_id"
            label="选择图书"
            rules={[{ required: true, message: '请选择图书' }]}
          >
            <Select
              placeholder="请选择图书（仅显示可借图书）"
              showSearch
              optionFilterProp="children"
              options={books.map(b => ({ label: `${b.title} - ${b.author} (可借:${b.available_stock})`, value: b.id }))}
            />
          </Form.Item>
          <Form.Item name="due_days" label="借阅天数" initialValue={30}>
            <InputNumber min={1} max={60} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>

      {/* 还书模态框 */}
      <Modal
        title="还书"
        open={returnModalVisible}
        onOk={handleReturn}
        onCancel={() => setReturnModalVisible(false)}
        okText="确认归还"
        cancelText="取消"
      >
        <Form form={returnForm} layout="vertical">
          <p style={{ marginBottom: 16 }}>
            归还图书：<span style={{ color: '#00d4ff' }}>{selectedRecord?.book_title}</span>
          </p>
          <Form.Item name="remark" label="备注">
            <Select placeholder="请选择备注">
              <Select.Option value="正常归还">正常归还</Select.Option>
              <Select.Option value="书籍有损坏">书籍有损坏</Select.Option>
              <Select.Option value="书籍丢失">书籍丢失</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default BorrowList
