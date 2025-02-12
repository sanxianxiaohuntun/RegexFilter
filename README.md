# 正则表达式过滤器

一个用于过滤大模型回复中特定内容的插件，支持XML标签和普通正则表达式过滤。

## 安装

配置完成 [LangBot](https://github.com/RockChinQ/LangBot) 主程序后使用管理员账号向机器人发送命令即可安装：

```
!plugin get https://github.com/sanxianxiaohuntun/RegexFilter
```

## 使用

插件提供以下命令：

- `/正则 <表达式>` - 添加新的正则表达式过滤规则
- `/正则 列表` - 显示当前所有正则表达式
- `/正则 删除 <表达式>` - 删除指定正则表达式
- `/正则 关闭 <表达式>` - 暂时关闭指定正则表达式
- `/正则 启用 <表达式>` - 启用指定正则表达式

### XML标签过滤示例

如果要过滤掉形如 `<think>内容</think>` 的内容，可以使用：
```
/正则 <think></think>
```

这将会移除所有 `<think>` 标签及其内容。

### 普通正则表达式示例

也支持普通的正则表达式过滤，例如：
```
/正则 \[.*?\]
```

这将会移除所有方括号及其内容。

### 管理正则表达式

1. 查看当前规则：
```
/正则 列表
```

2. 暂时关闭某个规则：
```
/正则 关闭 <think>
```

3. 重新启用规则：
```
/正则 启用 <think>
```

4. 删除不需要的规则：
```
/正则 删除 <think>
```

## 注意事项

- 正则表达式的修改会实时生效
- 所有规则会保存在配置文件中，重启后会自动加载
- XML标签过滤支持单个标签（如`<think>`）和复杂标签的处理
