import random

from selenium_trio.extras.javascript.js_scripts import (
    CLEAR_CANVAS_JS, PAGE_HEIGHT_JS, ADD_FRAGMENT_JS,
    DRAW_LINE_JS, DRAW_TEXT_JS, DRAW_RECT_JS, DRAW_MULTIPLE_RECTS_JS
)


COLOURS = ['blue', 'green', 'red', 'yellow', 'teal', 'lime', 'purple']
COLOURS_ALL = [
    'red', 'blue', 'green', 'teal', 'black', 'purple', 'orange', 'yellow', 'brown', 'olive', 'lime',
    'coral', 'DarkSeaGreen', 'DarkSlateBlue', 'Tomato', 'YellowGreen', 'SeaGreen', 'violet', 'DodgerBlue'
]


class DrawingMixin(object):

    async def draw(self, type, obj, colour, solid=False):

        if not self.canvas_added:
            await self.add_canvas()

        if colour == 'random':
            colour = COLOURS[random.randint(0, len(COLOURS) - 1)]

        if type == 'rect':
            return await self.draw_rect(obj, colour)
        elif type == 'line':
            x1, y1, x2, y2 = obj
            js_str = DRAW_LINE_JS % (colour, x1, y1, x2, y2)
        elif type == 'text':
            text, x, y = obj
            js_str = DRAW_TEXT_JS % (10, colour, text, x, y)
        elif type == 'multiple_rects':
            js_list = str([
                (rect['x'], rect['y'], rect['width'], rect['height'])
                for rect in obj
            ])
            # js_list = str([list(b) for b in obj])  # obj should be: [(x, y, width, height), ]
            js_str = DRAW_MULTIPLE_RECTS_JS % (js_list, colour)
            if solid:
                js_str = js_str.replace('ctx.rect(', 'ctx.fillRect(')
        else:
            print('invalid draw type: '+type); return
        await self.execute_script2(js_str)

    async def draw_rect(self, rect, colour, solid=False, dashed=False):
        if not self.canvas_added:
            await self.add_canvas()
        if colour == 'random':
            colour = COLOURS[random.randint(0, len(COLOURS) - 1)]
        rect = rect.copy()
        rect['colour'] = colour
        js_str = DRAW_RECT_JS % rect
        if dashed:
            js_str = js_str.replace('ctx.beginPath();', 'ctx.beginPath();\nctx.setLineDash([8]);')
        if solid:
            js_str = js_str.replace('ctx.rect(', 'ctx.fillRect(')
            js_str = js_str.replace('ctx.strokeStyle', 'ctx.fillStyle')
        await self.execute_script2(js_str)

    async def add_html_fragment(self, fragment, insert_before='document.body.childNodes[0]'):
        fragment = fragment.strip().replace('\n', '\\n')
        js = ADD_FRAGMENT_JS % (fragment, insert_before)
        await self.execute_script2(js)

    async def add_canvas(self):
        if self.canvas_added:
            return

        async def get_page_height():
            val = await self.execute_script2(PAGE_HEIGHT_JS)
            return int(round(val))

        page_height = await get_page_height()
        w_size = await self.get_window_size2()

        window_height = w_size['height']
        window_width = w_size['width']

        page_height = int((window_height + page_height) / 2)  # for some reason the full height results in the canvas not showing, so let's pick half-way

        await self.add_html_fragment(
            '<canvas id="myCanvas" width="%s" height="%s" style="z-index: 900; position: '
            'absolute; top: 0px; left: 0px;"></canvas>' % (window_width, page_height)
        )
        self.canvas_added = True

    async def clear_canvas(self):  # todo: doesn't work, maybe we should just remove it?
        await self.execute_script2(CLEAR_CANVAS_JS)


async def draw_clusters_on_driver(driver, clusters, reverse_colours=False, dashed=False, rect_offset=None):
    clusters.sort(key=lambda c: c.length, reverse=True)

    colours = list(COLOURS_ALL)
    num_colours = len(colours)
    if reverse_colours:
        colours.reverse()

    for i, cluster in enumerate(clusters):

        for ld in cluster.lds:
            rect = ld['rect'].copy()

            if rect_offset:
                rect['x'] += rect_offset['x']
                rect['y'] += rect_offset['y']

            if random.randint(0, 1) == 1:
                # helps see when two elements have accidentally be added to the same cluster
                rect['x'] += 2
                rect['y'] += 2

            await driver.draw_rect(rect, colours[i % num_colours], dashed=dashed)

        #driver.draw('multiple_rects', rects, colours[i%num_colours])

    await _draw_cluster_summary(driver, clusters)


async def _draw_cluster_summary(driver, clusters):

    for i, cluster in enumerate(clusters):

        colour = COLOURS_ALL[i%len(COLOURS_ALL)]
        cluster_title = 'cluster %s (%s) :' % (i, cluster.length)

        top, left = (i * 30) + 110, 20
        rect = {'x': 20, 'y': (i * 30) + 110, 'width': 100, 'height': 20}

        await driver.draw_rect(rect, 'white', solid=True)
        await driver.draw('text', (cluster_title, left, top+10), colour)

        def _get_coord(ld, key):  # hacky
            return ld.get(key, ld['rect'][key])

        top_left_elem = sorted(sorted(cluster.lds, key=lambda ld: _get_coord(ld, 'y')), key=lambda ld: _get_coord(ld, 'y'))[0]

        text = 'cluster %s' % i

        x = _get_coord(top_left_elem, 'x')
        y = _get_coord(top_left_elem, 'y')

        await driver.draw('text', (text, x-7, y-15), colour)
