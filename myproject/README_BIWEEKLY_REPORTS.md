# 半个月AI报告功能

## 功能概述

半个月AI报告功能允许系统自动为每个用户生成基于半个月周期的财务分析报告。报告从用户第一个交易开始计算，每半个月生成一份详细的财务健康分析。

## 主要特性

1. **自动周期计算** - 从用户第一个交易开始自动计算半个月周期
2. **智能报告生成** - 基于半个月的交易数据生成个性化财务建议
3. **避免重复生成** - 同一周期只生成一份报告，避免重复
4. **批量处理** - 支持批量生成所有用户的报告
5. **灵活查询** - 提供多种API端点查询报告

## 数据库模型

### AIReport模型扩展

新增字段：
- `report_type` - 报告类型（general, biweekly, monthly）
- `report_period_start` - 报告周期开始日期
- `report_period_end` - 报告周期结束日期
- `period_name` - 周期名称（如"2024-01-01 to 2024-01-15"）

## API端点

### 1. 获取半个月报告列表
```
GET /api/ai_report/biweekly/
```

**参数：**
- `page` - 页码（默认1）
- `page_size` - 每页数量（默认10）

**响应示例：**
```json
{
    "reports": [
        {
            "id": 1,
            "financial_advice_summary": "Based on your spending data...",
            "abnormal_alert": "No significant anomalies detected...",
            "money_saving_tip": "Consider tracking your daily expenses...",
            "report_date": "2024-01-15T10:30:00Z",
            "analysis_period": "Biweekly period: 2024-01-01 to 2024-01-15",
            "total_transactions": 5,
            "total_amount": "425.50",
            "is_generated": true,
            "generation_status": "completed",
            "report_type": "biweekly",
            "report_period_start": "2024-01-01",
            "report_period_end": "2024-01-15",
            "period_name": "2024-01-01 to 2024-01-15"
        }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10,
    "report_type": "biweekly"
}
```

### 2. 获取最新半个月报告
```
GET /api/ai_report/biweekly/latest/
```

**响应示例：**
```json
{
    "message": "Latest biweekly report retrieved successfully",
    "report": {
        "id": 1,
        "financial_advice_summary": "Based on your spending data...",
        "abnormal_alert": "No significant anomalies detected...",
        "money_saving_tip": "Consider tracking your daily expenses...",
        "report_date": "2024-01-15T10:30:00Z",
        "analysis_period": "Biweekly period: 2024-01-01 to 2024-01-15",
        "total_transactions": 5,
        "total_amount": "425.50",
        "is_generated": true,
        "generation_status": "completed",
        "report_type": "biweekly",
        "report_period_start": "2024-01-01",
        "report_period_end": "2024-01-15",
        "period_name": "2024-01-01 to 2024-01-15"
    }
}
```

### 3. 获取指定周期的半个月报告
```
GET /api/ai_report/biweekly/{start_date}/{end_date}/
```

**参数：**
- `start_date` - 开始日期（YYYY-MM-DD格式）
- `end_date` - 结束日期（YYYY-MM-DD格式）

**响应示例：**
```json
{
    "message": "Biweekly report retrieved successfully",
    "report": {
        "id": 1,
        "financial_advice_summary": "Based on your spending data...",
        "abnormal_alert": "No significant anomalies detected...",
        "money_saving_tip": "Consider tracking your daily expenses...",
        "report_date": "2024-01-15T10:30:00Z",
        "analysis_period": "Biweekly period: 2024-01-01 to 2024-01-15",
        "total_transactions": 5,
        "total_amount": "425.50",
        "is_generated": true,
        "generation_status": "completed",
        "report_type": "biweekly",
        "report_period_start": "2024-01-01",
        "report_period_end": "2024-01-15",
        "period_name": "2024-01-01 to 2024-01-15"
    }
}
```

### 4. 手动生成指定周期的半个月报告
```
POST /api/ai_report/biweekly/generate/
```

**请求体：**
```json
{
    "start_date": "2024-01-01",
    "end_date": "2024-01-15"
}
```

