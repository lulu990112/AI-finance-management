# Category List 页面实现说明

## 功能概述

实现了将后端transaction数据按category和subcategory分类显示的功能，替换了原有的mock数据。

## 实现方案

### 方案一：前端数据处理（已实现）

**优点：**
- 无需修改后端API
- 前端可以灵活处理数据展示
- 减少API调用次数
- 可以实现实时数据更新

**实现逻辑：**
1. 获取所有交易数据 (`GET /api/gpt/transactions/`)
2. 获取分类结构 (`GET /api/gpt/categories/`)
3. 前端数据处理和汇总
4. 按分类和子分类分组显示

## API函数

### 新增的API函数

#### `getCategoryDetail(categoryName)`
获取特定分类的详细数据，包括：
- 总金额
- 子分类汇总
- 交易记录列表

#### `getCategorySummary()`
获取所有分类的汇总数据，包括：
- 每个分类的总金额
- 颜色信息
- 交易数量

## 数据处理逻辑

### 分类匹配
处理了category和subcategory字段可能是对象或字符串的情况：
```javascript
const txCategory = typeof tx.category === 'object' ? tx.category.name : tx.category;
const subcategoryName = typeof tx.subcategory === 'object' ? tx.subcategory.name : tx.subcategory;
```

### 数据格式化
- 金额格式化：`parseFloat(amount).toFixed(2)`
- 日期格式化：`YYYY-MM-DD`格式
- 颜色映射：提供默认颜色，支持从API获取

### 错误处理
- API调用失败时使用回退数据
- 显示加载状态和错误信息
- 提供重试机制

## 页面组件

### Category List 主页面 (`/category-list`)
- 显示所有分类的汇总卡片
- 每个卡片显示分类名称、总金额和颜色
- 点击卡片跳转到详细页面

### Category Detail 页面 (`/category-list/[category]`)
- 显示特定分类的详细信息
- 子分类进度条和金额
- 交易记录表格
- 按日期排序（最新的在前）

## 数据流程

1. **页面加载** → 调用API获取数据
2. **数据处理** → 按分类筛选和汇总
3. **数据展示** → 渲染UI组件
4. **错误处理** → 回退到默认数据

## 技术特点

- **响应式设计**：适配不同屏幕尺寸
- **加载状态**：提供用户友好的加载提示
- **错误恢复**：API失败时自动使用回退数据
- **数据缓存**：减少重复API调用
- **类型安全**：处理不同数据格式

## 使用说明

1. 确保后端API正常运行
2. 访问 `/category-list` 查看分类汇总
3. 点击任意分类卡片查看详细信息
4. 如果API不可用，会自动使用默认数据

## 注意事项

- 需要用户登录才能访问数据
- 交易数据按用户隔离
- 支持分页加载（如果数据量较大）
- 颜色信息优先使用API返回的数据 