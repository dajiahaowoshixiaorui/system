import { useEffect, useState } from 'react'
import {
  Table,
  Button,
  Input,
  InputNumber,
  Select,
  Space,
  Tag,
  message,
  Popconfirm,
  Card,
  Row,
  Col,
  Modal,
  Form,
} from 'antd'
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
} from '@ant-design/icons'
import { usersApi } from '../../api/users'
import { User } from '../../types'

const { Search } = Input

const UserList = () => {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<User[]>([])
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 })
  const [filters, setFilters] = useState({ keyword: '', role: '', status: '' })
  const [modalVisible, setModalVisible] = useState(false)
  const [editingItem, setEditingItem] = useState<User | null>(null)
  const [form] = Form.useForm()

  useEffect(() => {
    loadData()
  }, [pagination.current, filters])

  const loadData = async () => {
    setLoading(true)
    try {
      const res = await usersApi.getList({
        page: pagination.current,
        page_size: pagination.pageSize,
        keyword: filters.keyword || undefined,
        role: filters.role || undefined,
        status: filters.status || undefined,
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

  const handleAdd = () => {
    setEditingItem(null)
    form.resetFields()
    setModalVisible(true)
  }

  const handleEdit = (record: User) => {
    setEditingItem(record)
    form.setFieldsValue(record)
    setModalVisible(true)
  }

  const handleDelete = async (id: number) => {
    try {
      await usersApi.delete(id)
      message.success('删除成功')
      loadData()
    } catch (e) {
      // 错误已在拦截器处理
    }
  }

  const handleModalOk = async () => {
    const values = await form.validateFields()
    try {
      if (editingItem) {
        await usersApi.update(editingItem.id, values)
        message.success('更新成功')
      } else {
        await usersApi.create(values)
        message.success('创建成功')
      }
      setModalVisible(false)
      loadData()
    } catch (e) {
      // 错误已在拦截器处理
    }
  }

  const getRoleColor = (role: string) => {
    const colors: Record<string, string> = {
      admin: 'red',
      librarian: 'blue',
      user: 'green',
    }
    return colors[role] || 'default'
  }

  const getRoleText = (role: string) => {
    const texts: Record<string, string> = {
      admin: '管理员',
      librarian: '图书管理员',
      user: '普通用户',
    }
    return texts[role] || role
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      active: 'success',
      inactive: 'error',
      suspended: 'warning',
    }
    return colors[status] || 'default'
  }

  const getStatusText = (status: string) => {
    const texts: Record<string, string> = {
      active: '正常',
      inactive: '禁用',
      suspended: '挂起',
    }
    return texts[status] || status
  }

  const columns = [
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
      render: (text: string) => <span style={{ color: '#00d4ff' }}>{text}</span>,
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      width: 120,
      render: (role: string) => (
        <Tag color={getRoleColor(role)}>{getRoleText(role)}</Tag>
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
      title: '当前借阅',
      dataIndex: 'current_borrow_count',
      key: 'current_borrow_count',
      width: 100,
      render: (count: number, record: User) => (
        <span>
          {count} / {record.max_borrow_count}
        </span>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_: any, record: User) => (
        <Space>
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            style={{ color: '#00d4ff' }}
          />
          <Popconfirm
            title="确定要删除这个用户吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="text" danger icon={<DeleteOutlined />} />
          </Popconfirm>
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
              placeholder="搜索用户名、邮箱"
              allowClear
              enterButton={<SearchOutlined />}
              size="large"
              style={{ maxWidth: 300 }}
              onSearch={handleSearch}
            />
          </Col>
          <Col>
            <Space wrap>
              <Select
                placeholder="角色"
                allowClear
                style={{ width: 120 }}
                options={[
                  { label: '管理员', value: 'admin' },
                  { label: '图书管理员', value: 'librarian' },
                  { label: '普通用户', value: 'user' },
                ]}
                onChange={(value) => {
                  setFilters({ ...filters, role: value || '' })
                  setPagination(prev => ({ ...prev, current: 1 }))
                }}
              />
              <Select
                placeholder="状态"
                allowClear
                style={{ width: 100 }}
                options={[
                  { label: '正常', value: 'active' },
                  { label: '禁用', value: 'inactive' },
                ]}
                onChange={(value) => {
                  setFilters({ ...filters, status: value || '' })
                  setPagination(prev => ({ ...prev, current: 1 }))
                }}
              />
              <Button icon={<ReloadOutlined />} onClick={loadData}>
                刷新
              </Button>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={handleAdd}
                style={{
                  background: 'linear-gradient(135deg, #00d4ff 0%, #0099cc 100%)',
                  border: 'none',
                }}
              >
                添加用户
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

      <Modal
        title={editingItem ? '编辑用户' : '添加用户'}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={() => setModalVisible(false)}
        okText="保存"
        cancelText="取消"
        width={500}
      >
        <Form form={form} layout="vertical">
          {!editingItem && (
            <>
              <Form.Item
                name="username"
                label="用户名"
                rules={[
                  { required: true, message: '请输入用户名' },
                  { min: 3, message: '用户名至少3个字符' },
                ]}
              >
                <Input placeholder="请输入用户名" />
              </Form.Item>
              <Form.Item
                name="password"
                label="密码"
                rules={[
                  { required: true, message: '请输入密码' },
                  { min: 6, message: '密码至少6个字符' },
                ]}
              >
                <Input.Password placeholder="请输入密码" />
              </Form.Item>
            </>
          )}
          <Form.Item
            name="email"
            label="邮箱"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' },
            ]}
          >
            <Input placeholder="请输入邮箱" />
          </Form.Item>
          <Form.Item name="full_name" label="真实姓名">
            <Input placeholder="请输入真实姓名" />
          </Form.Item>
          <Form.Item name="role" label="角色" initialValue="user">
            <Select
              options={[
                { label: '普通用户', value: 'user' },
                { label: '图书管理员', value: 'librarian' },
                { label: '管理员', value: 'admin' },
              ]}
            />
          </Form.Item>
          <Form.Item name="max_borrow_count" label="最大借阅数量" initialValue={5}>
            <InputNumber min={1} max={20} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default UserList
