import { useEffect, useState } from 'react'
import {
  Table,
  Button,
  Input,
  InputNumber,
  Space,
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
import { categoriesApi } from '../../api/categories'
import { Category } from '../../types'

const { Search } = Input

const CategoryList = () => {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<Category[]>([])
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 })
  const [searchKeyword, setSearchKeyword] = useState('')
  const [modalVisible, setModalVisible] = useState(false)
  const [editingItem, setEditingItem] = useState<Category | null>(null)
  const [form] = Form.useForm()

  useEffect(() => {
    loadData()
  }, [pagination.current, searchKeyword])

  const loadData = async () => {
    setLoading(true)
    try {
      const res = await categoriesApi.getList({
        page: pagination.current,
        page_size: pagination.pageSize,
        name: searchKeyword || undefined,
      })
      setData(res.items)
      setPagination(prev => ({ ...prev, total: res.total }))
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (value: string) => {
    setSearchKeyword(value)
    setPagination(prev => ({ ...prev, current: 1 }))
  }

  const handleAdd = () => {
    setEditingItem(null)
    form.resetFields()
    setModalVisible(true)
  }

  const handleEdit = (record: Category) => {
    setEditingItem(record)
    form.setFieldsValue(record)
    setModalVisible(true)
  }

  const handleDelete = async (id: number) => {
    try {
      await categoriesApi.delete(id)
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
        await categoriesApi.update(editingItem.id, values)
        message.success('更新成功')
      } else {
        await categoriesApi.create(values)
        message.success('创建成功')
      }
      setModalVisible(false)
      loadData()
    } catch (e) {
      // 错误已在拦截器处理
    }
  }

  const columns = [
    {
      title: '分类名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => <span style={{ color: '#00d4ff' }}>{text}</span>,
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 80,
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 80,
      render: (active: boolean) => (
        <span style={{ color: active ? '#52c41a' : '#ff4d4f' }}>
          {active ? '启用' : '禁用'}
        </span>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_: any, record: Category) => (
        <Space>
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            style={{ color: '#00d4ff' }}
          />
          <Popconfirm
            title="确定要删除这个分类吗？"
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
              placeholder="搜索分类名称"
              allowClear
              enterButton={<SearchOutlined />}
              size="large"
              style={{ maxWidth: 300 }}
              onSearch={handleSearch}
            />
          </Col>
          <Col>
            <Space>
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
                添加分类
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
        title={editingItem ? '编辑分类' : '添加分类'}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={() => setModalVisible(false)}
        okText="保存"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="分类名称"
            rules={[{ required: true, message: '请输入分类名称' }]}
          >
            <Input placeholder="请输入分类名称" />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={3} placeholder="请输入分类描述" />
          </Form.Item>
          <Form.Item name="sort_order" label="排序">
            <InputNumber min={0} style={{ width: '100%' }} placeholder="数字越小越靠前" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default CategoryList
