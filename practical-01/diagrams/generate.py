from collections import deque
from html import escape
from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
FONT_DIR = Path('C:/Windows/Fonts')


class Drawing:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.parts = []
        self.image = Image.new('RGB', (width, height), 'white')
        self.pen = ImageDraw.Draw(self.image)

    def text(self, x, y, text, size=22, color='#172536'):
        self.parts.append(f'<text x="{x}" y="{y}" text-anchor="middle" '
                          f'font-family="Arial, sans-serif" font-size="{size}" '
                          f'fill="{color}">{escape(text)}</text>')
        candidates = [FONT_DIR / 'arial.ttf', Path('/System/Library/Fonts/Supplemental/Arial.ttf'),
                      Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')]
        font = next((ImageFont.truetype(str(p), size) for p in candidates if p.exists()),
                    ImageFont.load_default())
        self.pen.text((x, y), text, font=font, fill=color, anchor='ms')

    def line(self, points, color='#536477'):
        coords = ' '.join(f'{x},{y}' for x, y in points)
        self.parts.append(f'<polyline points="{coords}" fill="none" stroke="{color}" '
                          'stroke-width="2.5" marker-end="url(#arrow)"/>')
        self.pen.line(points, fill=color, width=3)
        x, y = points[-1]
        px, py = points[-2]
        if x != px:
            d = 1 if x > px else -1
            triangle = [(x, y), (x - 11 * d, y - 5), (x - 11 * d, y + 5)]
        else:
            d = 1 if y > py else -1
            triangle = [(x, y), (x - 5, y - 11 * d), (x + 5, y - 11 * d)]
        self.pen.polygon(triangle, fill=color)

    def place(self, x, y, name, label, marked=False, label_dx=0, label_dy=0):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="29" fill="#eef5fc" '
                          'stroke="#265782" stroke-width="2.5"/>')
        self.pen.ellipse((x - 29, y - 29, x + 29, y + 29), fill='#eef5fc', outline='#265782', width=3)
        if marked:
            self.parts.append(f'<circle cx="{x}" cy="{y}" r="8" fill="#172536"/>')
            self.pen.ellipse((x - 8, y - 8, x + 8, y + 8), fill='#172536')
        self.text(x + label_dx, y + 58 + label_dy, name, 21)
        self.text(x + label_dx, y + 83 + label_dy, label, 18)

    def transition(self, x, y, name, label, label_dx=0):
        self.parts.append(f'<rect x="{x - 11}" y="{y - 29}" width="22" height="58" '
                          'fill="#265782"/>')
        self.pen.rectangle((x - 11, y - 29, x + 11, y + 29), fill='#265782')
        self.text(x + label_dx, y - 47, name, 21)
        self.text(x + label_dx, y + 58, label, 18)

    def save(self, name):
        defs = ('<defs><marker id="arrow" markerWidth="10" markerHeight="10" '
                'refX="9" refY="3" orient="auto" markerUnits="strokeWidth">'
                '<path d="M0,0 L0,6 L9,3 z" fill="#536477"/></marker></defs>')
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" '
               f'height="{self.height}" viewBox="0 0 {self.width} {self.height}">'
               '<rect width="100%" height="100%" fill="white"/>' + defs + ''.join(self.parts) + '</svg>')
        (ROOT / f'{name}.svg').write_text(svg, encoding='utf-8')
        self.image.save(ROOT / f'{name}.png')


