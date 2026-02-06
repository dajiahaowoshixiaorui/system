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
  Popconfirm,
} from 'antd'
import {
  ReloadOutlined,
  ReloadOutlined as RenewOutlined,
} from '@ant-design/icons'
import { borrowsApi } from '../../api/borrows'
import { BorrowRecord } from '../../types'

const MyBorrows = () => {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<BorrowRecord[]>([])
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 })
  const [status, setStatus] = useState('')

  useEffect(() => {
    loadData()
  }, [pagination.current, status])

  const loadData = async () => {
    setLoading(true)
    try {
      const res = await borrowsApi.getMyBorrows({
        page: pagination.current,
        page_size: pagination.pageSize,
        status: status || undefined,
      })
      setData(res.items)
      setPagination(prev => ({ ...prev, total: res.total }))
    } finally {
      setLoading(false)
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
      title: '图书',
      dataIndex: 'book_title',
      key: 'book_title',
      ellipsis: true,
      render: (text: string) => <span style={{ color: '#00d4ff' }}>{text}</span>,
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
      width: 120,
      render: (_: any, record: BorrowRecord) => (
        <Space>
          {record.status === 'borrowed' && (
            <>
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
            <Space>
              <Select
                placeholder="状态"
                allowClear
                style={{ width: 120 }}
                options={[
                  { label: '借出中', value: 'borrowed' },
                  { label: '已归还', value: 'returned' },
                  { label: '逾期', value: 'overdue' },
                ]}
                onChange={(value) => {
                  setStatus(value || '')
                  setPagination(prev => ({ ...prev, current: 1 }))
                }}
              />
              <Button icon={<ReloadOutlined />} onClick={loadData}>
                刷新
              </Button>
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
    </div>
  )
}

export default MyBorrows
