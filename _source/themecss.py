# -*- coding: utf-8 -*-
"""Light / dark: the header button can override the phone setting."""


def theme_css(css):
    """Dark-mode rules are written once inside @media (prefers-color-scheme:dark). Emit them twice:
    following the phone unless the visitor picked light, and always when the visitor picked dark."""
    import re
    def block_end(i):
        depth = 0
        for j in range(i, len(css)):
            if css[j] == '{': depth += 1
            elif css[j] == '}':
                depth -= 1
                if depth == 0: return j
    def prefix(rules, pre):
        out = []
        for m in re.finditer(r'([^{}]+)\{([^{}]*)\}', rules):
            sels = []
            for sel in m.group(1).split(','):
                sel = re.sub(r'/\*.*?\*/', '', sel, flags=re.S).strip()
                if not sel: continue
                if sel == ':root': sels.append(pre)
                elif sel.startswith('html'): sels.append(pre + sel[4:])
                else: sels.append(pre + ' ' + sel)
            out.append(','.join(sels) + '{' + m.group(2) + '}')
        return '\n'.join(out)
    key = '@media (prefers-color-scheme:dark){'
    while key in css:
        i = css.index(key)
        j = block_end(i)
        inner = re.sub(r'/\*.*?\*/', '', css[i + len(key):j], flags=re.S)
        new = ('@media (prefers-color-scheme:dark){' + prefix(inner, 'html:not([data-theme="light"])') + '}\n'
               + prefix(inner, 'html[data-theme="dark"]'))
        css = css[:i] + new.replace('prefers-color-scheme:dark', 'prefers-color-scheme: dark') + css[j + 1:]
    return css
