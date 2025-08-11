# 群组AI报告功能

## 功能概述

本功能为群组系统添加了完整的AI报告管理功能，实现了层级导航结构：

1. **群组详情页面** (`/groups/[id]`) - 添加了"查看AI报告"按钮
2. **群组AI报告列表页面** (`/groups/[id]/ai-report-list`) - 显示该群组的所有AI报告
3. **群组AI报告详情页面** (`/groups/[id]/ai-report/[reportId]`) - 显示具体AI报告的详细内容

## 路由结构

```
/groups/[id]                    # 群组详情页面
├── /ai-report-list            # 群组AI报告列表
└── /ai-report/[reportId]      # 具体AI报告详情
```

## 新增文件

### 1. 服务层扩展
- `app/services/groupService.js` - 添加了获取群组AI报告的方法

### 2. 页面组件
- `app/groups/[id]/ai-report-list/page.tsx` - 群组AI报告列表页面
- `app/groups/[id]/ai-report/[reportId]/page.tsx` - 群组AI报告详情页面

### 3. 功能特性

#### 群组详情页面
- 在功能按钮区域添加了"查看AI报告"按钮
- 按钮样式与其他功能按钮保持一致
- 点击后跳转到该群组的AI报告列表

#### 群组AI报告列表页面
- 显示该群组的所有AI报告
- 支持批量选择和操作（删除、导出）
- 表格显示报告的基本信息：
  - 报告ID
  - 群组ID
  - 报告日期
  - 分析周期
  - 交易笔数
  - 总金额
  - 生成状态
- 点击报告行可跳转到详情页面
- 包含返回群组页面的导航

#### 群组AI报告详情页面
- 显示AI报告的完整信息
- 包含以下内容区域：
  - 报告基本信息
  - AI财务分析
  - 财务建议
  - 支出分类统计
  - 交易记录
- 支持返回报告列表的导航

## API接口

### 新增的API方法

```javascript
// 获取群组AI报告列表
getGroupAIReports: async (groupId) => {
  return await apiRequest(`/api/group/${groupId}/ai_reports/`);
}

// 获取群组AI报告详情
getGroupAIReportDetail: async (groupId, reportId) => {
  return await apiRequest(`/api/group/${groupId}/ai_reports/${reportId}/`);
}
```

## 使用流程

1. 用户进入群组详情页面 (`/groups/[id]`)
2. 点击"查看AI报告"按钮
3. 跳转到群组AI报告列表页面 (`/groups/[id]/ai-report-list`)
4. 在列表中选择要查看的报告
5. 点击报告行跳转到详情页面 (`/groups/[id]/ai-report/[reportId]`)
6. 查看完整的AI报告内容

## 设计特点

- **层级导航**：清晰的导航结构，用户可以轻松在不同页面间切换
- **一致性**：UI设计与现有页面保持一致
- **响应式**：支持不同屏幕尺寸
- **错误处理**：完善的错误处理和加载状态
- **用户体验**：直观的操作流程和反馈

## 技术实现

- 使用Next.js App Router
- TypeScript支持
- 响应式设计
- 状态管理使用React Context
- 统一的API服务层
- 错误处理和用户反馈
