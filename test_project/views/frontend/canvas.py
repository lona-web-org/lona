from lona.html import Canvas, HTML, H1, P
from lona import LonaView


class CanvasView(LonaView):
    def handle_request(self, request):
        canvas = Canvas(width='300px', height='300px')

        canvas.ctx.lineWidth = 10
        canvas.ctx.strokeRect(75, 140, 150, 110)
        canvas.ctx.fillRect(130, 190, 40, 60)
        canvas.ctx.moveTo(50, 140)
        canvas.ctx.lineTo(150, 60)
        canvas.ctx.lineTo(250, 140)
        canvas.ctx.closePath()
        canvas.ctx.stroke()

        return HTML(
            H1('Canvas'),
            P('This should show a house'),
            canvas,
        )
