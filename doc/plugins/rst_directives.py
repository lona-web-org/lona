from flamingo.plugins.rst import register_directive, NestedDirective
from docutils.parsers.rst import directives
from docutils.nodes import raw


def rst_buttons(context):
    class RstButtons(NestedDirective):
        required_arguments = 0
        has_content = True

        def run(self):
            html = self.parse_content(context)

            return [
                raw(
                    '',
                    f'<div class="rst-footer-buttons" role="navigation">{html}</div>',
                    format='html',
                ),
            ]

    return RstButtons


def rst_button(context):
    class RstButton(NestedDirective):
        required_arguments = 0
        has_content = False

        option_spec = {
            'link_target': directives.unchanged,
            'link_title': directives.unchanged,
            'position': directives.unchanged,
        }

        def run(self):
            target = self.options['link_target']
            position = self.options.get('position', 'left')
            title = self.options['link_title']
            link = "{{{{ link('{}') }}}}".format(target)

            if position == 'left':
                title_left = ''
                title_right = title

            elif position == 'right':
                title_left = title
                title_right = ''

            return [
                raw(
                    '',
                    f"""
                        <a href="{link}" class="btn btn-neutral float-{position}" title="{title}">
                            {title_left} <span class="fa fa-arrow-circle-{position}" aria-hidden="true"></span> {title_right}
                        </a>
                    """,
                    format='html',
                ),
            ]

    return RstButton


class rstDirectives:
    def parser_setup(self, context):
        register_directive('rst-buttons', rst_buttons(context))
        register_directive('rst-button', rst_button(context))