**响应示例：**
```json
{
    "message": "Biweekly report generated successfully",
    "report": {
        "id": 1,
        "financial_advice_summary": "Based on your spending data...",
        "abnormal_alert": "No significant anomalies detected...",
        "money_saving_tip": "Consider tracking your daily expenses...",
        "report_date": "2024-01-15T10:30:00Z",
        "analysis_period": "Biweekly period: 2024-01-01 to 2024-01-15",
        "total_transactions": 5,
        "total_amount": "425.50",
        "is_generated": true,
        "generation_status": "completed",
        "report_type": "biweekly",
        "report_period_start": "2024-01-01",
        "report_period_end": "2024-01-15",
        "period_name": "2024-01-01 to 2024-01-15"
    },
    "is_cached": false
}
```

## 管理命令

### 生成半个月报告

```bash
# 为所有用户生成半个月报告
python manage.py generate_biweekly_reports

# 为特定用户生成报告
python manage.py generate_biweekly_reports --user-id 1

# 强制重新生成已存在的报告
python manage.py generate_biweekly_reports --force

# 试运行模式（不实际生成报告）
python manage.py generate_biweekly_reports --dry-run

# 生成过去6个月的报告（默认）
python manage.py generate_biweekly_reports --periods-back 6

# 生成过去12个月的报告
python manage.py generate_biweekly_reports --periods-back 12
```

### 命令参数说明

- `--user-id` - 为特定用户生成报告（用户ID）
- `--force` - 强制重新生成已存在的报告
- `--dry-run` - 试运行模式，不实际生成报告
- `--periods-back` - 生成多少个月前的报告（默认6个月）

## 定时任务设置

### Linux/Mac (cron)

```bash
# 每月1号和16号凌晨2点执行
0 2 1,16 * * cd /path/to/project && python manage.py generate_biweekly_reports

# 或者每天凌晨2点执行（系统会自动跳过已存在的报告）
0 2 * * * cd /path/to/project && python manage.py generate_biweekly_reports
```

### Windows (任务计划程序)

1. 打开任务计划程序
2. 创建基本任务
3. 设置触发器为每月1号和16号
4. 设置操作为运行命令：`python manage.py generate_biweekly_reports`
5. 设置起始目录为项目目录

## 测试

### 运行测试脚本

```bash
python test_biweekly_reports.py
```

测试脚本会：
1. 创建测试用户和交易数据
2. 测试半个月周期计算
3. 测试报告生成功能
4. 测试报告列表查询
5. 可选择清理测试数据

### 手动测试

1. 确保有用户和交易数据
2. 运行测试脚本创建测试数据
3. 验证半个月报告生成功能
4. 检查报告内容质量

## 配置要求

### 1. 数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. OpenAI API Key

确保在环境变量或`.env`文件中设置：
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. 分类设置

```bash
python manage.py setup_categories
```

## 错误处理

### 常见错误及解决方案

1. **没有交易数据**
   - 确保用户有交易记录
   - 先同步和处理邮件

2. **OpenAI API错误**
   - 检查API Key是否正确
   - 检查网络连接
   - 检查API配额

3. **报告生成失败**
   - 检查GPT服务是否正常
   - 查看日志获取详细错误信息

4. **周期计算错误**
   - 检查用户是否有交易数据
   - 检查日期格式是否正确

## 性能优化

### 1. 缓存机制
- 同一周期只生成一份报告
- 避免重复调用GPT API

### 2. 批量处理
- 支持批量生成所有用户的报告
- 使用数据库索引提高查询性能

### 3. 异步处理
- 可以考虑将报告生成改为异步任务
- 使用Celery等任务队列

## 扩展功能

### 1. 报告模板
- 支持多种报告模板
- 根据用户偏好定制报告风格

### 2. 历史趋势分析
- 比较不同时期的消费模式
- 生成趋势图表

### 3. 预算建议
- 基于历史数据推荐预算分配
- 提供预算执行建议

## 安全考虑

1. **数据隐私**
   - 用户数据仅用于生成报告
   - 不存储敏感财务信息

2. **API安全**
   - 所有端点需要用户认证
   - 用户只能访问自己的报告

3. **访问控制**
   - 用户只能查看自己的报告
   - 管理员可以查看所有报告

## 监控和维护

### 1. 日志记录
- 记录报告生成过程
- 记录错误和异常情况
- 提供报告生成统计信息

### 2. 错误处理
- 处理无交易数据的情况
- 处理API调用失败的情况
- 提供重试机制

### 3. 性能监控
- 监控报告生成时间
- 监控API调用频率
- 监控数据库查询性能