def verify(net):
    initial = frozenset(net['initial'])
    pending = deque([(initial, ())])
    visited = set()
    markings = set()
    terminals = set()
    reverse = {}
    final = frozenset(['done'])
    while pending:
        marking, trace = pending.popleft()
        if (marking, trace) in visited:
            continue
        visited.add((marking, trace))
        markings.add(marking)
        enabled = []
        for transition in net['transitions']:
            inputs = set(transition['inputs'])
            outputs = set(transition['outputs'])
            if inputs <= marking:
                enabled.append(transition)
                remaining = marking - inputs
                if remaining & outputs:
                    raise AssertionError(f"Unsafe place at {transition['id']}")
                successor = frozenset(remaining | outputs)
                reverse.setdefault(successor, set()).add(marking)
                next_trace = trace
                if 'print' in transition:
                    next_trace += (transition['print'],)
                pending.append((successor, next_trace))
        if not enabled:
            assert marking == final, f'Unexpected deadlock: {marking}'
            terminals.add(trace)
    expected = {(0, 1, 2), (0, 2, 1)} if net['mode'] == 'unordered' else {(0, 1, 2)}
    assert terminals == expected, terminals
    can_finish = {final}
    pending = deque([final])
    while pending:
        for predecessor in reverse.get(pending.popleft(), set()):
            if predecessor not in can_finish:
                can_finish.add(predecessor)
                pending.append(predecessor)
    assert markings <= can_finish
    return {'reachable_markings': len(markings), 'one_safe': True,
            'unexpected_deadlocks': 0, 'all_markings_can_finish': True,
            'print_sequences': sorted(map(list, terminals))}


def make_net(mode):
    transitions = []

    def add(name, inputs, outputs, printed=None):
        item = {'id': name, 'inputs': inputs.split(), 'outputs': outputs.split()}
        if printed is not None:
            item['print'] = printed
        transitions.append(item)

    add('Send1', 's1', 'm1')
    add('Send2', 's2', 'm2')
    if mode == 'unordered':
        add('Print0', 'start', 'ready', 0)
        add('Recv1', 'ready m1', 'r1')
        add('Print1', 'r1', 'ready f1', 1)
        add('Recv2', 'ready m2', 'r2')
        add('Print2', 'r2', 'ready f2', 2)
        add('End', 'ready f1 f2', 'done')
    else:
        add('Print0', 'start', 'q1', 0)
        add('Recv1', 'q1 m1', 'r1')
        add('Print1', 'r1', 'q2', 1)
        add('Recv2', 'q2 m2', 'r2')
        add('Print2', 'r2', 'done', 2)
    return {'mode': mode, 'processes': 3, 'rounds': 1, 'benchmark': False,
            'initial': ['start', 's1', 's2'], 'transitions': transitions}


def unordered():
    d = Drawing(1760, 1030)
    d.text(880, 43, 'Неупорядоченный приём: MPI_ANY_SOURCE', 32)
    d.text(880, 77, '3 процесса · 1 раунд · обычный режим · начальная маркировка', 21)
    arcs = [
        [(209, 150), (439, 150)], [(461, 150), (701, 150)], [(730, 179), (730, 301)],
        [(209, 820), (439, 820)], [(461, 820), (701, 820)], [(730, 791), (730, 659)],
        [(169, 480), (299, 480)], [(321, 480), (471, 480)],
        [(529, 480), (610, 480), (610, 330), (719, 330)],
        [(529, 480), (610, 480), (610, 630), (719, 630)],
        [(741, 330), (871, 330)], [(929, 330), (1059, 330)], [(1081, 330), (1221, 330)],
        [(1081, 330), (1120, 330), (1120, 430), (500, 430), (500, 451)],
        [(741, 630), (871, 630)], [(929, 630), (1059, 630)], [(1081, 630), (1221, 630)],
        [(1081, 630), (1120, 630), (1120, 560), (500, 560), (500, 509)],
        [(529, 480), (1449, 480)],
        [(1279, 330), (1460, 330), (1460, 451)],
        [(1279, 630), (1460, 630), (1460, 509)],
        [(1471, 480), (1601, 480)],
    ]
    for arc in arcs:
        d.line(arc)
    d.place(180, 150, 's1', 'Процесс 1 готов', True)
    d.transition(450, 150, 'Send1', 'Сообщение от 1 доступно')
    d.place(730, 150, 'm1', 'Сообщение от 1', label_dx=120)
    d.place(180, 820, 's2', 'Процесс 2 готов', True)
    d.transition(450, 820, 'Send2', 'Сообщение от 2 доступно')
    d.place(730, 820, 'm2', 'Сообщение от 2')
    d.place(140, 480, 'start', 'Процесс 0 готов', True)
    d.transition(310, 480, 'Print0', 'Печать 0')
    d.place(500, 480, 'ready', 'Можно принять', label_dy=-170)
    for y, rank in [(330, 1), (630, 2)]:
        d.transition(730, y, f'Recv{rank}', f'Приём от {rank}')
        d.place(900, y, f'r{rank}', f'Принят ранг {rank}')
        d.transition(1070, y, f'Print{rank}', f'Печать {rank}')
        d.place(1250, y, f'f{rank}', f'Ранг {rank} напечатан')
    d.transition(1460, 480, 'End', 'Конец', label_dx=95)
    d.place(1630, 480, 'done', 'Готово')
    d.text(1170, 462, 'End требует ready, f1 и f2', 18)
    d.text(880, 948, 'Кружок — позиция; прямоугольник — переход; чёрная точка — начальный маркер.', 21)
    d.text(880, 984, 'm1 и m2 раздельны: личность отправителя не теряется. Все дуги имеют вес 1.', 21)
    d.save('unordered')


