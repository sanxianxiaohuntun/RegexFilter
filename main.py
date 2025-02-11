import re
import yaml
import os
from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *
from pkg.platform.types import message as platform_message

@register(name="自定义正则表达式过滤", description="用户可以自定义正则表达式过滤", version="0.2", author="小馄饨")
class RegexFilterPlugin(BasePlugin):
    def __init__(self, host: APIHost):
        super().__init__(host)
        self.config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
        self.patterns = {}
        self.load_patterns()

    def load_patterns(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                patterns_data = config.get('patterns', {})
                if isinstance(patterns_data, list):
                    self.patterns = {pattern: {'pattern': pattern, 'enabled': True} for pattern in patterns_data}
                else:
                    self.patterns = patterns_data
        else:
            self.save_patterns()

    def save_patterns(self):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump({'patterns': self.patterns}, f, allow_unicode=True)

    def apply_regex_filters(self, text: str) -> str:
        if not text:
            return text

        result = text
        for pattern_info in self.patterns.values():
            if not pattern_info['enabled']:
                continue
                
            pattern = pattern_info['pattern']
            if pattern.startswith('<') and pattern.endswith('>'):
                tag_name = pattern[1:-1]
                if '></' not in tag_name:
                    xml_pattern = f"<{tag_name}>[\\s\\S]*?</{tag_name}>"
                    result = re.sub(xml_pattern, '', result)
                else:
                    tag_parts = tag_name.split('></')
                    if len(tag_parts) == 2:
                        start_tag = tag_parts[0]
                        end_tag = tag_parts[1]
                        xml_pattern = f"<{start_tag}>[\\s\\S]*?</{end_tag}>"
                        result = re.sub(xml_pattern, '', result)
            else:
                try:
                    result = re.sub(pattern, '', result)
                except Exception as e:
                    pass

        lines = [line.strip() for line in result.splitlines()]
        lines = [line for line in lines if line]
        return '\n'.join(lines)

    def format_pattern_list(self) -> str:
        if not self.patterns:
            return "当前没有正则表达式"
        
        result = "当前正则表达式列表：\n"
        for pattern, info in self.patterns.items():
            status = "启用" if info['enabled'] else "关闭"
            result += f"- {pattern} [{status}]\n"
        return result

    def get_help_text(self) -> str:
        return (
            "正则表达式过滤器使用说明：\n"
            "/正则 <表达式> - 添加新的正则表达式\n"
            "/正则 列表 - 显示当前所有正则表达式\n"
            "/正则 删除 <表达式> - 删除指定正则表达式\n"
            "/正则 关闭 <表达式> - 暂时关闭指定正则表达式\n"
            "/正则 启用 <表达式> - 启用指定正则表达式\n"
            "示例：/正则 <think></think> - 将过滤掉<think></think>标签及其内部内容"
        )

    @handler(NormalMessageResponded)
    async def handle_response(self, ctx: EventContext):
        if not ctx.event.response_text:
            return

        filtered_text = self.apply_regex_filters(ctx.event.response_text)
        if filtered_text != ctx.event.response_text:
            ctx.event.response_text = filtered_text

    @handler(PersonNormalMessageReceived)
    async def handle_person_message(self, ctx: EventContext):
        await self.process_message(ctx)

    @handler(GroupNormalMessageReceived)
    async def handle_group_message(self, ctx: EventContext):
        await self.process_message(ctx)

    async def process_message(self, ctx: EventContext):
        msg = ctx.event.text_message
        if not msg.startswith('/正则'):
            return

        parts = msg.split(maxsplit=2)
        if len(parts) == 1:
            ctx.add_return("reply", [self.get_help_text()])
            ctx.prevent_default()
            return

        command = parts[1] if len(parts) > 1 else ""
        pattern = parts[2] if len(parts) > 2 else ""

        if command == "列表":
            ctx.add_return("reply", [self.format_pattern_list()])
        elif command == "删除" and pattern:
            if pattern in self.patterns:
                del self.patterns[pattern]
                self.save_patterns()
                ctx.add_return("reply", [f"已删除正则表达式：{pattern}"])
            else:
                ctx.add_return("reply", ["未找到该正则表达式"])
        elif command == "关闭" and pattern:
            if pattern in self.patterns:
                self.patterns[pattern]['enabled'] = False
                self.save_patterns()
                ctx.add_return("reply", [f"已关闭正则表达式：{pattern}"])
            else:
                ctx.add_return("reply", ["未找到该正则表达式"])
        elif command == "启用" and pattern:
            if pattern in self.patterns:
                self.patterns[pattern]['enabled'] = True
                self.save_patterns()
                ctx.add_return("reply", [f"已启用正则表达式：{pattern}"])
            else:
                ctx.add_return("reply", ["未找到该正则表达式"])
        elif command and not command.startswith(("列表", "删除", "关闭", "启用")):
            pattern = command
            if pattern not in self.patterns:
                self.patterns[pattern] = {'pattern': pattern, 'enabled': True}
                self.save_patterns()
                ctx.add_return("reply", [f"已添加正则表达式：{pattern}"])
            else:
                ctx.add_return("reply", ["该正则表达式已存在"])
        else:
            ctx.add_return("reply", [self.get_help_text()])

        ctx.prevent_default() 