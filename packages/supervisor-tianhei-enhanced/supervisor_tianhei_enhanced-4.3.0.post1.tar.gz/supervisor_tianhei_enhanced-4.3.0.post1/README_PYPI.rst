Supervisor TianHei Enhanced
============================

这是基于原始 Supervisor 项目的增强版本，由 TianHei 维护和开发。

**重要声明**: 这是对原始 Supervisor 项目的增强版本，不是官方版本。原始 Supervisor 项目可以在 http://supervisord.org/ 找到。

功能增强
--------

本版本在原始 Supervisor 基础上新增了以下功能：

**Web 界面增强**
    - 新增进程组批量操作按钮
    - 一键重启/停止整个进程组
    - 改进的用户界面体验

**日志查看增强**
    - 语法高亮显示
    - 行号显示
    - 自动滚动功能
    - 内置搜索功能
    - 一键复制功能

**中文支持**
    - 完整的中文文档
    - 中文安装指南
    - 中文使用说明

安装
----

.. code-block:: bash

    pip install supervisor-tianhei-enhanced

基本使用
--------

安装完成后，您可以像使用原始 Supervisor 一样使用所有命令：

.. code-block:: bash

    # 生成配置文件
    echo_supervisord_conf > supervisord.conf
    
    # 启动 supervisord
    supervisord -c supervisord.conf
    
    # 使用控制台
    supervisorctl -c supervisord.conf status

与原始版本的兼容性
------------------

本增强版本与原始 Supervisor 完全兼容：

- 所有原始命令和配置选项都支持
- 现有的配置文件无需修改即可使用
- API 和插件接口保持不变

许可证
------

本项目遵循与原始 Supervisor 相同的 BSD 风格许可证。

- 原始 Supervisor: Copyright (c) 2006-2015 Agendaless Consulting and Contributors
- 增强功能: Copyright (c) 2024 TianHei

感谢
----

特别感谢原始 Supervisor 项目的所有贡献者，特别是 Chris McDonough 和 Agendaless Consulting 团队。

相关链接
--------

- 原始 Supervisor 官网: http://supervisord.org/
- 原始 Supervisor 文档: http://supervisord.org/
- 原始 Supervisor GitHub: https://github.com/Supervisor/supervisor
- 本增强版源码: https://github.com/tianhei/supervisor-enhanced

如果您需要生产环境的稳定版本，建议使用官方的 ``supervisor`` 包。
如果您需要额外的功能和中文支持，可以尝试本增强版本。 