# latex2docx文档转换

这是一个把LaTeX转换成docx的工作框架，框架核心是基于pandoc和pandoc-tex-numbering这个filter完成，但pandoc对LaTeX和docx的支持都不够完善，所以需要使用这个框架来完成转换前后一些额外的处理。

对于普通用户，我会提供简单的bat脚本，对于已知可以支持的功能，你只需要按照我描述的工作流程就可以零代码完成转换。

对于熟悉Python的用户，你可以把这个项目视为一个工作脚手架，只需要按照自己的需求扩展`processor.py`文件的`reader`和`writer`函数，就可以实现自己的转换需求。

本项目的工作流：

```mermaid
flowchart LR
    A([LaTeX]) --> B{Python Reader}
    B --> C[Temp Tex File]
    C --> D("`pandoc
    pandoc-tex-numbering`")
    D --> E[Temp Docx File]
    E --> F{Python Writer}
    F --> G([Docx])
```