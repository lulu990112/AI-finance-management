# 批量邮件处理功能说明

## 概述

本项目新增了批量处理邮件的功能，可以自动将邮件转换为交易记录。支持的核心处理方式：

**批量同步和处理邮件** - 一次性完成Gmail邮件同步和批量处理

**注意：** 系统只支持批量同步和处理，不提供单独的批量处理功能。

## 重复处理防护机制

为了避免重复处理邮件，系统实现了以下防护机制：

### 1. 同步时只处理新邮件
- 同步邮件时只处理新创建的邮件（`created=True`）
- 避免重复处理已存在的邮件

### 2. 定时任务时间窗口限制
- 定时任务会跳过最近5分钟内创建的邮件
- 防止处理刚同步的邮件

### 3. 邮件状态标记
- 处理完成后标记 `is_processed=True`
- 避免重复处理同一封邮件

## 新增API端点

### 1. 批量同步和处理邮件
```
POST /api/gpt/batch_sync_and_process/
```

**功能说明：**
一次性完成Gmail邮件同步和批量处理，提高效率。

**请求参数：**
- `max_sync_emails` (可选): 最大同步邮件数量，默认50
- `max_process_emails` (可选): 最大处理邮件数量，默认20
- `auto_process` (可选): 是否自动处理，默认true

**示例请求：**
```json
{
    "max_sync_emails": 100,
    "max_process_emails": 30,
    "auto_process": true
}
```

**响应示例：**
```json
{
    "message": "成功同步 50 封邮件",
    "sync_stats": {
        "total_synced": 50,
        "newly_created": 15,
        "already_existed": 35
    },
    "emails": [...],
    "auto_process_enabled": true,
    "process_results": {
        "processed_count": 15,
        "transactions_created": 8,
        "success_emails": [...],
        "failed_emails": [],
        "total_emails": 15,
        "success_rate": "15/15"
    }
}
```

### 2. 获取处理统计
```
GET /api/gpt/processing_stats/
```

**响应示例：**
```json
{
    "total_emails": 150,
    "processed_emails": 120,
    "unprocessed_emails": 30,
    "total_transactions": 85,
    "processing_rate": "120/150",
    "category_stats": {
        "Shopping": {
            "count": 45,
            "total_amount": 1250.50
        },
        "Dining": {
            "count": 25,
            "total_amount": 350.75
        }
    }
}
```

### 3. 同步邮件（自动处理新邮件）
```
GET /api/gmail/sync/
```

**响应示例：**
```json
{
    "message": "Successfully synced 10 emails",
    "emails": [...],
    "user": "username",
    "newly_created_count": 3,
    "auto_process_result": {
        "processed_count": 3,
        "transactions_created": 5
    }
}
```

## 命令行工具

### 1. 批量处理邮件命令
```bash
# 处理所有用户的未处理邮件
python manage.py batch_process_emails

# 处理指定用户的邮件
python manage.py batch_process_emails --user-id 1

# 限制处理邮件数量
python manage.py batch_process_emails --max-emails 100

# 试运行模式（不实际创建交易记录）
python manage.py batch_process_emails --dry-run
```

### 2. 定时处理任务
```bash
# 处理最近7天的新邮件（跳过最近5分钟内的邮件）
python manage.py schedule_email_processing

# 处理最近30天的新邮件
python manage.py schedule_email_processing --days-back 30

# 每个用户最多处理5封邮件
python manage.py schedule_email_processing --max-emails-per-user 5

# 试运行模式
python manage.py schedule_email_processing --dry-run
```

## 自动处理功能

### 1. 同步邮件时自动处理
当调用 `GET /api/gmail/sync/` 同步邮件时，系统会自动处理新同步的邮件。

### 2. 设置定时任务
可以使用cron或其他任务调度器定期执行：

```bash
# 每小时执行一次
0 * * * * cd /path/to/project && python manage.py schedule_email_processing

# 每天凌晨2点执行
0 2 * * * cd /path/to/project && python manage.py schedule_email_processing
```

## 使用场景

### 1. 一次性处理历史邮件
```bash
# 处理所有未处理的邮件
python manage.py batch_process_emails --max-emails 1000
```

### 2. 定期处理新邮件
```bash
# 设置定时任务，每天处理新邮件
python manage.py schedule_email_processing --max-emails-per-user 10
```

### 3. 通过API批量同步和处理邮件
```javascript
// 前端调用示例
fetch('/api/gpt/batch_sync_and_process/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    },
    body: JSON.stringify({
        max_sync_emails: 100,
        max_process_emails: 30,
        auto_process: true
    })
})
.then(response => response.json())
.then(data => {
    console.log('同步和处理完成:', data);
});
```

### 4. 同步邮件并自动处理
```javascript
// 同步邮件并自动处理新邮件
fetch('/api/gmail/sync/')
.then(response => response.json())
.then(data => {
    console.log('同步完成:', data);
});
```

