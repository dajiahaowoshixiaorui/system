import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  Form,
  Input,
  Select,
  InputNumber,
  Button,
  Card,
  Row,
  Col,
  message,
  Space,
  Divider,
} from 'antd'
import {
  ArrowLeftOutlined,
  SaveOutlined,
} from '@ant-design/icons'
import { booksApi } from '../../api/books'
import { categoriesApi } from '../../api/categories'
import { Book, Category, BookCreateParams } from '../../types'

const { TextArea } = Input

const BookForm = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [initialValues, setInitialValues] = useState<Partial<BookCreateParams> | undefined>()
  const [categories, setCategories] = useState<Category[]>([])

  const isEdit = !!id

  useEffect(() => {
    loadCategories()
    if (id) {
      loadBookDetail()
    }
  }, [id])

  const loadCategories = async () => {
    try {
      const res = await categoriesApi.getAll()
      setCategories(res || [])
    } catch (e) {
      // 错误已在拦截器处理
    }
  }

  const loadBookDetail = async () => {
    setLoading(true)
    try {
      const book = await booksApi.getDetail(Number(id))
      setInitialValues({
        isbn: book.isbn,
        title: book.title,
        author: book.author,
        publisher: book.publisher,
        publish_date: book.publish_date,
        price: Number(book.price),
        category_id: book.category_id,
        summary: book.summary,
        total_stock: book.total_stock,
        location: book.location,
      })
    } finally {
      setLoading(false)
    }
  }

  const onFinish = async (values: BookCreateParams) => {
    setSubmitting(true)
    try {
      if (isEdit) {
        await booksApi.update(Number(id), values)
        message.success('更新成功')
      } else {
        await booksApi.create(values)
        message.success('创建成功')
      }
      navigate('/books')
    } finally {
      setSubmitting(false)
    }
  }

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
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/books')}
          style={{ marginBottom: 16 }}
        >
          返回列表
        </Button>
        <h2 style={{ margin: 0, color: '#e0e0e0' }}>
          {isEdit ? '编辑图书' : '添加图书'}
        </h2>
      </Card>

      <Card
        style={{
          background: 'rgba(255, 255, 255, 0.03)',
          border: '1px solid rgba(0, 212, 255, 0.1)',
          borderRadius: 12,
        }}
        variant="borderless"
      >
        <Form
          layout="vertical"
          initialValues={initialValues}
          onFinish={onFinish}
          disabled={loading}
        >
          <Divider orientation="left" style={{ color: '#00d4ff' }}>
            基础信息
          </Divider>

          <Row gutter={16}>
            <Col xs={24} md={8}>
              <Form.Item
                name="isbn"
                label="ISBN"
                rules={[
                  { required: true, message: '请输入ISBN' },
                  { min: 10, message: 'ISBN至少10个字符' },
                  { max: 20, message: 'ISBN最多20个字符' },
                ]}
              >
                <Input placeholder="请输入ISBN" />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item
                name="title"
                label="书名"
                rules={[{ required: true, message: '请输入书名' }]}
              >
                <Input placeholder="请输入书名" />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item
                name="author"
                label="作者"
                rules={[{ required: true, message: '请输入作者' }]}
              >
                <Input placeholder="请输入作者" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} md={8}>
              <Form.Item name="publisher" label="出版社">
                <Input placeholder="请输入出版社" />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="publish_date" label="出版日期">
                <Input placeholder="如：2024-01" />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item
                name="price"
                label="价格"
                rules={[{ required: true, message: '请输入价格' }]}
              >
                <InputNumber
                  min={0}
                  precision={2}
                  style={{ width: '100%' }}
                  prefix="¥"
                  placeholder="请输入价格"
                />
              </Form.Item>
            </Col>
          </Row>

          <Divider orientation="left" style={{ color: '#00d4ff' }}>
            分类与库存
          </Divider>

          <Row gutter={16}>
            <Col xs={24} md={8}>
              <Form.Item name="category_id" label="分类">
                <Select
                  placeholder="请选择分类"
                  allowClear
                  options={categories.map(c => ({ label: c.name, value: c.id }))}
                />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item
                name="total_stock"
                label="库存数量"
                rules={[{ required: true, message: '请输入库存数量' }]}
              >
                <InputNumber min={0} style={{ width: '100%' }} placeholder="请输入库存数量" />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="location" label="馆藏位置">
                <Input placeholder="如：A-1-1" />
              </Form.Item>
            </Col>
          </Row>

          <Divider orientation="left" style={{ color: '#4400ffff' }}>
            其他信息
          </Divider>

          <Form.Item name="summary" label="图书简介">
            <TextArea rows={4} placeholder="请输入图书简介" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                icon={<SaveOutlined />}
                loading={submitting}
                style={{
                  background: 'linear-gradient(135deg, #4c00ffff 0%, #6900ccff 100%)',
                  border: 'none',
                }}
              >
                保存
              </Button>
              <Button onClick={() => navigate('/books')}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}

export default BookForm
