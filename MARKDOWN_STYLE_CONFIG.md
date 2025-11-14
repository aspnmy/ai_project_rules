# Markdown标题红色样式配置说明

本文件提供了在不同IDE中配置Markdown标题显示为红色的方法，以便更快速地识别文档结构。

## 已创建的样式文件

已在项目根目录创建了样式文件：`markdown_red_headings.css`

## VS Code配置方法

1. 安装"Markdown Preview Enhanced"插件（如果尚未安装）
2. 打开设置（File > Preferences > Settings 或 Ctrl+,）
3. 在搜索框中输入"markdown.styles"
4. 点击"Edit in settings.json"
5. 添加以下配置：

```json
{
    "markdown.styles": [
        "${workspaceFolder}/markdown_red_headings.css"
    ]
}
```
6. 保存设置并重启VS Code
7. 打开任何Markdown文件，使用Ctrl+Shift+V预览，标题应显示为红色

## JetBrains IDEs配置方法 (IntelliJ IDEA, PyCharm等)

1. 打开IDE设置（File > Settings 或 Ctrl+Alt+S）
2. 导航到 Editor > Color Scheme > Markdown
3. 选择"Headers"类别
4. 为不同级别的标题（H1-H6）设置颜色为红色（#FF0000）
5. 应用设置并确认

## Visual Studio配置方法

1. 安装"Markdown Editor"扩展
2. 打开扩展选项（Tools > Options > Markdown Editor）
3. 选择"Style"选项卡
4. 导入或粘贴`markdown_red_headings.css`中的样式内容
5. 应用设置

## Sublime Text配置方法

1. 安装"MarkdownPreview"插件
2. 创建或编辑用户配置文件（Preferences > Package Settings > Markdown Preview > Settings）
3. 添加以下配置：

```json
{
    "css_file": "${packages}/User/markdown_red_headings.css"
}
```
4. 将markdown_red_headings.css内容复制到相应位置

## 注意事项

- 不同IDE可能需要不同的配置方法，请根据您使用的具体IDE选择相应的配置方式
- 样式更改仅影响Markdown的显示，不会修改文件内容本身
- 某些预览工具可能需要刷新或重启才能应用新样式

## 自定义样式

如果需要调整红色的深浅程度，可以修改`markdown_red_headings.css`文件中的颜色值：
- `#FF0000`：纯红色
- `#CC0000`：深红色
- `#FF3333`：浅红色
- 或使用任何其他有效的CSS颜色值