def ordered():
    d = Drawing(1880, 650)
    d.text(940, 43, 'Упорядоченный приём: source = 1, затем source = 2', 30)
    d.text(940, 77, '3 процесса · 1 раунд · обычный режим · начальная маркировка', 21)
    points = [140, 300, 460, 620, 780, 940, 1100, 1260, 1420, 1580, 1740]
    for i, (left, right) in enumerate(zip(points, points[1:])):
        d.line([(left + (29 if i % 2 == 0 else 11), 410),
                (right - (11 if i % 2 == 0 else 29), 410)])
    for source, send, mailbox in [(140, 300, 620), (940, 1100, 1260)]:
        d.line([(source + 29, 170), (send - 11, 170)])
        d.line([(send + 11, 170), (mailbox - 29, 170)])
        d.line([(mailbox, 199), (mailbox, 381)])
    for rank, source, send, mailbox in [(1, 140, 300, 620), (2, 940, 1100, 1260)]:
        d.place(source, 170, f's{rank}', f'Процесс {rank} готов', True)
        d.transition(send, 170, f'Send{rank}', f'Сообщение {rank} доступно')
        d.place(mailbox, 170, f'm{rank}', f'Сообщение от {rank}', label_dx=120)
    for x, name, label, marked in [
        (140, 'start', 'Процесс 0 готов', True), (460, 'q1', 'Ждём ранг 1', False),
        (780, 'r1', 'Принят ранг 1', False), (1100, 'q2', 'Ждём ранг 2', False),
        (1420, 'r2', 'Принят ранг 2', False), (1740, 'done', 'Готово', False),
    ]:
        d.place(x, 410, name, label, marked)
    for x, name, label in [(300, 'Print0', 'Печать 0'), (620, 'Recv1', 'Приём от 1'),
                           (940, 'Print1', 'Печать 1'), (1260, 'Recv2', 'Приём от 2'),
                           (1580, 'Print2', 'Печать 2')]:
        d.transition(x, 410, name, label)
    d.text(940, 573, 'Сообщение от 2 может быть доступно раньше, но Recv2 ждёт маркер в q2.', 22)
    d.text(940, 615, 'Все дуги имеют вес 1. Начальные маркеры: start, s1, s2.', 21)
    d.save('ordered')


if __name__ == '__main__':
    report = {}
    for mode in ['unordered', 'ordered']:
        net = make_net(mode)
        report[mode] = verify(net)
        (ROOT / f'{mode}.json').write_text(json.dumps(net, indent=2) + '\n', encoding='utf-8')
    unordered()
    ordered()
    (ROOT / 'verification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
