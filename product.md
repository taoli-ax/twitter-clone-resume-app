# 简历管理系统功能规划

## 1. 核心功能模块

### **用户管理**
- 用户注册/登录与认证（JWT 或 Session 认证）。
- 用户信息管理（头像、邮箱、联系方式等）。

### **简历创建与管理**
- 支持多份简历管理。
- 模块化编辑：
  - 个人信息（姓名、职位、简介等）。
  - 教育背景（学校、学位、时间等）。
  - 工作经历（公司、职位、职责、起止时间等）。
  - 技能标签（Python、Selenium 等）。
- 数据实时保存。

### **简历模板与预览**
- 多种简历模板选择。
- 实时预览简历效果。
- 导出 PDF（后端生成或前端打印）。

### **管理员后台（可选）**
- 查看所有用户及其简历。
- 数据统计（简历数、活跃用户数）。

---

## 2. 技术标准选型

### **后端**
- **框架**：Django + Django REST Framework（DRF）。
- **数据库**：PostgreSQL 或 SQLite（开发环境）。
- **工具**：
  - Celery + Redis（用于异步任务，比如 PDF 生成）。
  - Django Admin（快速搭建后台管理功能）。

### **前端**
- **框架**：Vue.js 或 React。
- **工具**：
  - TailwindCSS 或 Ant Design（简化样式开发）。
  - Vue Router 或 React Router（页面导航）。

### **测试**
- **自动化测试**：
  - Pytest + Requests（后端接口测试）。
  - Selenium（前端功能测试）。
- **单元测试**：
  - Django 自带测试工具。

### **CI/CD**
- GitHub Actions（测试和自动部署）。
- Docker（部署环境统一）。

---

## 3. 开发步骤

### **阶段 1：需求分析与环境搭建**
- 列出 MVP（最小可行产品）功能。
- 搭建开发环境：
  - 安装 Django、Vue/React，初始化项目。
  - 配置数据库（SQLite 用于开发，PostgreSQL 用于生产）。

---

### **阶段 2：后端开发**

1. **用户模块**
   - 使用 Django 内置的用户模型，扩展用户字段（如头像、联系方式）。
   - 实现 JWT 登录认证（使用 `djangorestframework-simplejwt`）。
   - API：
     - 注册、登录、修改个人信息。

2. **简历模块**
   - 设计数据库模型：
     ```python
     from django import models
     
     class Resume(models.Model):
         user = models.ForeignKey(User, on_delete=models.CASCADE)
         title = models.CharField(max_length=255)
         personal_info = models.JSONField()
         education = models.JSONField()
         work_experience = models.JSONField()
         skills = models.JSONField()
         created_at = models.DateTimeField(auto_now_add=True)
     ```
   - API：
     - CRUD 操作（创建、读取、更新、删除简历）。

3. **文件导出**
   - 集成 `WeasyPrint` 或 `xhtml2pdf`，将 HTML 模板转为 PDF。
   - 异步任务：使用 Celery 实现导出功能，避免阻塞请求。

---

### **阶段 3：前端开发**

1. **界面设计**
   - 使用 Ant Design 或 TailwindCSS 快速搭建页面。
   - 页面：
     - 登录/注册页。
     - 简历列表页。
     - 简历编辑页（表单式模块化编辑）。
     - 预览页面（PDF 导出按钮）。
2. **API 集成**
   - 前端调用后端 API：
   - 用户登录认证。
   - 简历数据的获取和提交。
   - 使用 Axios（Vue）或 Fetch API（React）处理异步请求。
3. **动态预览**
   - 使用前端模板渲染简历（Vue/React 动态绑定数据）。
   - 导出 PDF 时，将 HTML 转换为 PDF（通过后端 API）。


### **阶段 4：测试与优化**
1. 测试覆盖率
  - 编写单元测试（后端模型和 API 测试）。
  - 编写端到端测试（使用 Selenium 测试用户操作流程）。
2. 性能优化
   - 前端优化（代码分包、懒加载）。
   - 数据库优化（索引、查询优化）。
3. 部署
    - 使用 Docker 容器化部署。
    - 将项目托管到云服务（如 AWS、阿里云或自建服务器）
   
### **时间规划**
- 第 1 周：需求分析、环境搭建，用户模块开发。
- 第 2 周：简历模块开发，API 测试。
- 第 3 周：前端开发，动态预览功能。
- 第 4 周：文件导出、测试、部署。



### 简历管理系统的 MVP 功能规划
1. 用户管理
    - 用户注册与登录
      - 用户可以通过邮箱或用户名注册。
      - 支持登录与身份验证（使用 JWT 或 Session）。
2. 简历创建与管理
    - 单份简历管理
    - 用户可以创建一份简历。
      - 简历的基本模块包括：
      - 个人信息（姓名、联系方式）。
      - 教育背景。
      - 工作经历。 
      - 技能标签。
    - CRUD 操作
      - 支持新增、查看、编辑、删除简历。
3. 简历模板与预览
    - 提供单一简历模板。
    - 支持简历的实时预览。
4. 文件导出
    - 简单实现 HTML 转 PDF 的功能，支持下载。

   
### 技术实现
1. 后端
   - 使用 Django + Django REST Framework 实现基础 API。
   - 数据库选择 SQLite，简化开发流程。
   - 提供用户注册登录接口及简历 CRUD 接口。
2. 前端
   - 使用 Vue.js 或 React。
   - 设计简单的用户界面：
   - 登录/注册页。
   - 简历编辑页面（分模块表单）。
   - 简历预览页面。
3. 部署
   - 使用 Docker 部署后端与数据库。
   - 使用简单的 GitHub Pages 或 Vercel 部署前端。

### 开发优先级
1. 实现后端 API：
    - 用户注册登录。
    - 简历模块 CRUD。

2. 实现前端界面与交互： 
   - 简历编辑与预览。
   - 实现 PDF 导出功能。
   - 简单部署，进行用户测试。
     
     