## 重复处理防护说明

### 防护机制工作原理

1. **邮件创建时间检查**
   - 同步时只处理新创建的邮件
   - 定时任务跳过最近5分钟创建的邮件

2. **处理状态标记**
   - 处理完成后标记 `is_processed=True`
   - 避免重复处理同一封邮件

3. **时间窗口控制**
   - 定时任务使用 `created_at__lt=min_processing_time` 过滤
   - 确保不会处理刚同步的邮件

### 推荐使用策略

1. **生产环境**
   - 使用定时任务处理邮件（推荐）
   - 同步时自动处理新邮件

2. **开发环境**
   - 可以启用同步时自动处理进行测试
   - 使用 `--dry-run` 模式测试

3. **高频率同步场景**
   - 依赖定时任务进行批量处理
   - 同步时自动处理新邮件

## 错误处理

系统包含完善的错误处理机制：

1. **GPT API调用失败** - 记录错误但继续处理其他邮件
2. **数据库操作失败** - 记录详细错误信息
3. **邮件格式问题** - 跳过问题邮件继续处理
4. **网络超时** - 自动重试机制

## 性能优化

1. **批量处理** - 避免频繁的数据库操作
2. **错误隔离** - 单个邮件失败不影响其他邮件
3. **进度跟踪** - 实时显示处理进度
4. **资源控制** - 限制每次处理的邮件数量

## 监控和日志

所有处理操作都会记录详细日志：

```python
# 查看处理日志
tail -f logs/django.log | grep "邮件处理"
```

## 注意事项

1. **API限制** - 注意GPT API的调用限制和费用
2. **数据库性能** - 大量处理时注意数据库性能
3. **内存使用** - 处理大量邮件时注意内存使用
4. **错误恢复** - 处理失败后可以重新处理

## 配置建议

1. **生产环境** - 建议使用定时任务而不是API批量处理
2. **测试环境** - 使用 `--dry-run` 模式测试
3. **监控** - 设置监控和告警机制
4. **备份** - 处理前备份重要数据

## 代码重构说明

### 重构目标
消除GPT处理邮件和转换为transaction过程中的冗余代码，提高代码复用性和维护性。

### 重构内容

1. **创建通用工具模块** (`email_processing_utils.py`)
   - `create_transaction_from_gpt_result()`: 从GPT结果创建交易记录
   - `process_emails_batch()`: 批量处理邮件的通用函数
   - `mark_email_as_processed()`: 标记邮件为已处理的通用函数
   - `add_failed_email_to_results()`: 添加失败邮件到结果的通用函数

2. **简化API函数**
   - `batch_process_emails()`: 从60行代码简化为15行
   - `auto_process_new_emails()`: 从60行代码简化为15行

3. **简化管理命令**
   - `batch_process_emails`: 使用通用函数处理，移除force参数
   - `schedule_email_processing`: 统一处理逻辑

4. **移除单个邮件处理功能**
   - 移除了 `test_parse_email` API
   - 移除了 `process_single_email_with_gpt` 函数
   - 简化了代码结构，只保留批量处理功能

### 重构效果

- **代码行数减少**: 从原来的重复代码中减少了约400行
- **维护性提升**: 所有处理逻辑统一在一个地方
- **错误处理统一**: 所有地方使用相同的错误处理机制
- **功能一致性**: 确保所有处理方式行为一致
- **功能简化**: 只保留核心的批量处理功能
- **消除重复**: 完全消除了批量处理逻辑的重复代码
- **进一步优化**: 消除了邮件标记和错误处理的重复代码
- **功能聚焦**: 移除了单个邮件处理功能，专注于批量处理

### 文件结构

```
api/
├── views_gpt.py                    # API视图函数（大幅简化）
├── email_processing_utils.py       # 通用工具函数（4个核心函数）
├── management/commands/
│   ├── batch_process_emails.py     # 批量处理命令（简化）
│   └── schedule_email_processing.py # 定时任务命令（简化）
└── gpt_service.py                  # GPT服务
```

### 使用示例

```python
# 在任何地方都可以使用通用函数
from api.email_processing_utils import process_emails_batch

# 批量处理邮件
results = process_emails_batch(emails, user, dry_run=False)

# 检查结果
print(f"处理了 {results['processed_count']} 封邮件")
print(f"创建了 {results['transactions_created']} 个交易")
```

### 重构前后对比

**重构前:**
- `batch_process_emails`: 60行重复代码
- `auto_process_new_emails`: 60行重复代码
- 管理命令: 各50行重复代码
- 邮件标记逻辑: 重复6行代码
- 错误处理逻辑: 重复8行代码
- 单个邮件处理: 80行代码
- 总计: 约320行重复代码

**重构后:**
- `batch_process_emails`: 15行代码
- `auto_process_new_emails`: 15行代码
- 管理命令: 各20行代码
- 通用函数: 80行代码（可复用）
- 总计: 减少约400行重复代码 